import collections
import os
from pathlib import Path

CATALOG_FILENAME = Path(__file__).with_name("library.txt")


def load_catalog(path=CATALOG_FILENAME):
    catalog = {}
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) == 1:
                title = parts[0]
                author = ""
                copies = 1
            elif len(parts) == 2:
                title, copies = parts
                author = ""
                try:
                    copies = int(copies)
                except ValueError:
                    author = copies
                    copies = 1
            else:
                title = parts[0]
                author = parts[1]
                try:
                    copies = int(parts[2])
                except (ValueError, IndexError):
                    copies = 1

            if title in catalog:
                catalog[title]["copies"] += copies
            else:
                catalog[title] = {"author": author, "copies": copies}

    return catalog


def show_catalog(catalog, waitlists):
    if not catalog:
        print("Catalog is empty.")
        return
    print("Catalog:")
    for title, info in sorted(catalog.items()):
        copies = info["copies"]
        author = info["author"]
        waiting = len(waitlists.get(title, []))
        line = f"- {title}"
        if author:
            line += f" by {author}"
        line += f" | available: {copies}"
        if waiting:
            line += f" | waiting: {waiting}"
        print(line)


def request_book(title, patron, catalog, waitlists):
    title = title.strip()
    if title not in catalog:
        print(f"Book '{title}' is not in the catalog.")
        return

    if catalog[title]["copies"] > 0:
        catalog[title]["copies"] -= 1
        print(f"{patron} checked out '{title}'.")
    else:
        queue = waitlists.setdefault(title, collections.deque())
        if patron in queue:
            print(f"{patron} is already on the waiting list for '{title}'.")
            return
        queue.append(patron)
        print(f"'{title}' is not available. {patron} has been added to the waiting list.")


def return_book(title, catalog, waitlists):
    title = title.strip()
    if title not in catalog:
        print(f"Book '{title}' is not in the catalog.")
        return

    queue = waitlists.get(title)
    if queue:
        next_patron = queue.popleft()
        if not queue:
            waitlists.pop(title, None)
        print(f"'{title}' was returned and immediately assigned to {next_patron} from the waiting list.")
        return

    catalog[title]["copies"] += 1
    print(f"'{title}' was returned and is now available.")


def show_waitlist(title, waitlists):
    title = title.strip()
    if title and title not in waitlists:
        print(f"No waiting list found for '{title}'.")
        return

    if title:
        queue = waitlists.get(title, [])
        if not queue:
            print(f"Waiting list for '{title}' is empty.")
            return
        print(f"Waiting list for '{title}':")
        for position, patron in enumerate(queue, start=1):
            print(f"  {position}. {patron}")
    else:
        if not waitlists:
            print("No waiting lists are currently active.")
            return
        print("Active waiting lists:")
        for book_title, queue in sorted(waitlists.items()):
            print(f"- {book_title}: {len(queue)} waiting")


def show_help():
    print("Commands:")
    print("  catalog                 Show all books in the catalog.")
    print("  request <title> <name>  Request a book; join waiting list if unavailable.")
    print("  return <title>          Return a book; next waiting patron receives it.")
    print("  waitlist [title]        Show waiting list for a book or all waiting lists.")
    print("  help                    Show this help text.")
    print("  exit                    Exit the program.")


def main():
    try:
        catalog = load_catalog()
    except FileNotFoundError as error:
        print(error)
        return

    waitlists = {}
    print("Library waiting list system loaded.")
    print("Type 'help' for a list of commands.")

    while True:
        command_line = input("> ").strip()
        if not command_line:
            continue

        parts = command_line.split()
        command = parts[0].lower()

        if command == "exit":
            break
        if command == "help":
            show_help()
            continue
        if command == "catalog":
            show_catalog(catalog, waitlists)
            continue
        if command == "request" and len(parts) >= 3:
            title = " ".join(parts[1:-1])
            patron = parts[-1]
            request_book(title, patron, catalog, waitlists)
            continue
        if command == "return" and len(parts) >= 2:
            title = " ".join(parts[1:])
            return_book(title, catalog, waitlists)
            continue
        if command == "waitlist":
            title = " ".join(parts[1:]) if len(parts) > 1 else ""
            show_waitlist(title, waitlists)
            continue

        print("Unknown command. Type 'help' for available commands.")


if __name__ == "__main__":
    main()
