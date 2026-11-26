import os
import sys
import traceback
from pathlib import Path

from knowledge.cli.parser import build_parser
from knowledge.errors import ItemNotFoundError, KnowledgeError, ValidationError
from knowledge.service import KnowledgeService
from knowledge.storage.sqlite import SqliteKnowledgeRepository

DEFAULT_DB_PATH = Path.home() / ".knowledge" / "knowledge.db"


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
        return error.exit_code
    except KnowledgeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return error.exit_code
    except Exception:
        if args.debug:
            traceback.print_exc()
        print("Unexpected error. Run again with --debug for details.", file=sys.stderr)
        return 1


def main() -> int:
    return run(sys.argv[1:])
