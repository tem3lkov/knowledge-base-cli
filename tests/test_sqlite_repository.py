import pytest

from knowledge.errors import StorageError
from knowledge.storage.sqlite import SqliteKnowledgeRepository


def test_items_survive_reopening(db_path):
    with SqliteKnowledgeRepository(db_path) as repo:
        repo.add("Python", "A programming language.")

    with SqliteKnowledgeRepository(db_path) as repo:
        items = repo.list_all()

    assert [item.title for item in items] == ["Python"]


def test_ids_are_not_reused_after_delete(db_path):
    with SqliteKnowledgeRepository(db_path) as repo:
        first = repo.add("A", "a")
        repo.delete(first.id)
        second = repo.add("B", "b")

    assert second.id != first.id


def test_delete_missing_id_returns_false(db_path):
    with SqliteKnowledgeRepository(db_path) as repo:
        assert repo.delete(42) is False


def test_corrupted_file_raises_storage_error(tmp_path):
    bad_file = tmp_path / "bad.db"
    bad_file.write_text("this is not a database")

    with pytest.raises(StorageError):
        SqliteKnowledgeRepository(bad_file)

def test_get_returns_item_or_none(db_path):
    with SqliteKnowledgeRepository(db_path) as repo:
        created = repo.add("Docker", "Container platform.")

        assert repo.get(created.id) == created
        assert repo.get(999) is None