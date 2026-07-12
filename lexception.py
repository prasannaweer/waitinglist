class WaitlistError(Exception):
    """Base exception for all waitlist errors."""


class InvalidBookIDError(WaitlistError):
    """Raised when a book ID is invalid."""


class DuplicateRequestError(WaitlistError):
    """Raised when a member is already waiting for the book."""


class WaitlistEntryNotFoundError(WaitlistError):
    """Raised when a member is not found in a waitlist."""


class EmptyWaitlistError(WaitlistError):
    """Raised when an operation requires a non-empty waitlist."""