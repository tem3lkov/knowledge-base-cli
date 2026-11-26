from argparse import Namespace

from knowledge.cli import formatting
from knowledge.service import KnowledgeService


def handle_add(args: Namespace, service: KnowledgeService) -> None:
    item = service.add(args.title, args.content)
    print(f"Added item {item.id}: {item.title}")


def handle_list(args: Namespace, service: KnowledgeService) -> None:
    print(formatting.format_list(service.list_items()))


def handle_show(args: Namespace, service: KnowledgeService) -> None:
    print(formatting.format_item(service.get(args.id)))


def handle_search(args: Namespace, service: KnowledgeService) -> None:
    items = service.search(args.text)
    print(formatting.format_search_results(items, args.text))


def handle_delete(args: Namespace, service: KnowledgeService) -> None:
    service.delete(args.id)
    print(f"Deleted item {args.id}.")
