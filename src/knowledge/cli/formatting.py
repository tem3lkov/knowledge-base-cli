from knowledge.models import KnowledgeItem


def format_list(items: list[KnowledgeItem]) -> str:
    if not items:
        return 'No items yet. Add one with: knowledge add "<title>" "<content>"'
    width = len(str(items[-1].id))
    return "\n".join(f"{item.id:>{width}} | {item.title}" for item in items)


def format_item(item: KnowledgeItem) -> str:
    created = item.created_at.strftime("%Y-%m-%d %H:%M")
    return f"Title: {item.title}\n\n{item.content}\n\nCreated: {created} UTC"


def format_search_results(items: list[KnowledgeItem], text: str) -> str:
    if not items:
        return f'No items match "{text}".'
    return format_list(items)