from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

from fastapi import WebSocket


class AbstractSender(ABC):
    def __init__(self, framerate: float = 10):
        self._delay: float = 1 / framerate
        self.__connections: list[WebSocket] = []

    @property
    @abstractmethod
    def event_name(self) -> str:
        raise NotImplementedError("Must specify 'event_name' in inherited Sender")

    async def start(self) -> None:
        while True:
            await self.send()
            await asyncio.sleep(self._delay)

    async def send(self) -> None:
        for connection in self.__connections:
            message = {
                "event": self.event_name,
                "data": self.create_message_data(),
                "timestamp": datetime.now().isoformat()
            }

            await connection.send_json(message)

    @abstractmethod
    def create_message_data(self) -> dict[str, [str, dict]]:
        raise NotImplementedError()

    async def add_connection(self, websocket: WebSocket) -> None:
        self.__connections.append(websocket)

    async def remove_connection(self, websocket: WebSocket) -> None:
        self.__connections.remove(websocket)

    