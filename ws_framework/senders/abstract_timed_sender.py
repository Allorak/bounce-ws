from abc import ABC
import asyncio

from ws_framework.senders import AbstractSender


class AbstractTimedSender(AbstractSender, ABC):
    """
    An abstract sender that sends WebSocket messages at a fixed interval.

    This class extends `AbstractSender` to provide periodic message sending
    with a configurable frame rate. Subclasses must implement the required
    methods from `AbstractSender`.

    Attributes:
        _delay (float): The delay interval (in seconds) between each message send.
        _is_active (bool): A flag indicating whether the sender is currently active.
    """

    def __init__(self, framerate: float):
        """
        Initializes the timed sender with a given frame rate.

        Args:
            framerate (float): The number of times messages should be sent per second.
        """
        super().__init__()

        if framerate <= 0:
            raise ValueError("Framerate must be greater than zero.")

        self._delay: float = 1 / framerate
        self._is_active: bool = True


    async def start(self) -> None:
        """
        Starts the periodic sending of messages.

        This method continuously sends messages at the specified interval
        until `stop` is called to deactivate the sender.
        """
        self._is_active = True

        while self._is_active:
            await self.send()
            await asyncio.sleep(self._delay)


    def stop(self) -> None:
        """
        Stops the periodic sending of messages.

        Sets the active flag to `False`, stopping the sending loop gracefully.
        """
        self._is_active = False
