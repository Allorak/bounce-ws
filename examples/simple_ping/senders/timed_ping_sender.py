from typing import Any

from bounce.senders import AbstractTimedSender

class TimedPingSender(AbstractTimedSender):
    def __init__(self, framerate: float = 10):
        super().__init__(framerate)

    @property
    def event_name(self) -> str:
        return "ping_timed"

    def create_message_data(self) -> dict[str, Any]:
        return {
            "ping": "ping"
        }
