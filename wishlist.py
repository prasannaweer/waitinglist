from pathlib import Path

CATALOG_FILE = Path(__file__).with_name("library.txt")


def load_catalog():
    """Read library.txt into {id: {"title":..., "author":..., "copies":...}}"""
    catalog = {}
    with CATALOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            book_id, title, author = line.split("|")
            catalog[book_id] = {"title": title, "author": author, "copies": 1}
    return catalog


def print_book(book_id, book, waitlists):
    waiting = len(waitlists.get(book_id, []))
    line = f"[{book_id}] {book['title']} by {book['author']} | available: {book['copies']}"
    if waiting:
        line += f" | waiting: {waiting}"
    print(line)


def show_catalog(catalog, waitlists):
    for book_id in sorted(catalog, key=int):
        print_book(book_id, catalog[book_id], waitlists)


def search_catalog(text, catalog, waitlists):
    text = text.lower()
    found = False
    for book_id, book in catalog.items():
        if text in book["title"].lower() or text in book["author"].lower():
            print_book(book_id, book, waitlists)
            found = True
    if not found:
        print(f"No matches for '{text}'.")


def request_book(book_id, patron, catalog, waitlists):
    if book_id not in catalog:
        print(f"No book with id {book_id}.")
        return

    book = catalog[book_id]
    if book["copies"] > 0:
        book["copies"] -= 1
        print(f"{patron} checked out '{book['title']}'.")
    else:
        queue = waitlists.setdefault(book_id, [])
        if patron in queue:
            print(f"{patron} is already waiting for '{book['title']}'.")
        else:
            queue.append(patron)
            print(f"'{book['title']}' unavailable. {patron} added to waiting list.")


def return_book(book_id, catalog, waitlists):
    if book_id not in catalog:
        print(f"No book with id {book_id}.")
        return

    book = catalog[book_id]
    queue = waitlists.get(book_id)
    if queue:
        next_patron = queue.pop(0)
        if not queue:
            waitlists.pop(book_id, None)
        print(f"'{book['title']}' returned and given to {next_patron}.")
    else:
        book["copies"] += 1
        print(f"'{book['title']}' returned and is now available.")


def show_waitlist(book_id, catalog, waitlists):
    queue = waitlists.get(book_id, [])
    title = catalog.get(book_id, {}).get("title", book_id)
    if not queue:
        print(f"Waiting list for '{title}' is empty.")
        return
    print(f"Waiting list for '{title}':")
    for i, patron in enumerate(queue, start=1):
        print(f"  {i}. {patron}")


def show_help():
    print("Commands:")
    print("  catalog                 Show all books")
    print("  search <text>           Search by title or author")
    print("  request <id> <name>     Request a book by id")
    print("  return <id>             Return a book by id")
    print("  waitlist <id>           Show waiting list for a book")
    print("  help                    Show this help text")
    print("  exit                    Quit")


def main():
    catalog = load_catalog()
    waitlists = {}
    print("Library system loaded. Type 'help' for commands.")

    while True:
        parts = input("> ").strip().split()
        if not parts:
            continue
        command, args = parts[0].lower(), parts[1:]

        if command == "exit":
            break
        elif command == "help":
            show_help()
        elif command == "catalog":
            show_catalog(catalog, waitlists)
        elif command == "search" and args:
            search_catalog(" ".join(args), catalog, waitlists)
        elif command == "request" and len(args) >= 2:
            request_book(args[0], args[1], catalog, waitlists)
        elif command == "return" and args:
            return_book(args[0], catalog, waitlists)
        elif command == "waitlist" and args:
            show_waitlist(args[0], catalog, waitlists)
        else:
            print("Unknown command. Type 'help' for available commands.")


if __name__ == "__main__":
    main()
