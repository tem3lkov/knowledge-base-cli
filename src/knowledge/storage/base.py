# storage/base.py
from abc import ABC, abstractmethod

from knowledge.models import KnowledgeItem


class KnowledgeRepository(ABC):

    @abstractmethod
    def add(self, title: str, content: str) -> KnowledgeItem: 
        ...

    @abstractmethod
    def get(self, item_id: int) -> KnowledgeItem | None: 
        ...

    @abstractmethod
    def list_all(self) -> list[KnowledgeItem]:
        ...

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        ...