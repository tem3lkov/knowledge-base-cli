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