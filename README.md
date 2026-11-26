# Knowledge Base CLI

[![Tests](https://github.com/tem3lkov/knowledge-base-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/tem3lkov/knowledge-base-cli/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)

A small command-line app for storing, searching and managing short notes.

## Requirements

- [uv](https://docs.astral.sh/uv/) – it also installs the right Python version (3.12).

## Setup

```bash
git clone https://github.com/tem3lkov/knowledge-base-cli.git
cd knowledge-base-cli
uv sync
```

## Usage

Run commands with `uv run knowledge ...` (or `uv run python -m knowledge ...`).
After `source .venv/bin/activate`, plain `knowledge ...` works too.

```text
$ uv run knowledge add "Python" "Python is a high-level programming language."
Added item 1: Python

$ uv run knowledge add "Docker" "Docker packages applications into containers."
Added item 2: Docker

$ uv run knowledge list
1 | Python
2 | Docker

$ uv run knowledge show 2
Title: Docker
Created: 2026-11-26 21:59

Docker packages applications into containers.

$ uv run knowledge search CONTAINER
2 | Docker

$ uv run knowledge edit 2 --title "Docker Engine"
Updated item 2: Docker Engine

$ uv run knowledge show 2
Title: Docker Engine
Created: 2026-11-26 21:59
Updated: 2026-11-26 22:03

Docker packages applications into containers.

$ uv run knowledge delete 1
Deleted item 1.
```

| Command | What it does |
| --- | --- |
| `add TITLE CONTENT` | Adds a new item |
| `list` | Lists all items (ID and title) |
| `show ID` | Shows the full item |
| `search TEXT` | Finds items whose title or content contains the text (case-insensitive) |
| `delete ID` | Deletes the item |
| `edit ID [--title T] [--content C]` | Changes the title and/or content (optional feature) |

`uv run knowledge --help` and `uv run knowledge <command> --help` show all options.

### Where the data is stored

By default in `~/.knowledge/knowledge.db`. Another file can be used with `--db PATH`
or the `KNOWLEDGE_DB` environment variable (`--db` wins). Options go after the command:

```bash
uv run knowledge list --db /tmp/test.db
```

### Errors

Errors are printed as one clear line, never as a Python traceback, and each kind has
its own exit code:

| Exit code | Meaning | Example |
| --- | --- | --- |
| 0 | Success | |
| 2 | Invalid input | missing argument, `show abc`, empty title |
| 3 | Item not found | `show 42` when there is no item 42 |
| 4 | The database cannot be opened | the file is corrupted or not a database |
| 1 | Unexpected error | a bug; `--debug` shows the traceback |

```text
$ uv run knowledge show 42
Error: No item with ID 42.
Use 'knowledge list' to see all IDs.

$ uv run knowledge add "" "text"
Error: Title must not be empty.
```

## Running the tests

```bash
uv run pytest
```

The tests also run on every push and pull request with GitHub Actions.

## Project structure

```text
src/knowledge/
├── models.py          # KnowledgeItem
├── errors.py          # error classes with their exit codes
├── service.py         # KnowledgeService – validation and business rules
├── storage/
│   ├── base.py        # KnowledgeRepository – storage interface
│   └── sqlite.py      # SqliteKnowledgeRepository
└── cli/
    ├── parser.py      # argparse setup, one subcommand per command
    ├── commands.py    # one small handler function per command
    ├── formatting.py  # turns items into text
    └── app.py         # entry point, the only place that catches errors
tests/                 # storage, service and end-to-end CLI tests
```

## Design decisions

```text
CLI (argparse) ──▶ KnowledgeService (rules) ──▶ KnowledgeRepository (SQLite)
```

**Layers.** The CLI only parses arguments and prints. `KnowledgeService` holds the rules
(validation, "item not found"). The repository only stores and reads data. The service
gets the repository passed in, so the tests can use a temporary database.

**Storage: SQLite.** It comes with Python, so there are no extra dependencies, and every
change runs in a transaction, so the file is never left half-written. A command reads
only the rows it needs instead of loading and rewriting a whole file like with JSON.
The trade-off is that the file is not human-readable. The service depends only on the
`KnowledgeRepository` interface, so another storage could be added without changing it.

**CLI: argparse with plain functions.** argparse comes with Python and already does
what a command dispatcher needs: it finds the command, checks the arguments, prints help
and calls the right handler (`set_defaults(handler=...)`). Adding a command is one
function and a few lines in the parser. A class per command would add code without
adding anything for six short commands.

**Search in Python, not in SQL.** SQLite's `LIKE` ignores case only for Latin letters,
so a search for "ДОКЕР" would not find "Докер". The service filters with
`str.casefold()` instead, which works for all languages. Both ways scan every item,
so it is not slower.

**Times.** Stored in UTC, shown in the local time zone.

## Assumptions

- IDs are whole numbers given by the database and are never reused after a delete.
- The title is a single line of up to 200 characters; the content is up to 10,000 characters.
- Leading and trailing spaces are removed; an empty title or content is rejected.
- Duplicate titles are allowed.
- Search matches part of the title or content and ignores case.
- `delete` does not ask for confirmation.
- One user, one local database file.

## Tests

The tests follow the requirements and the error cases from the task:

- **Storage:** data survives reopening the database, IDs are not reused, a corrupted
  file or invalid data in it gives a clear error.
- **Service:** empty input, multi-line titles, invalid characters, missing IDs,
  case-insensitive search (including Cyrillic), updating only the given fields.
- **CLI (end to end):** every command with its output and exit code, missing and
  invalid arguments (including IDs too large for SQLite), a database with the wrong
  structure, and that no traceback is shown.

They use a temporary database (`tmp_path`) and pytest's `capsys` to check the output.

## Optional feature: `edit`

Without it, fixing a typo means deleting the item and adding it again with a new ID.
`edit` changes only the given fields and keeps the ID and creation time; `show` then
also prints when the item was last updated. It was developed on a separate branch and
merged through a pull request.

## Possible improvements

- Full-text search with SQLite FTS5 for large knowledge bases.
- `export` / `import` to JSON for backups.
- Tags or categories.

## Use of AI tools

I used AI assistants (Claude and Gemini) while working on the project:

- **Design:** I set the principles the code had to follow (layers, CLI separate from
  the core logic, dependency injection, typed errors) and discussed how to apply them
  in Python, including SQLite vs JSON for storage.
- **Tests:** help with some of the test cases and with pytest features I had not used
  before (`tmp_path`, `capsys`, `parametrize`).
- **Tooling:** questions about argparse, SQLite, uv and GitHub Actions.
- **README:** wording of this file, which I checked against the actual app.

**How I checked the results:** I ran the tests after every change, ran every command by
hand (including the error cases), read the code line by line and fixed the warnings
from Pylance and ruff.

**What I changed or rejected:** I replaced a class per command with plain functions and
argparse, removed abstractions I could not justify, and moved the search from SQL to
Python because SQLite's `LIKE` ignores case only for Latin letters.