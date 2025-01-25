from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from fastapi import WebSocket
from loguru import logger


class AbstractSender(ABC):
    """
    An abstract base class for WebSocket message senders.

    This class provides a framework for sending structured JSON messages to connected WebSocket clients.
    Subclasses must implement the `event_name` and `create_message_data` methods.

    Attributes:
        _connections (list[WebSocket]): A private list storing active WebSocket connections.
    """

    def __init__(self):
        """
        Initializes the sender with an empty list of WebSocket connections.
        """
        self._connections: list[WebSocket] = []

    @property
    @abstractmethod
    def event_name(self) -> str:
        """
        Abstract property to define the event name.

        Subclasses must override this property to specify the name of the event
        that will be included in the message payload.

        Returns:
            str: The event name.
        """
        raise NotImplementedError("Must specify 'event_name' in inherited Sender")

    async def send(self) -> None:
        """
        Sends a JSON message to all connected WebSocket clients.

        The message contains the event name, data provided by `create_message_data`,
        and a timestamp.

        Raises:
            Exception: If sending fails for any connection.
        """
        timestamp = datetime.now().isoformat()

        message = {
            "event": self.event_name,
            "data": self.create_message_data(),
            "timestamp": timestamp
        }

        for connection in self._connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")

    @abstractmethod
    def create_message_data(self) -> dict[str, Any]:
        """
        Abstract method to create message data.

        Subclasses must implement this method to generate the content of the message.

        Returns:
            dict[str, [str, dict]]: The message payload structure.
        """
        raise NotImplementedError()

    def add_connection(self, websocket: WebSocket) -> None:
        """
        Adds a WebSocket connection to the sender.

        Args:
            websocket (WebSocket): The WebSocket connection to be added.
        """
        if websocket not in self._connections:
            self._connections.append(websocket)

    def remove_connection(self, websocket: WebSocket) -> None:
        """
        Removes a WebSocket connection from the sender.

        Args:
            websocket (WebSocket): The WebSocket connection to be removed.

        Raises:
            ValueError: If the WebSocket connection is not found in the list.
        """
        if websocket in self._connections:
            self._connections.remove(websocket)
