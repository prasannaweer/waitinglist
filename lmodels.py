from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class WaitlistEntry:
    """
    Represents one member waiting for one book.

    member_id:
        The ID of the library member.

    requested_at:
        Date and time when the member joined the queue.
    """

    member_id: str
    requested_at: str

    @classmethod
    def create(cls, member_id: str) -> "WaitlistEntry":
        """Create a new entry using the current date and time."""

        cleaned_member_id = str(member_id).strip()

        if not cleaned_member_id:
            raise ValueError("Member ID cannot be empty.")

        current_time = datetime.now().isoformat(timespec="seconds")

        return cls(
            member_id=cleaned_member_id,
            requested_at=current_time,
        )

    def to_dict(self) -> dict:
        """Convert the structure into a dictionary."""

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WaitlistEntry":
        """Create a WaitlistEntry from stored dictionary data."""

        return cls(
            member_id=str(data["member_id"]),
            requested_at=str(data["requested_at"]),
        )