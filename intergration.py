import tempfile
import unittest
from pathlib import Path

from src.queue_service import WaitlistService
from src.reports import build_waitlist_summary
from src.storage import LibraryStorage


class TestMember2Integration(unittest.TestCase):

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

        self.waitlists_file.write_text(
            "{}",
            encoding="utf-8"
        )

        self.storage = LibraryStorage(
            self.books_file,
            self.waitlists_file
        )

    def tearDown(self):

        self.temp_directory.cleanup()

    def test_storage_and_queue_integration(self):

        books = self.storage.load_books()

        service = WaitlistService(
            books.keys()
        )

        service.add_to_waitlist(
            "1",
            "M001"
        )

        service.add_to_waitlist(
            "1",
            "M002"
        )

        self.storage.save_waitlists(
            service.export_waitlists()
        )

        loaded_waitlists = (
            self.storage.load_waitlists()
        )

        new_service = WaitlistService(
            valid_book_ids=books.keys(),

            initial_waitlists=loaded_waitlists
        )

        position = new_service.get_position(
            "1",
            "M002"
        )

        self.assertEqual(
            position,
            2
        )

    def test_report_summary(self):

        books = self.storage.load_books()

        service = WaitlistService(
            books.keys()
        )

        service.add_to_waitlist(
            "2",
            "M001"
        )

        report = build_waitlist_summary(
            service,
            books
        )

        self.assertEqual(
            report[0]["book_id"],
            "2"
        )

        self.assertEqual(
            report[0]["waiting_count"],
            1
        )

        self.assertEqual(
            report[0]["next_member_id"],
            "M001"
        )


if __name__ == "__main__":
    unittest.main()