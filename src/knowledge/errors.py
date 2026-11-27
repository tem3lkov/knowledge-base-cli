class KnowledgeError(Exception):
    """Base class for every error the user should see as a clean message."""


class ValidationError(KnowledgeError):
    """Input breaks a rule, e.g. an empty title."""


class ItemNotFoundError(KnowledgeError):
    """The requested item does not exist."""

    def __init__(self, item_id: int) -> None:
        super().__init__(f"No item with ID {item_id}.")


class StorageError(KnowledgeError):
    """The database cannot be opened, read or written."""
