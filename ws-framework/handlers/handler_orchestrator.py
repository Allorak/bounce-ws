import datetime
from typing import Optional, Any

from loguru import logger

from src.handlers import AbstractHandler


class HandlerOrchestrator:
    """
    Manages the registration, unregistration, and message handling for WebSocket event handlers.

    This class acts as a central registry for event handlers and ensures that messages
    are routed to the appropriate handlers based on the event name.

    Attributes:
        _handlers_dict (dict[str, AbstractHandler]): A dictionary storing handlers mapped by event names.
    """

    def __init__(self):
        """
        Initializes the orchestrator with an empty handler registry.
        """
        self._handlers_dict: dict[str, AbstractHandler] = dict()
        self._last_event_timestamp: dict[str, datetime.datetime] = dict()

    @property
    def registered_events(self) -> list[str]:
        """
        Retrieves a list of currently registered event names.

        Returns:
            list[str]: A list of event names that have associated handlers.
        """
        return list(self._handlers_dict.keys())

    @property
    def handlers(self) -> list[AbstractHandler]:
        """
        Retrieves a list of currently registered handler instances.

        Returns:
            list[AbstractHandler]: A list of registered handler objects.
        """
        return list(self._handlers_dict.values())

    def get_handler(self, event_name: str) -> Optional[AbstractHandler]:
        """
        Retrieves a handler by event name.

        Args:
            event_name (str): The name of the event.

        Returns:
            Optional[AbstractHandler]: The handler instance if found, else None.
        """
        return self._handlers_dict.get(event_name)

    def register_handler(self, handler: AbstractHandler) -> None:
        """
        Registers a handler instance for a specific event.

        If a handler for the event already exists, an error is logged and registration is ignored.

        Args:
            handler (AbstractHandler): The handler instance to be registered.

        Logs:
            - Error if the handler for the given event is already registered.
        """
        if handler.event_name in self._handlers_dict:
            logger.error(f"Handler for event {handler.event_name} is already registered, ignoring...")
            return

        self._handlers_dict[handler.event_name] = handler
        self._last_event_timestamp[handler.event_name] = datetime.datetime.now()

    def unregister_handler(self, handler: AbstractHandler) -> None:
        """
        Unregisters a handler instance based on its event name.

        If the handler does not exist or the provided instance does not match the registered one,
        an error is logged and the operation is ignored.

        Args:
            handler (AbstractHandler): The handler instance to be unregistered.

        Logs:
            - Error if no handler is found for the given event.
            - Error if the provided handler does not match the registered handler.
        """
        if handler.event_name not in self._handlers_dict:
            logger.error(f"No handler found for event {handler.event_name}, can't unregister")
            return

        if self._handlers_dict[handler.event_name] != handler:
            logger.error(f"Handler instance for event {handler.event_name} does not match, can't unregister")
            return

        del self._handlers_dict[handler.event_name]
        del self._last_event_timestamp[handler.event_name]

    async def handle_message(self, message: dict[str, Any]) -> None:
        """
        Processes an incoming message and routes it to the appropriate handler.

        The message must contain an 'event' key that corresponds to a registered handler.
        If no event is specified or no matching handler is found, appropriate warnings are logged.

        Args:
            message (dict): The message to be processed, expected to contain 'event', 'data' and 'timestamp' keys.

        Logs:
            - Info if the message does not contain an 'event' key.
            - Warning if no handler is registered for the specified event.
        """
        event_name = message.get("event")

        if event_name is None:
            logger.info("Received message without 'event' specified")
            return

        timestamp_iso = message.get("timestamp")

        if timestamp_iso is None:
            logger.info("Received message without 'timestamp' specified")
            return

        event_time = datetime.datetime.fromisoformat(timestamp_iso)

        if event_time < self._last_event_timestamp[event_name]:
            logger.info("Ignoring not synchronised event received")
            return

        handler = self._handlers_dict.get(event_name)

        if handler is None:
            logger.warning(f"Received event for {event_name} without corresponding handler registered")
            return

        data = message.get('data', dict())
        await handler.handle(data)

    def refresh(self):
        for event in self._last_event_timestamp.keys():
            self._last_event_timestamp[event] = datetime.datetime.now()
