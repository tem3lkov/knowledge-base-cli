from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class KnowledgeItem:
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
