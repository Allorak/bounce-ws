from typing import Any

from bounce_ws.senders import AbstractSender

class PingSender(AbstractSender):
    def __init__(self):
        super().__init__()

    @property
    def event_name(self) -> str:
        return "ping"

    def create_message_data(self) -> dict[str, Any]:
        return {
            "ping": "ping"
        }
