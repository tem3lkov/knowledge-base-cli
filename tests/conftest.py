import pytest

from knowledge.service import KnowledgeService
from knowledge.storage.sqlite import SqliteKnowledgeRepository


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def service(db_path):
    with SqliteKnowledgeRepository(db_path) as repository:
        yield KnowledgeService(repository)
