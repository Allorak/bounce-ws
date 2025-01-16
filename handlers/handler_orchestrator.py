from loguru import logger

from handlers import AbstractHandler


class HandlerOrchestrator:
    def __init__(self):
        self.__handlers_dict: dict[str, AbstractHandler] = dict()

    @property
    def registered_events(self) -> list[str]:
        return list(self.__handlers_dict.keys())

    @property
    def handlers(self) -> list[AbstractHandler]:
        return list(self.__handlers_dict.values())

    def register_handler(self, handler: AbstractHandler) -> None:
        if handler.event_name in self.__handlers_dict:
            logger.error(f"Handler for event {handler.event_name} is already registered, ignoring...")
            return

        self.__handlers_dict[handler.event_name] = handler

    def unregister_handler(self, handler: AbstractHandler) -> None:
        if handler.event_name not in self.__handlers_dict:
            logger.error(f"No handler found for event {handler.event_name}, can't unregister")
            return

        if self.__handlers_dict[handler.event_name] != handler:
            logger.error(f"Handler instance for event {handler.event_name} does not match, can't unregister")
            return

        del self.__handlers_dict[handler.event_name]

    def handle_message(self, message: dict) -> None:
        event_name = message.get('event')

        if event_name is None:
            logger.info("Received message without 'event' specified")
            return

        handler = self.__handlers_dict.get(event_name)

        if handler is None:
            logger.warning(f"Received event for {event_name} without corresponding handler registered")
            return

        data = message.get('data', dict())
        handler.handle(data)
