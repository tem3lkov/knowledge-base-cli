import sqlite3

import pytest

from knowledge.cli.app import run


def run_cli(db_path, *argv: str) -> int:
    return run([*argv, "--db", str(db_path)])


def test_add_then_show_prints_title_and_content(db_path, capsys):
    assert run_cli(db_path, "add", "Docker", "Packages apps into containers.") == 0
    assert run_cli(db_path, "show", "1") == 0

    out = capsys.readouterr().out
    assert "Title: Docker" in out
    assert "Packages apps into containers." in out


def test_list_prints_all_items(db_path, capsys):
    run_cli(db_path, "add", "Python", "Standard library.")
    run_cli(db_path, "add", "Docker", "Container runtime.")

    assert run_cli(db_path, "list") == 0
    out = capsys.readouterr().out
    assert "1 | Python" in out
    assert "2 | Docker" in out


def test_search_finds_matching_items(db_path, capsys):
    run_cli(db_path, "add", "Python", "Standard library.")
    run_cli(db_path, "add", "Docker", "Container runtime.")

    assert run_cli(db_path, "search", "container") == 0
    out = capsys.readouterr().out
    assert "2 | Docker" in out


def test_delete_removes_item(db_path):
    assert run_cli(db_path, "add", "Temp", "To be deleted.") == 0
    assert run_cli(db_path, "delete", "1") == 0
    assert run_cli(db_path, "show", "1") == 3


def test_validation_error_exits_2_without_traceback(db_path, capsys):
    code = run_cli(db_path, "add", "   ", "Content")
    captured = capsys.readouterr()

    assert code == 2
    assert "Title must not be empty." in captured.err
    assert "Traceback" not in captured.err


def test_unknown_id_exits_3_without_traceback(db_path, capsys):
    code = run_cli(db_path, "show", "42")
    captured = capsys.readouterr()

    assert code == 3
    assert "No item with ID 42" in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""


def test_missing_argument_exits_2_with_usage(db_path, capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_cli(db_path, "add", "Python")

    assert exc_info.value.code == 2
    assert "usage:" in capsys.readouterr().err


@pytest.mark.parametrize("bad_id", ["abc", "0", "-1", "1_0", "99999999999999999999"])
def test_invalid_id_exits_2(db_path, bad_id):
    with pytest.raises(SystemExit) as exc_info:
        run_cli(db_path, "show", bad_id)

    assert exc_info.value.code == 2


def test_largest_valid_id_is_accepted(db_path):
    assert run_cli(db_path, "show", "9223372036854775807") == 3


def test_edit_changes_title(db_path, capsys):
    run_cli(db_path, "add", "Docker", "Containers")

    assert run_cli(db_path, "edit", "1", "--title", "Docker Engine") == 0
    run_cli(db_path, "show", "1")

    out = capsys.readouterr().out
    assert "Title: Docker Engine" in out
    assert "Updated:" in out


def test_edit_without_fields_exits_2(db_path, capsys):
    run_cli(db_path, "add", "Docker", "Containers")

    assert run_cli(db_path, "edit", "1") == 2
    assert "Nothing to update" in capsys.readouterr().err


def test_edit_missing_id_exits_3(db_path, capsys):
    assert run_cli(db_path, "edit", "42", "--title", "Docker") == 3
    assert "No item with ID 42" in capsys.readouterr().err


def test_database_with_wrong_schema_exits_4_without_traceback(db_path, capsys):
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, other TEXT)")
        conn.execute("INSERT INTO items (other) VALUES ('x')")
    conn.close()

    code = run_cli(db_path, "list")
    captured = capsys.readouterr()

    assert code == 4
    assert "invalid data" in captured.err
    assert "Traceback" not in captured.err


def test_empty_db_path_exits_2(capsys):
    assert run(["list", "--db", ""]) == 2
    assert "Database path must not be empty." in capsys.readouterr().err
