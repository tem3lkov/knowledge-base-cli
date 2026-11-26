from knowledge.errors import ItemNotFoundError, ValidationError
from knowledge.models import KnowledgeItem
from knowledge.storage.base import KnowledgeRepository

MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 10_000


class KnowledgeService:
    def __init__(self, repository: KnowledgeRepository) -> None:
        self._repository = repository

    def add(self, title: str, content: str) -> KnowledgeItem:
        title = _require_title(title)
        content = _require_text(content, "Content", MAX_CONTENT_LENGTH)
        return self._repository.add(title, content)

    def get(self, item_id: int) -> KnowledgeItem:
        item = self._repository.get(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item

    def list_all(self) -> list[KnowledgeItem]:
        return self._repository.list_all()

    def search(self, text: str) -> list[KnowledgeItem]:
        query = _require_text(text, "Search text", MAX_TITLE_LENGTH).casefold()
        return [
            item
            for item in self._repository.list_all()
            if query in item.title.casefold() or query in item.content.casefold()
        ]

    def delete(self, item_id: int) -> None:
        if not self._repository.delete(item_id):
            raise ItemNotFoundError(item_id)

    def update(
        self, item_id: int, title: str | None = None, content: str | None = None
    ) -> KnowledgeItem:
        if title is None and content is None:
            raise ValidationError("Nothing to update: give a new title and/or content.")
        current = self.get(item_id)
        new_title = current.title if title is None else _require_title(title)
        new_content = (
            current.content
            if content is None
            else _require_text(content, "Content", MAX_CONTENT_LENGTH)
        )

        updated = self._repository.update(item_id, new_title, new_content)
        if updated is None:
            raise ItemNotFoundError(item_id)
        return updated


def _require_text(value: str, field: str, max_length: int) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field} must not be empty.")
    if len(cleaned) > max_length:
        raise ValidationError(f"{field} must be at most {max_length} characters.")
    try:
        cleaned.encode("utf-8")
    except UnicodeEncodeError:
        raise ValidationError(f"{field} contains invalid characters.") from None

    return cleaned


def _require_title(value: str) -> str:
    title = _require_text(value, "Title", MAX_TITLE_LENGTH)
    if len(title.splitlines()) > 1:
        raise ValidationError("Title must be a single line.")
    return title
