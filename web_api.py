import asyncio
import json
from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
import uvicorn

from senders import SenderOrchestrator
from handlers import HandlerOrchestrator


class WebApi:
    __thread: Thread
    __server: uvicorn.Server
    def __init__(self, app: FastAPI, sender_orchestrator: SenderOrchestrator, handler_orchestrator: HandlerOrchestrator,
                 host: str = "localhost", port: int = 8080, name: str = 'Websocket API', route: str = '/ws') -> None:
        self._app: FastAPI = app
        self._app.router.lifespan_context = self.lifespan
        self._app.add_websocket_route(route, self.process)

        self._host: str = host
        self._port: int = port
        self._name: str = name

        self.__connections: list[WebSocket] = []
        self.__sender_orchestrator: SenderOrchestrator = sender_orchestrator
        self.__handler_orchestrator: HandlerOrchestrator = handler_orchestrator


    def start(self) -> None:
        config = uvicorn.Config(self._app, host=self._host, port=self._port)
        self.__server = uvicorn.Server(config)

        self.__thread = Thread(target=self.__server.run, daemon=True)
        self.__thread.start()
        logger.info(f'{self._name} server started')


    def stop(self) -> None:
        if self.__server is None:
            return

        self.__server.should_exit = True
        self.__thread.join()
        logger.info(f'{self._name} server stopped')


    async def process(self, websocket: WebSocket) -> None:
        await websocket.accept()

        self.__connections.append(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                self.__handler_orchestrator.handle_message(message)
        except WebSocketDisconnect as _:
            self.__connections.remove(websocket)


    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> None:
        # Startup phase, executes before serving messages
        tasks = [asyncio.create_task(sender.start()) for sender in self.__sender_orchestrator.senders]

        yield

        # Shutdown phase, executes when the application is shutting down
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

