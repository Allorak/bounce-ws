from loguru import logger

from senders import AbstractSender

class SenderOrchestrator:
    def __init__(self):
        self.__senders_dict: dict[str, AbstractSender] = dict()

    @property
    def registered_events(self) -> list[str]:
        return list(self.__senders_dict.keys())

    @property
    def senders(self) -> list[AbstractSender]:
        return list(self.__senders_dict.values())


    def register_sender(self, sender: AbstractSender) -> None:
        if sender.event_name in self.__senders_dict:
            logger.error(f"Sender for event {sender.event_name} is already registered, ignoring...")
            return

        self.__senders_dict[sender.event_name] = sender


    def unregister_sender(self, sender: AbstractSender) -> None:
        if sender.event_name not in self.__senders_dict:
            logger.error(f"No sender found for event {sender.event_name}, can't unregister")
            return

        if self.__senders_dict[sender.event_name] != sender:
            logger.error(f"Sender instance for event {sender.event_name} does not match, can't unregister")
            return

        del self.__senders_dict[sender.event_name]