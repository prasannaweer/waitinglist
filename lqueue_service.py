from collections import deque
from typing import Iterable, Optional

from src.exceptions import (
    DuplicateRequestError,
    InvalidBookIDError,
    WaitlistEntryNotFoundError,
)
from src.models import WaitlistEntry


class WaitlistService:
    """
    Manages one FIFO queue for each library book.

    FIFO means:
        First In, First Out.

    The first member added to the queue is the first member
    selected when the book is returned.
    """

    def __init__(
        self,
        valid_book_ids: Iterable[str],
        initial_waitlists: Optional[
            dict[str, Iterable[WaitlistEntry]]
        ] = None,
    ) -> None:

        self.valid_book_ids = {
            str(book_id).strip()
            for book_id in valid_book_ids
        }

        self.waitlists: dict[
            str,
            deque[WaitlistEntry]
        ] = {}

        if initial_waitlists:
            for book_id, entries in initial_waitlists.items():
                cleaned_book_id = str(book_id).strip()

                self.waitlists[cleaned_book_id] = deque(entries)

    def _validate_book_id(self, book_id: str) -> str:
        """
        Clean and validate a book ID.

        Valid IDs for this project are:
        1, 2, 3, 4, 5, 6, 7, 8 and 9.
        """

        cleaned_book_id = str(book_id).strip()

        if cleaned_book_id not in self.valid_book_ids:
            raise InvalidBookIDError(
                f"Book ID {cleaned_book_id} does not exist."
            )

        return cleaned_book_id

    @staticmethod
    def _validate_member_id(member_id: str) -> str:
        """Check that a member ID is not empty."""

        cleaned_member_id = str(member_id).strip()

        if not cleaned_member_id:
            raise ValueError("Member ID cannot be empty.")

        return cleaned_member_id

    def add_to_waitlist(
        self,
        book_id: str,
        member_id: str,
    ) -> int:
        """
        Add a member to the rear of the book's queue.

        Returns:
            The new queue position.
        """

        book_id = self._validate_book_id(book_id)
        member_id = self._validate_member_id(member_id)

        queue = self.waitlists.setdefault(
            book_id,
            deque(),
        )

        for entry in queue:
            if entry.member_id == member_id:
                raise DuplicateRequestError(
                    f"Member {member_id} is already waiting "
                    f"for book {book_id}."
                )

        new_entry = WaitlistEntry.create(member_id)

        queue.append(new_entry)

        return len(queue)

    def get_waitlist(
        self,
        book_id: str,
    ) -> list[WaitlistEntry]:
        """Return the queue in FIFO order."""

        book_id = self._validate_book_id(book_id)

        queue = self.waitlists.get(
            book_id,
            deque(),
        )

        return list(queue)

    def get_position(
        self,
        book_id: str,
        member_id: str,
    ) -> Optional[int]:
        """
        Return the member's queue position.

        Returns None when the member is not waiting.
        """

        book_id = self._validate_book_id(book_id)
        member_id = self._validate_member_id(member_id)

        queue = self.waitlists.get(
            book_id,
            deque(),
        )

        for position, entry in enumerate(
            queue,
            start=1,
        ):
            if entry.member_id == member_id:
                return position

        return None

    def peek_next(
        self,
        book_id: str,
    ) -> Optional[WaitlistEntry]:
        """
        Return the first waiting member without removing them.
        """

        book_id = self._validate_book_id(book_id)

        queue = self.waitlists.get(
            book_id,
            deque(),
        )

        if not queue:
            return None

        return queue[0]

    def serve_next(
        self,
        book_id: str,
    ) -> Optional[WaitlistEntry]:
        """
        Remove and return the first waiting member.

        This function should be called when a book is returned.
        """

        book_id = self._validate_book_id(book_id)

        queue = self.waitlists.get(
            book_id,
            deque(),
        )

        if not queue:
            return None

        selected_member = queue.popleft()

        if not queue:
            self.waitlists.pop(book_id, None)

        return selected_member

    def cancel_request(
        self,
        book_id: str,
        member_id: str,
    ) -> None:
        """Remove a member from a book's waitlist."""

        book_id = self._validate_book_id(book_id)
        member_id = self._validate_member_id(member_id)

        queue = self.waitlists.get(
            book_id,
            deque(),
        )

        updated_queue = deque(
            entry
            for entry in queue
            if entry.member_id != member_id
        )

        if len(updated_queue) == len(queue):
            raise WaitlistEntryNotFoundError(
                f"Member {member_id} is not waiting "
                f"for book {book_id}."
            )

        if updated_queue:
            self.waitlists[book_id] = updated_queue
        else:
            self.waitlists.pop(book_id, None)

    def get_waiting_count(
        self,
        book_id: str,
    ) -> int:
        """Return the number of members waiting for a book."""

        book_id = self._validate_book_id(book_id)

        return len(
            self.waitlists.get(
                book_id,
                deque(),
            )
        )

    def export_waitlists(self) -> dict:
        """
        Convert all queues into JSON-compatible dictionaries.

        Member 2 can pass this result to the storage function.
        """

        return {
            book_id: [
                entry.to_dict()
                for entry in queue
            ]
            for book_id, queue in self.waitlists.items()
        }