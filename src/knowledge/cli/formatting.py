from datetime import datetime

from knowledge.models import KnowledgeItem


def format_list(items: list[KnowledgeItem]) -> str:
    if not items:
        return 'No items yet. Add one with: knowledge add "<title>" "<content>"'
    width = len(str(items[-1].id))
    return "\n".join(f"{item.id:>{width}} | {item.title}" for item in items)


def _local_time(moment: datetime) -> str:
    return moment.astimezone().strftime("%Y-%m-%d %H:%M")


def format_item(item: KnowledgeItem) -> str:
    text = f"Title: {item.title}\nCreated: {_local_time(item.created_at)}"
    if item.updated_at != item.created_at:
        text += f"\nUpdated: {_local_time(item.updated_at)}"
    return f"{text}\n\n{item.content}"


def format_search_results(items: list[KnowledgeItem], text: str) -> str:
    if not items:
        return f'No items match "{text}".'
    return format_list(items)
