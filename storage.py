import json
from pathlib import Path
from typing import Any

from src.models import WaitlistEntry


class StorageError(Exception):
    """Raised when a data file cannot be read or saved."""


class LibraryStorage:
    """Load books and save/load waitlist information."""

    def __init__(
        self,
        books_file: str | Path,
        waitlists_file: str | Path
    ):
        self.books_file = Path(books_file)
        self.waitlists_file = Path(waitlists_file)

    def load_books(self) -> dict[str, dict[str, str]]:
        """
        Load books from books.txt.

        Expected format:
        book_id|title|author
        """

        if not self.books_file.exists():
            raise StorageError(
                f"Book file was not found: {self.books_file}"
            )

        books = {}

        try:
            with self.books_file.open(
                "r",
                encoding="utf-8"
            ) as file:

                for line_number, raw_line in enumerate(
                    file,
                    start=1
                ):
                    line = raw_line.strip()

                    if not line:
                        continue

                    parts = [
                        part.strip()
                        for part in line.split("|")
                    ]

                    if len(parts) != 3:
                        raise StorageError(
                            f"Invalid book record on line "
                            f"{line_number}."
                        )

                    book_id, title, author = parts

                    if not book_id or not title or not author:
                        raise StorageError(
                            f"Empty value in book record "
                            f"on line {line_number}."
                        )

                    if book_id in books:
                        raise StorageError(
                            f"Duplicate book ID: {book_id}"
                        )

                    books[book_id] = {
                        "book_id": book_id,
                        "title": title,
                        "author": author
                    }

        except OSError as error:
            raise StorageError(
                f"Could not read the book file: {error}"
            ) from error

        if not books:
            raise StorageError(
                "The book catalogue is empty."
            )

        return books

    def load_waitlists(
        self
    ) -> dict[str, list[WaitlistEntry]]:
        """
        Load saved waiting lists from waitlists.json.
        """

        if not self.waitlists_file.exists():
            self.waitlists_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            self.waitlists_file.write_text(
                "{}",
                encoding="utf-8"
            )

            return {}

        try:
            content = self.waitlists_file.read_text(
                encoding="utf-8"
            )

            raw_data = json.loads(content)

        except json.JSONDecodeError as error:
            raise StorageError(
                f"Invalid JSON file: {error}"
            ) from error

        except OSError as error:
            raise StorageError(
                f"Could not read the waitlist file: {error}"
            ) from error

        if not isinstance(raw_data, dict):
            raise StorageError(
                "Waitlist data must be a JSON object."
            )

        waitlists = {}

        for book_id, entries in raw_data.items():

            if not isinstance(entries, list):
                raise StorageError(
                    f"Waitlist for book {book_id} "
                    "must be a list."
                )

            try:
                waitlists[str(book_id)] = [
                    WaitlistEntry.from_dict(entry)
                    for entry in entries
                ]

            except (
                KeyError,
                TypeError,
                ValueError
            ) as error:
                raise StorageError(
                    f"Invalid waitlist entry for "
                    f"book {book_id}: {error}"
                ) from error

        return waitlists

    def save_waitlists(
        self,
        waitlists: dict[str, Any]
    ) -> None:
        """
        Save waiting lists into waitlists.json.

        This accepts the result of:

        service.export_waitlists()
        """

        self.waitlists_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        serialised_data = {}

        for book_id, entries in waitlists.items():

            serialised_data[str(book_id)] = []

            for entry in entries:

                if isinstance(entry, WaitlistEntry):
                    serialised_data[str(book_id)].append(
                        entry.to_dict()
                    )

                elif isinstance(entry, dict):
                    serialised_data[str(book_id)].append(
                        {
                            "member_id": str(
                                entry["member_id"]
                            ).strip(),

                            "requested_at": str(
                                entry["requested_at"]
                            ).strip()
                        }
                    )

                else:
                    raise StorageError(
                        "Unsupported waitlist entry type."
                    )

        temporary_file = self.waitlists_file.with_suffix(
            ".tmp"
        )

        try:
            temporary_file.write_text(
                json.dumps(
                    serialised_data,
                    indent=4
                ),
                encoding="utf-8"
            )

            temporary_file.replace(
                self.waitlists_file
            )

        except (
            OSError,
            KeyError
        ) as error:
            raise StorageError(
                f"Could not save waitlists: {error}"
            ) from error