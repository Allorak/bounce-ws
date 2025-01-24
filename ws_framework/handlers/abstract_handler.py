from abc import ABC, abstractmethod
from typing import Any, Optional

from ws_framework.senders import AbstractSender


class AbstractHandler(ABC):
    """
    An abstract base class for WebSocket event handlers.

    This class provides a structure for handling incoming WebSocket messages
    and processing them via the provided sender callback.

    Attributes:
        _callback_sender (AbstractSender): The sender instance used to send responses or
                                          follow-up messages after handling an event.
    """
    def __init__(self, callback_sender: Optional[AbstractSender]):
        """
        Initializes the handler with a callback sender.

        Args:
            callback_sender (AbstractSender): An instance of AbstractSender used to send
                                              messages after handling the event. Can be None.
        """
        self._callback_sender: AbstractSender = callback_sender

    @property
    @abstractmethod
    def event_name(self) -> str:
        """
        Abstract property to define the event name that this handler processes.

        Subclasses must override this property to specify the name of the event
        they are responsible for handling.

        Returns:
            str: The event name associated with this handler.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Must specify 'event_name' in inherited Handler")

    @abstractmethod
    async def handle(self, data: dict[str, Any]) -> None:
        """
        Method to handle incoming event data.

        Calls abstract 'process_data' that must be implemented in inherited class

        Args:
            data (dict): The event data received from the WebSocket connection.
        """

        self.process_data(data)

        if self._callback_sender is not None:
            await self._callback_sender.send()

    @abstractmethod
    def process_data(self, data: dict[str, Any]) -> None:
        """
        Abstract method to process incoming event data

        Subclasses must implement this method to process the incoming data and
        perform necessary actions.

        Args:
            data (dict): The event data received from the WebSocket connection.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Must define 'process_data' behaviour in inherited Handler")
