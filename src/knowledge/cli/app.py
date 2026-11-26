# cli/app.py
import os
import sys
import traceback
from pathlib import Path

from knowledge.cli.parser import build_parser
from knowledge.errors import KnowledgeError
from knowledge.service import KnowledgeService
from knowledge.storage.sqlite import SqliteKnowledgeRepository

DEFAULT_DB_PATH = Path.home() / ".knowledge" / "knowledge.db"


def resolve_db_path(cli_value: str | None) -> Path:
    raw = cli_value or os.environ.get("KNOWLEDGE_DB")
    return Path(raw).expanduser() if raw else DEFAULT_DB_PATH


def run(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    with SqliteKnowledgeRepository(resolve_db_path(args.db)) as repository:
        args.handler(args, KnowledgeService(repository))
    return 0


def main() -> int:
    return run(sys.argv[1:])