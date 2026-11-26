import pytest

from knowledge.errors import ItemNotFoundError, ValidationError


def test_add_strips_whitespace_and_assigns_id(service):
    item = service.add("  Python  ", "  A language.  ")

    assert item.id == 1
    assert item.title == "Python"
    assert item.content == "A language."


@pytest.mark.parametrize(
    "title, content",
    [("", "text"), ("   ", "text"), ("Title", ""), ("Title", "\n")],
)
def test_empty_title_or_content_is_rejected(service, title, content):
    with pytest.raises(ValidationError):
        service.add(title, content)


def test_multiline_title_is_rejected(service):
    with pytest.raises(ValidationError):
        service.add("Line 1\nLine 2", "text")


def test_get_missing_id_raises_not_found(service):
    with pytest.raises(ItemNotFoundError):
        service.get(42)


def test_search_is_case_insensitive_including_cyrillic(service):
    service.add("Докер", "Контейнери")
    service.add("Python", "A language")

    assert [item.title for item in service.search("ДОКЕР")] == ["Докер"]
    assert [item.title for item in service.search("python")] == ["Python"]


def test_delete_missing_id_raises_not_found(service):
    with pytest.raises(ItemNotFoundError):
        service.delete(42)


def test_update_changes_only_given_fields(service):
    item = service.add("Docker", "Old content")

    updated = service.update(item.id, title="Docker Engine")

    assert updated.title == "Docker Engine"
    assert updated.content == "Old content"
    assert updated.id == item.id
    assert updated.created_at == item.created_at


def test_update_without_fields_is_rejected(service):
    item = service.add("Docker", "text")

    with pytest.raises(ValidationError):
        service.update(item.id)


def test_update_missing_id_raises_not_found(service):
    with pytest.raises(ItemNotFoundError):
        service.update(42, title="Anything")


@pytest.mark.parametrize("title", ["", "   ", "Line 1\nLine 2"])
def test_update_rejects_invalid_title(service, title):
    item = service.add("Docker", "text")

    with pytest.raises(ValidationError):
        service.update(item.id, title=title)


def test_invalid_characters_are_rejected(service):
    with pytest.raises(ValidationError):
        service.add("bad\udcff", "text")