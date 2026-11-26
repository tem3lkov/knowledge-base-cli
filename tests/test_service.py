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
