import csv
from pathlib import Path

from src.queue_service import WaitlistService


def build_waitlist_summary(
    service: WaitlistService,
    books: dict[str, dict]
) -> list[dict]:
    """
    Create summary information for every active waitlist.
    """

    summary = []

    sorted_book_ids = sorted(
        service.waitlists,
        key=lambda value: (
            int(value)
            if value.isdigit()
            else value
        )
    )

    for book_id in sorted_book_ids:

        queue = service.get_waitlist(
            book_id
        )

        book = books.get(
            book_id,
            {}
        )

        if queue:
            next_member_id = queue[0].member_id
        else:
            next_member_id = ""

        summary.append(
            {
                "book_id": book_id,

                "title": book.get(
                    "title",
                    "Unknown"
                ),

                "author": book.get(
                    "author",
                    "Unknown"
                ),

                "waiting_count": len(queue),

                "next_member_id": next_member_id
            }
        )

    return summary


def export_waitlist_report_csv(
    output_file: str | Path,
    service: WaitlistService,
    books: dict[str, dict]
) -> Path:
    """
    Export complete waiting-list data to a CSV file.
    """

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "book_id",
                "title",
                "author",
                "position",
                "member_id",
                "requested_at"
            ]
        )

        writer.writeheader()

        sorted_book_ids = sorted(
            service.waitlists,
            key=lambda value: (
                int(value)
                if value.isdigit()
                else value
            )
        )

        for book_id in sorted_book_ids:

            book = books.get(
                book_id,
                {}
            )

            queue = service.get_waitlist(
                book_id
            )

            for position, entry in enumerate(
                queue,
                start=1
            ):
                writer.writerow(
                    {
                        "book_id": book_id,

                        "title": book.get(
                            "title",
                            "Unknown"
                        ),

                        "author": book.get(
                            "author",
                            "Unknown"
                        ),

                        "position": position,

                        "member_id": entry.member_id,

                        "requested_at": entry.requested_at
                    }
                )

    return output_path