from abc import ABC, abstractmethod

from knowledge.models import KnowledgeItem


class KnowledgeRepository(ABC):
    """Storage interface. Knows nothing about validation or the CLI."""

    @abstractmethod
    def add(self, title: str, content: str) -> KnowledgeItem: ...

    @abstractmethod
    def get(self, item_id: int) -> KnowledgeItem | None: ...

    @abstractmethod
    def list_all(self) -> list[KnowledgeItem]: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...

    @abstractmethod
    def update(
        self, item_id: int, title: str, content: str
    ) -> KnowledgeItem | None: ...
