from typing import Any

from loguru import logger

from bounce_ws.handlers import AbstractHandler
from bounce_ws.senders import AbstractSender

class PingHandler(AbstractHandler):
    def __init__(self, callback_sender: AbstractSender):
        super().__init__(callback_sender)

    @property
    def event_name(self) -> str:
        return "ping"

    def process_data(self, data: dict[str, Any]) -> None:
        logger.info("Received ping message")
