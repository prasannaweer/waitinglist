import tempfile
import unittest
from pathlib import Path

from src.models import WaitlistEntry

from src.storage import (
    LibraryStorage,
    StorageError
)


class TestLibraryStorage(unittest.TestCase):

    def setUp(self):

        self.temp_directory = (
            tempfile.TemporaryDirectory()
        )

        self.root = Path(
            self.temp_directory.name
        )

        self.books_file = (
            self.root / "books.txt"
        )

        self.waitlists_file = (
            self.root / "waitlists.json"
        )

        self.books_file.write_text(
            "1|1984|George Orwell\n"
            "2|Dune|Frank Herbert\n",
            encoding="utf-8"
        )

        self.storage = LibraryStorage(
            self.books_file,
            self.waitlists_file
        )

    def tearDown(self):

        self.temp_directory.cleanup()

    def test_load_books(self):

        books = self.storage.load_books()

        self.assertEqual(
            len(books),
            2
        )

        self.assertEqual(
            books["1"]["title"],
            "1984"
        )

        self.assertEqual(
            books["2"]["author"],
            "Frank Herbert"
        )

    def test_missing_waitlist_file_creates_file(self):

        waitlists = self.storage.load_waitlists()

        self.assertEqual(
            waitlists,
            {}
        )

        self.assertTrue(
            self.waitlists_file.exists()
        )

    def test_save_and_reload_waitlists(self):

        waitlist_data = {
            "1": [
                WaitlistEntry(
                    member_id="M001",

                    requested_at=(
                        "2026-07-12T10:00:00"
                    )
                )
            ]
        }

        self.storage.save_waitlists(
            waitlist_data
        )

        loaded_data = (
            self.storage.load_waitlists()
        )

        self.assertEqual(
            loaded_data["1"][0].member_id,
            "M001"
        )

    def test_invalid_book_record(self):

        self.books_file.write_text(
            "1|1984\n",
            encoding="utf-8"
        )

        with self.assertRaises(
            StorageError
        ):
            self.storage.load_books()

    def test_duplicate_book_id(self):

        self.books_file.write_text(
            "1|1984|George Orwell\n"
            "1|Dune|Frank Herbert\n",
            encoding="utf-8"
        )

        with self.assertRaises(
            StorageError
        ):
            self.storage.load_books()

    def test_invalid_waitlist_json(self):

        self.waitlists_file.write_text(
            "{invalid json}",
            encoding="utf-8"
        )

        with self.assertRaises(
            StorageError
        ):
            self.storage.load_waitlists()


if __name__ == "__main__":
    unittest.main()