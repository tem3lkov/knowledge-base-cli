import io
import os
import sys
import traceback
from pathlib import Path

from knowledge.cli.parser import build_parser
from knowledge.errors import (
    ItemNotFoundError,
    KnowledgeError,
    StorageError,
    ValidationError,
)
from knowledge.service import KnowledgeService
from knowledge.storage.sqlite import SqliteKnowledgeRepository

DEFAULT_DB_PATH = Path.home() / ".knowledge" / "knowledge.db"

EXIT_CODES = {ValidationError: 2, ItemNotFoundError: 3, StorageError: 4}


def resolve_db_path(cli_value: str | None) -> Path:
    if cli_value is not None and not cli_value.strip():
        raise ValidationError("Database path must not be empty.")
    raw = cli_value or os.environ.get("KNOWLEDGE_DB")
    return Path(raw).expanduser() if raw else DEFAULT_DB_PATH


def run(argv: list[str]) -> int:
    """Run one command and return the exit code. The only place that catches errors."""
    args = build_parser().parse_args(argv)
    try:
        with SqliteKnowledgeRepository(resolve_db_path(args.db)) as repository:
            service = KnowledgeService(repository)
            args.handler(args, service)
        return 0
    except ItemNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        print("Use 'knowledge list' to see all IDs.", file=sys.stderr)
        return EXIT_CODES.get(type(error), 1)
    except KnowledgeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_CODES.get(type(error), 1)
    except Exception:
        if args.debug:
            traceback.print_exc()
        print("Unexpected error. Run again with --debug for details.", file=sys.stderr)
        return 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    return run(sys.argv[1:])
