def clean_book_id(
    book_id: str,
    books: dict[str, dict]
) -> str:
    """
    Check whether the entered book ID exists.
    """

    cleaned_book_id = str(book_id).strip()

    if not cleaned_book_id:
        raise ValueError(
            "Book ID cannot be empty."
        )

    if cleaned_book_id not in books:
        raise ValueError(
            f"Book ID '{cleaned_book_id}' "
            "does not exist. Use an ID from 1 to 9."
        )

    return cleaned_book_id


def clean_member_id(
    member_id: str
) -> str:
    """
    Check whether the member ID is valid.
    """

    cleaned_member_id = str(member_id).strip()

    if not cleaned_member_id:
        raise ValueError(
            "Member ID cannot be empty."
        )

    if len(cleaned_member_id) > 30:
        raise ValueError(
            "Member ID is too long."
        )

    return cleaned_member_id


def clean_menu_choice(
    choice: str
) -> str:
    """
    Remove unnecessary spaces from menu input.
    """

    return str(choice).strip()