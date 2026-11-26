import argparse

from knowledge.cli import commands


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid ID (expected a whole number).")
    if number < 1:
        raise argparse.ArgumentTypeError("ID must be a positive number.")
    return number


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", help="Path to the database file.")
    common.add_argument("--debug", action="store_true", help="Show the traceback on unexpected errors.")

    parser = argparse.ArgumentParser(prog="knowledge", description="A small command-line knowledge base.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", parents=[common], help="Add a new item with a title and content.")
    add.add_argument("title")
    add.add_argument("content")
    add.set_defaults(handler=commands.handle_add)

    list_cmd = subparsers.add_parser("list", parents=[common], help="List all items.")
    list_cmd.set_defaults(handler=commands.handle_list)

    show = subparsers.add_parser("show", parents=[common], help="Show the item with the given ID.")
    show.add_argument("id", type=positive_int)
    show.set_defaults(handler=commands.handle_show)

    search = subparsers.add_parser("search", parents=[common], help="Find items whose title or content contains the text.")
    search.add_argument("text")
    search.set_defaults(handler=commands.handle_search)

    delete = subparsers.add_parser("delete", parents=[common], help="Delete the item with the given ID.")
    delete.add_argument("id", type=positive_int)
    delete.set_defaults(handler=commands.handle_delete)

    return parser