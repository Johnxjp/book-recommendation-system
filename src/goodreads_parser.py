import csv

from src.models import UserBook
from src.utils import isbn10_to_13


def _to_iso_date(raw: str) -> str | None:
    """Convert YYYY/MM/DD to YYYY-MM-DD."""
    cleaned = raw.strip()
    return cleaned.replace("/", "-") if cleaned else None


def _clean_isbn(raw: str) -> str | None:
    """Goodreads wraps ISBNs like =\"0312278497\" — strip that."""
    cleaned = raw.strip().strip('="')
    return cleaned if cleaned else None


def _resolve_isbn(row: dict) -> str | None:
    """Return ISBN-13, converting from ISBN-10 if needed."""
    isbn13 = _clean_isbn(row.get("ISBN13", ""))
    if isbn13:
        return isbn13
    isbn10 = _clean_isbn(row.get("ISBN", ""))
    if isbn10:
        return isbn10_to_13(isbn10)
    return None


def parse_goodreads(csv_path: str) -> list[UserBook]:
    books = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            authors = [row["Author"]]
            if row.get("Additional Authors", "").strip():
                authors.extend(
                    a.strip() for a in row["Additional Authors"].split(",") if a.strip()
                )

            rating = int(row["My Rating"])
            pages = row.get("Number of Pages", "").strip()
            year = row.get("Year Published", "").strip()
            raw_shelf = row.get("Exclusive Shelf", "").strip()
            shelf = {"currently-reading": "is-reading"}.get(
                raw_shelf, raw_shelf
            ) or "read"
            publisher = row.get("Publisher", "").strip() or None

            books.append(
                UserBook(
                    goodreads_id=int(row["Book Id"]),
                    title=row["Title"],
                    authors=authors,
                    isbn=_resolve_isbn(row),
                    publisher=publisher,
                    genres=None,
                    pages=int(pages) if pages else None,
                    year_published=int(year) if year else None,
                    shelf=shelf,
                    my_rating=rating if rating > 0 else None,
                    date_added=_to_iso_date(row.get("Date Added", "")),
                    date_read=_to_iso_date(row.get("Date Read", "")),
                )
            )
    return books
