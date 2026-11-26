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
    try:
        with SqliteKnowledgeRepository(resolve_db_path(args.db)) as repository:
            service = KnowledgeService(repository)
            args.handler(args, service)
        return 0
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
