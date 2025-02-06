import asyncio
import datetime
import json
from contextlib import asynccontextmanager
from threading import Thread
from typing import Optional, Any, AsyncGenerator
import traceback
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
import uvicorn

from .senders import AbstractTimedSender, SenderOrchestrator
from .handlers import HandlerOrchestrator


class WebSocketApi:
    """
    Manages a WebSocket API server using FastAPI and Uvicorn.

    This class handles WebSocket connections, message processing, and orchestrates sender
    and handler operations. It provides methods to start and stop the server.
    """

    def __init__(self, app: FastAPI, sender_orchestrator: SenderOrchestrator, handler_orchestrator: HandlerOrchestrator,
                 host: str = "localhost", port: int = 8080, name: str = 'Websocket API', route: str = '/ws') -> None:
        """
        Initializes the WebSocketApi instance with the given FastAPI app and orchestrators.

        Args:
            app (FastAPI): The FastAPI application instance.
            sender_orchestrator (SenderOrchestrator): Orchestrator for message senders.
            handler_orchestrator (HandlerOrchestrator): Orchestrator for message handlers.
            host (str, optional): The host address for the server. Defaults to "localhost".
            port (int, optional): The port number for the server. Defaults to 8080.
            name (str, optional): The server name for logging. Defaults to 'Websocket API'.
            route (str, optional): The WebSocket route to attach. Defaults to '/ws'.
        """
        self._app: FastAPI = app
        self._app.router.lifespan_context = self.lifespan
        self._app.add_websocket_route(route, self.process)

        self._host: str = host
        self._port: int = port
        self._route: str = route
        self._name: str = name

        self.__sender_orchestrator: SenderOrchestrator = sender_orchestrator
        self.__handler_orchestrator: HandlerOrchestrator = handler_orchestrator

        self.__thread: Optional[Thread] = None
        self.__server: Optional[uvicorn.Server] = None


    def start(self, background: bool = False) -> None:
        """
        Starts the WebSocket server using Uvicorn in a separate thread.

        Args:
            background (bool): If False (default), the method blocks execution until the server stops.
                               If True, the server runs in the background, allowing other tasks to proceed.

        Behavior:
            - When `background` is set to False, the method blocks the main thread until
              interrupted (e.g., via Ctrl+C), at which point the server is stopped gracefully.
            - When `background` is set to True, the server runs in a separate daemon thread,
              and control returns to the caller immediately.

        Raises:
            KeyboardInterrupt: If interrupted manually when running in blocking mode.

        Example:
            # Start the server and block execution
            server.start()

            # Start the server in background mode
            server.start(background=True)
        """
        config = uvicorn.Config(self._app, host=self._host, port=self._port)
        self.__server = uvicorn.Server(config)

        self.__thread = Thread(target=self.__server.run, daemon=True)
        self.__thread.start()

        logger.info(f'{self._name} server starting at {self._host}:{self._port}{self._route}')

        if background:
            return
            
        try:
            self.__thread.join()
        except KeyboardInterrupt:
            self.stop()


    def stop(self) -> None:
        """
        Stops the running WebSocket server gracefully.
        """
        if self.__server is None:
            return

        self.__server.should_exit = True
        self.__thread.join(timeout=1)
        logger.info(f'{self._name} server stopped')


    async def process(self, websocket: WebSocket) -> None:
        """
        Handles incoming WebSocket connections and processes messages.

        This method accepts a new connection, listens for incoming messages,
        and routes them to the handler orchestrator.

        Args:
            websocket (WebSocket): The WebSocket connection instance.
        """
        await websocket.accept()

        try:
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    continue

                try:
                    event, data, timestamp = self.get_message_info(message)
                except ValueError:
                    logger.error("Invalid message contents, can't parse")
                    continue

                if event == 'subscribe':
                    self.__sender_orchestrator.subscribe(websocket, data)
                elif event == 'unsubscribe':
                    self.__sender_orchestrator.unsubscribe(websocket, data)
                else:
                    await self.__handler_orchestrator.handle_message(event, data, timestamp)
        except WebSocketDisconnect as _:
            self.__sender_orchestrator.unsubscribe(websocket)

    @staticmethod
    def get_message_info( message: dict[str, Any]) -> (str, dict[str,Any], datetime.datetime):
        """
        Parses incoming WebSocket message and returns event name, contents and timestamp.
        Args:
            message: dictionary with message contents, expected to have 'event', and 'timestamp' keys.

        Raises:
            ValueError: if message doesn't contain 'event', or 'timestamp' key.
        """
        event_name = message.get("event")

        if event_name is None:
            raise ValueError("Received message without 'event' specified")

        timestamp_iso = message.get("timestamp")

        if timestamp_iso is None:
            raise ValueError("Received message without 'timestamp' specified")

        event_time = datetime.datetime.fromisoformat(timestamp_iso)

        data = message.get("data", dict())

        return event_name, data, event_time

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[Any, Any]:
        """
        Manages the startup and shutdown phases of the FastAPI application.

        During startup, it starts all senders that are instances of AbstractTimedSender.
        During shutdown, it cancels ongoing tasks gracefully.

        Args:
            app (FastAPI): The FastAPI application instance.

        Yields:
            None
        """
        # Startup phase, executes before serving messages
        async def safe_start(timed_sender: AbstractTimedSender):
            try:
                await timed_sender.start()
            except Exception as e:
                logger.error(f"Error in sender {timed_sender}: {e}")
                traceback.print_exc(file=sys.stdout)

        tasks = []
        for sender in self.__sender_orchestrator.senders:
            if isinstance(sender, AbstractTimedSender):
                task = asyncio.create_task(safe_start(sender))
                tasks.append(task)

        # Yield is for the working state of the app
        yield
        # Shutdown phase, executes when the application is shutting down

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        for task in done:
            if e := task.exception():
                logger.error(f"Task failed with: {e}")
                traceback.print_exception(type(e), e, task.get_coro().cr_frame)
                raise e

        for task in pending:
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=5)
            except asyncio.CancelledError:
                pass

