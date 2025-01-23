import asyncio
import json
from contextlib import asynccontextmanager
from threading import Thread
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
import uvicorn

from .senders import AbstractTimedSender, SenderOrchestrator
from .handlers import HandlerOrchestrator


class WebApi:
    """
    A class to manage a WebSocket API server using FastAPI and Uvicorn.

    This class handles starting and stopping the server, managing WebSocket connections,
    and orchestrating sender and handler operations.

    Attributes:
        _app (FastAPI): The FastAPI application instance.
        _host (str): The host address for the server.
        _port (int): The port number for the server.
        _name (str): A name identifier for logging purposes.
        __sender_orchestrator (SenderOrchestrator): Manages sender instances.
        __handler_orchestrator (HandlerOrchestrator): Handles incoming WebSocket messages.
    """

    def __init__(self, app: FastAPI, sender_orchestrator: SenderOrchestrator, handler_orchestrator: HandlerOrchestrator,
                 host: str = "localhost", port: int = 8080, name: str = 'Websocket API', route: str = '/ws') -> None:
        """
        Initializes the WebApi instance with the given FastAPI app and orchestrators.

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


    def start(self) -> None:
        """
        Starts the WebSocket server using Uvicorn in a separate thread.
        """
        config = uvicorn.Config(self._app, host=self._host, port=self._port)
        self.__server = uvicorn.Server(config)

        self.__thread = Thread(target=self.__server.run, daemon=True)
        self.__thread.start()

        try:
            self.__thread.join()
        except KeyboardInterrupt:
            self.stop()

        logger.info(f'{self._name} server started at {self._host}:{self._port}/{self._route}')


    def stop(self) -> None:
        """
        Stops the running WebSocket server gracefully.
        """
        if self.__server is None:
            return

        self.__server.should_exit = True
        self.__thread.join()
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

        self.__sender_orchestrator.add_connection(websocket)

        try:
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    continue

                await self.__handler_orchestrator.handle_message(message)
        except WebSocketDisconnect as _:
            self.__sender_orchestrator.remove_connection(websocket)


    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> None:
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
        tasks = [asyncio.create_task(sender.start()) for sender in self.__sender_orchestrator.senders
                                                     if isinstance(sender, AbstractTimedSender)]

        yield

        # Shutdown phase, executes when the application is shutting down
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

