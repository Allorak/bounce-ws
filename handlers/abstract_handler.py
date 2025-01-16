from abc import ABC, abstractmethod

class AbstractHandler(ABC):
    @property
    @abstractmethod
    def event_name(self) -> str:
        raise NotImplementedError("Must specify 'event_name' in inherited Handler")

    @abstractmethod
    def handle(self, data: dict) -> None:
        raise NotImplementedError("Must define 'handle' behaviour in inherited Handler")
