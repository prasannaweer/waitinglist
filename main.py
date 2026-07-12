from pathlib import Path

from src.exceptions import WaitlistError
from src.queue_service import WaitlistService

from src.reports import (
    build_waitlist_summary,
    export_waitlist_report_csv
)

from src.storage import (
    LibraryStorage,
    StorageError
)

from src.validation import (
    clean_book_id,
    clean_member_id,
    clean_menu_choice
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIRECTORY = PROJECT_ROOT / "data"


storage = LibraryStorage(
    books_file=DATA_DIRECTORY / "books.txt",

    waitlists_file=DATA_DIRECTORY / "waitlists.json"
)


def display_books(
    books: dict[str, dict]
) -> None:
    """
    Display all books.
    """

    print("\nBOOK CATALOGUE")

    print("-" * 70)

    print(
        f"{'ID':<5}"
        f"{'Title':<35}"
        f"{'Author'}"
    )

    print("-" * 70)

    sorted_book_ids = sorted(
        books,
        key=lambda value: (
            int(value)
            if value.isdigit()
            else value
        )
    )

    for book_id in sorted_book_ids:

        book = books[book_id]

        print(
            f"{book_id:<5}"
            f"{book['title']:<35}"
            f"{book['author']}"
        )


def display_waitlist(
    service: WaitlistService,
    books: dict[str, dict],
    book_id: str
) -> None:
    """
    Display one book's waiting list.
    """

    book = books[book_id]

    queue = service.get_waitlist(
        book_id
    )

    print(
        f"\nBook: {book_id} - "
        f"{book['title']} "
        f"by {book['author']}"
    )

    if not queue:
        print(
            "No members are waiting for this book."
        )

        return

    print("-" * 70)

    print(
        f"{'Position':<12}"
        f"{'Member ID':<20}"
        f"{'Requested At'}"
    )

    print("-" * 70)

    for position, entry in enumerate(
        queue,
        start=1
    ):
        print(
            f"{position:<12}"
            f"{entry.member_id:<20}"
            f"{entry.requested_at}"
        )


def save_current_waitlists(
    storage: LibraryStorage,
    service: WaitlistService
) -> None:
    """
    Save the current queues.
    """

    data = service.export_waitlists()

    storage.save_waitlists(
        data
    )


def display_summary(
    service: WaitlistService,
    books: dict[str, dict]
) -> None:
    """
    Display the waiting-list summary.
    """

    rows = build_waitlist_summary(
        service,
        books
    )

    if not rows:
        print(
            "\nThere are no active waitlists."
        )

        return

    print("\nWAITLIST SUMMARY")

    print("-" * 80)

    print(
        f"{'ID':<5}"
        f"{'Title':<35}"
        f"{'Waiting':<12}"
        f"{'Next Member'}"
    )

    print("-" * 80)

    for row in rows:

        print(
            f"{row['book_id']:<5}"
            f"{row['title']:<35}"
            f"{row['waiting_count']:<12}"
            f"{row['next_member_id']}"
        )


def run_menu() -> None:
    """
    Run the main Waitlist Manager menu.
    """

    books = storage.load_books()

    loaded_waitlists = storage.load_waitlists()

    service = WaitlistService(
        valid_book_ids=books.keys(),

        initial_waitlists=loaded_waitlists
    )

    while True:

        print(
            """
================ TEAM 3: WAITLIST MANAGER ================

1. Display book catalogue
2. Add member to a waitlist
3. Display a book's waitlist
4. Check a member's queue position
5. View the next waiting member
6. Process a returned book
7. Cancel a waitlist request
8. Display waitlist summary
9. Export waitlist report to CSV
0. Exit

==========================================================
"""
        )

        choice = clean_menu_choice(
            input("Select an option: ")
        )

        try:

            if choice == "1":

                display_books(
                    books
                )

            elif choice == "2":

                book_id = clean_book_id(
                    input(
                        "Enter book ID from 1 to 9: "
                    ),
                    books
                )

                member_id = clean_member_id(
                    input(
                        "Enter member ID: "
                    )
                )

                position = service.add_to_waitlist(
                    book_id,
                    member_id
                )

                save_current_waitlists(
                    storage,
                    service
                )

                print(
                    f"Member {member_id} "
                    "was added successfully."
                )

                print(
                    f"Queue position: {position}"
                )

            elif choice == "3":

                book_id = clean_book_id(
                    input(
                        "Enter book ID from 1 to 9: "
                    ),
                    books
                )

                display_waitlist(
                    service,
                    books,
                    book_id
                )

            elif choice == "4":

                book_id = clean_book_id(
                    input(
                        "Enter book ID from 1 to 9: "
                    ),
                    books
                )

                member_id = clean_member_id(
                    input(
                        "Enter member ID: "
                    )
                )

                position = service.get_position(
                    book_id,
                    member_id
                )

                if position is None:

                    print(
                        f"Member {member_id} "
                        "is not waiting for "
                        f"book {book_id}."
                    )

                else:

                    print(
                        f"Member {member_id}'s "
                        f"queue position is {position}."
                    )

            elif choice == "5":

                book_id = clean_book_id(
                    input(
                        "Enter book ID from 1 to 9: "
                    ),
                    books
                )

                next_member = service.peek_next(
                    book_id
                )

                if next_member is None:

                    print(
                        "No member is waiting "
                        "for this book."
                    )

                else:

                    print(
                        "Next waiting member:",
                        next_member.member_id
                    )

                    print(
                        "Requested at:",
                        next_member.requested_at
                    )

            elif choice == "6":

                book_id = clean_book_id(
                    input(
                        "Enter returned book ID: "
                    ),
                    books
                )

                selected_member = service.serve_next(
                    book_id
                )

                save_current_waitlists(
                    storage,
                    service
                )

                if selected_member is None:

                    print(
                        "No member is waiting."
                    )

                    print(
                        "The book can be marked "
                        "as available."
                    )

                else:

                    print(
                        "Reserve the returned book "
                        "for member:"
                    )

                    print(
                        selected_member.member_id
                    )

            elif choice == "7":

                book_id = clean_book_id(
                    input(
                        "Enter book ID from 1 to 9: "
                    ),
                    books
                )

                member_id = clean_member_id(
                    input(
                        "Enter member ID: "
                    )
                )

                service.cancel_request(
                    book_id,
                    member_id
                )

                save_current_waitlists(
                    storage,
                    service
                )

                print(
                    "Waitlist request "
                    "cancelled successfully."
                )

            elif choice == "8":

                display_summary(
                    service,
                    books
                )

            elif choice == "9":

                output_file = (
                    PROJECT_ROOT /
                    "waitlist_report.csv"
                )

                result = export_waitlist_report_csv(
                    output_file,
                    service,
                    books
                )

                print(
                    f"Report created successfully: "
                    f"{result}"
                )

            elif choice == "0":

                print(
                    "Waitlist Manager closed."
                )

                break

            else:

                print(
                    "Please enter a valid "
                    "option from 0 to 9."
                )

        except (
            WaitlistError,
            ValueError,
            StorageError
        ) as error:

            print(
                f"Error: {error}"
            )


if __name__ == "__main__":

    try:
        run_menu()

    except StorageError as error:
        print(
            f"Program startup error: {error}"
        )