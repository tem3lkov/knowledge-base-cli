class KnowledgeError(Exception):
    """Base class for every error the user should see as a clean message."""
    exit_code = 1


class ValidationError(KnowledgeError):
    """Input breaks a rule, e.g. an empty title."""
    exit_code = 2


class ItemNotFoundError(KnowledgeError):
    exit_code = 3

    def __init__(self, item_id: int) -> None:
        super().__init__(f"No item with ID {item_id}. Use 'knowledge list' to see all IDs.")


class StorageError(KnowledgeError):
    """The database cannot be opened, read or written."""
    exit_code = 4