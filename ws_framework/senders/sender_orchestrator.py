from typing import Optional, Any

from loguru import logger
from fastapi import WebSocket

from ws_framework.senders import AbstractSender

class SenderOrchestrator:
    """
    Manages registration and unregistration of WebSocket senders.

    This class acts as a central registry for `AbstractSender` instances,
    allowing registration, unregistration, and retrieval of event-based senders.

    Attributes:
        _senders_dict (dict[str, AbstractSender]): A dictionary storing senders mapped by event names.
    """

    def __init__(self):
        """
        Initializes the orchestrator with an empty sender registry.
        """
        self._senders_dict: dict[str, AbstractSender] = {}

    @property
    def registered_events(self) -> list[str]:
        """
        Retrieves the list of registered event names.

        Returns:
            list[str]: A list of event names currently registered.
        """
        return list(self._senders_dict.keys())

    @property
    def senders(self) -> list[AbstractSender]:
        """
        Retrieves the list of registered sender instances.

        Returns:
            list[AbstractSender]: A list of registered sender objects.
        """
        return list(self._senders_dict.values())

    def get_sender(self, event_name: str) -> Optional[AbstractSender]:
        """
        Retrieves a sender by event name.

        Args:
            event_name (str): The name of the event.

        Returns:
            Optional[AbstractSender]: The sender instance if found, else None.
        """
        return self._senders_dict.get(event_name)


    def register_sender(self, sender: AbstractSender) -> None:
        """
        Registers a sender instance for its associated event name.

        If a sender for the event already exists, the registration is ignored, and
        an error message is logged.

        Args:
            sender (AbstractSender): The sender instance to be registered.

        Logs:
            - Error if sender for the event is already registered.
        """
        if sender.event_name in self._senders_dict:
            logger.error(f"Sender for event {sender.event_name} is already registered, ignoring...")
            return

        self._senders_dict[sender.event_name] = sender


    def unregister_sender(self, sender: AbstractSender) -> None:
        """
        Unregisters a sender instance based on its event name.

        If the event name is not found, or if the sender instance does not match the registered one,
        an error message is logged.

        Args:
            sender (AbstractSender): The sender instance to be unregistered.

        Logs:
            - Error if no sender is found for the given event.
            - Error if the registered sender instance does not match.
        """
        if sender.event_name not in self._senders_dict:
            logger.error(f"No sender found for event {sender.event_name}, can't unregister")
            return

        if self._senders_dict[sender.event_name] != sender:
            logger.error(f"Sender instance for event {sender.event_name} does not match, can't unregister")
            return

        del self._senders_dict[sender.event_name]

    def subscribe(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        """
        Subscribes websocket to the senders with specified events

        Args:
            websocket: websocket instance to be subscribed
            data: contents of the 'subscribe' event message
        """
        events: list[str] = data.get("events")

        if events is None:
            logger.warning('No events specified in "subscribe" event')
            return

        if "*" in events:
            for sender in self._senders_dict.values():
                if not sender.has_connection(websocket):
                    sender.add_connection(websocket)
            return

        for event in events:
            sender = self._senders_dict[event]

            if not sender.has_connection(websocket):
                sender.add_connection(websocket)

    def unsubscribe(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        """
        Unsubscribes websocket from the senders with specified events

        Args:
            websocket: websocket instance to be unsubscribed
            data: contents of the 'unsubscribe' event message
        """
        events: list[str] = data.get("events")

        if events is None:
            logger.warning('No events specified in "unsubscribe" event')
            return

        if "*" in events:
            for sender in self._senders_dict.values():
                if sender.has_connection(websocket):
                    sender.remove_connection(websocket)
            return

        for event in events:
            sender = self._senders_dict[event]

            if sender.has_connection(websocket):
                sender.remove_connection(websocket)

