import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from knowledge.errors import StorageError
from knowledge.models import KnowledgeItem
from knowledge.storage.base import KnowledgeRepository

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
)
"""


class SqliteKnowledgeRepository(KnowledgeRepository):
    def __init__(self, db_path: Path) -> None:
        error_message = (
            f"Cannot open knowledge base at '{db_path}'. "
            "The file may be corrupted or not a database."
        )

        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(db_path)
        except (sqlite3.Error, OSError) as err:
            raise StorageError(error_message) from err

        try:
            self._conn.row_factory = sqlite3.Row
            with self._conn:
                self._conn.execute(CREATE_TABLE)
        except sqlite3.Error as err:
            self._conn.close()
            raise StorageError(error_message) from err

    def __enter__(self) -> "SqliteKnowledgeRepository":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._conn.close()

    def add(self, title: str, content: str) -> KnowledgeItem:
        now = datetime.now(UTC)
        timestamp = now.isoformat()
        try:
            with self._conn:
                cursor = self._conn.execute(
                    "INSERT INTO items (title, content, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?)",
                    (title, content, timestamp, timestamp),
                )
        except sqlite3.Error as err:
            raise StorageError("Could not save the item.") from err

        if cursor.lastrowid is None:
            raise StorageError("Could not retrieve the ID of the saved item.")

        return KnowledgeItem(
            id=cursor.lastrowid,
            title=title,
            content=content,
            created_at=now,
            updated_at=now,
        )

    def get(self, item_id: int) -> KnowledgeItem | None:
        rows = self._read("SELECT * FROM items WHERE id = ?", (item_id,))
        return self._to_item(rows[0]) if rows else None

    def list_all(self) -> list[KnowledgeItem]:
        rows = self._read("SELECT * FROM items ORDER BY id")
        return [self._to_item(row) for row in rows]

    def delete(self, item_id: int) -> bool:
        try:
            with self._conn:
                cursor = self._conn.execute(
                    "DELETE FROM items WHERE id = ?",
                    (item_id,),
                )
        except sqlite3.Error as err:
            raise StorageError(f"Could not delete item {item_id}.") from err
        return cursor.rowcount > 0

    def update(self, item_id: int, title: str, content: str) -> KnowledgeItem | None:
        now = datetime.now(UTC).isoformat()
        try:
            with self._conn:
                cursor = self._conn.execute(
                    "UPDATE items SET title = ?, content = ?, updated_at = ? WHERE id = ?",
                    (title, content, now, item_id),
                )
        except sqlite3.Error as err:
            raise StorageError("Could not update the item.") from err
        return self.get(item_id) if cursor.rowcount else None

    def _read(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        try:
            return self._conn.execute(sql, params).fetchall()
        except sqlite3.Error as err:
            raise StorageError(
                "Could not read the knowledge base. The file may be corrupted."
            ) from err

    @staticmethod
    def _to_item(row: sqlite3.Row) -> KnowledgeItem:
        try:
            return KnowledgeItem(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        except (IndexError, TypeError, ValueError) as err:
            raise StorageError("The knowledge base contains invalid data.") from err
