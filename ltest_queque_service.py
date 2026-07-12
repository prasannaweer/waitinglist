import unittest

from src.exceptions import (
    DuplicateRequestError,
    InvalidBookIDError,
    WaitlistEntryNotFoundError,
)
from src.queue_service import WaitlistService


class TestWaitlistService(unittest.TestCase):

    def setUp(self) -> None:
        self.valid_book_ids = {
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
        }

        self.service = WaitlistService(
            valid_book_ids=self.valid_book_ids
        )

    def test_first_member_gets_position_one(self):
        position = self.service.add_to_waitlist(
            "1",
            "M001",
        )

        self.assertEqual(position, 1)

    def test_second_member_gets_position_two(self):
        self.service.add_to_waitlist(
            "1",
            "M001",
        )

        position = self.service.add_to_waitlist(
            "1",
            "M002",
        )

        self.assertEqual(position, 2)

    def test_fifo_order(self):
        self.service.add_to_waitlist(
            "1",
            "M001",
        )

        self.service.add_to_waitlist(
            "1",
            "M002",
        )

        selected_member = self.service.serve_next("1")

        self.assertIsNotNone(selected_member)
        self.assertEqual(
            selected_member.member_id,
            "M001",
        )

    def test_duplicate_request_is_rejected(self):
        self.service.add_to_waitlist(
            "2",
            "M001",
        )

        with self.assertRaises(
            DuplicateRequestError
        ):
            self.service.add_to_waitlist(
                "2",
                "M001",
            )

    def test_get_member_position(self):
        self.service.add_to_waitlist(
            "3",
            "M001",
        )

        self.service.add_to_waitlist(
            "3",
            "M002",
        )

        position = self.service.get_position(
            "3",
            "M002",
        )

        self.assertEqual(position, 2)

    def test_peek_does_not_remove_member(self):
        self.service.add_to_waitlist(
            "4",
            "M001",
        )

        first_member = self.service.peek_next("4")

        self.assertEqual(
            first_member.member_id,
            "M001",
        )

        self.assertEqual(
            self.service.get_waiting_count("4"),
            1,
        )

    def test_cancel_request(self):
        self.service.add_to_waitlist(
            "5",
            "M001",
        )

        self.service.add_to_waitlist(
            "5",
            "M002",
        )

        self.service.cancel_request(
            "5",
            "M001",
        )

        position = self.service.get_position(
            "5",
            "M002",
        )

        self.assertEqual(position, 1)

    def test_cancel_unknown_request(self):
        with self.assertRaises(
            WaitlistEntryNotFoundError
        ):
            self.service.cancel_request(
                "6",
                "M999",
            )

    def test_invalid_book_id_is_rejected(self):
        with self.assertRaises(
            InvalidBookIDError
        ):
            self.service.add_to_waitlist(
                "10",
                "M001",
            )

    def test_empty_queue_returns_none(self):
        selected_member = self.service.serve_next("7")

        self.assertIsNone(selected_member)

    def test_different_books_have_separate_queues(self):
        self.service.add_to_waitlist(
            "8",
            "M001",
        )

        self.service.add_to_waitlist(
            "9",
            "M002",
        )

        self.assertEqual(
            self.service.get_waiting_count("8"),
            1,
        )

        self.assertEqual(
            self.service.get_waiting_count("9"),
            1,
        )


if __name__ == "__main__":
    unittest.main()