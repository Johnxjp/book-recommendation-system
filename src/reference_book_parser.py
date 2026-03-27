"""Parser for the GoodReads 100K books CSV dataset.

Handles quirks in the dataset:
- isbn13 field is in scientific notation (9.78E+12) which loses precision — unusable.
  Instead, derive isbn13 from isbn10 using the converter.
- authors as comma-separated within quotes
- genres as comma-separated with possible '...' truncation
- goodreads_id extracted from link field (/book/show/1001053.Title -> 1001053)
- pages: 0 or empty -> None
"""

import csv
import re

from src.models import Book
from src.utils import isbn10_to_13


def _parse_isbn13(raw: str) -> str | None:
    """Parse isbn13 field. Returns None if scientific notation (precision lost)."""
    raw = raw.strip()
    if not raw:
        return None
    # Scientific notation like 9.78E+12 loses precision — discard
    if "E" in raw.upper() or "." in raw:
        return None
    # Only accept if it's already a full 13-digit string
    digits = raw.strip()
    if len(digits) == 13 and digits.isdigit():
        return digits
    return None


def _parse_isbn(raw: str) -> str | None:
    """Clean ISBN-10 field."""
    raw = raw.strip()
    return raw if raw else None


def _parse_genres(raw: str) -> list[str] | None:
    """Parse comma-separated genres, stripping truncation markers."""
    raw = raw.strip()
    if not raw:
        return None
    genres = [g.strip().rstrip(".") for g in raw.split(",")]
    genres = [g for g in genres if g]
    return genres if genres else None


def _parse_goodreads_id(link: str) -> int | None:
    """Extract goodreads_id from a link like /book/show/1001053.Title."""
    match = re.search(r"/book/show/(\d+)", link)
    if match:
        return int(match.group(1))
    return None


def _parse_int(raw: str) -> int | None:
    """Parse an integer field, returning None for empty/zero."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        value = int(raw)
        return value if value > 0 else None
    except ValueError:
        return None


def _parse_float(raw: str) -> float | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_authors(raw: str) -> list[str]:
    """Parse authors field (comma-separated)."""
    return [a.strip() for a in raw.split(",") if a.strip()]


def parse_reference_books(csv_path: str) -> list[Book]:
    """Parse the GoodReads 100K CSV into a list of Book models."""
    books = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            isbn13 = _parse_isbn13(row.get("isbn13", ""))
            isbn = _parse_isbn(row.get("isbn", ""))
            # Derive isbn13 from isbn10 when the CSV field is unusable
            if not isbn13 and isbn and len(isbn) == 10:
                try:
                    isbn13 = isbn10_to_13(isbn)
                except Exception:
                    pass
            goodreads_id = _parse_goodreads_id(row.get("link", ""))
            pages = _parse_int(row.get("pages", ""))
            rating = _parse_float(row.get("rating", ""))
            total_ratings = _parse_int(row.get("totalratings", ""))
            genres = _parse_genres(row.get("genre", ""))
            authors = _parse_authors(row.get("author", ""))
            description = row.get("desc", "").strip() or None
            cover_image_url = row.get("img", "").strip() or None
            book_format = row.get("bookformat", "").strip() or None
            goodreads_url = row.get("link", "").strip() or None

            if not authors or not row.get("title", "").strip():
                continue

            books.append(
                Book(
                    title=row["title"].strip(),
                    authors=authors,
                    isbn=isbn,
                    isbn13=isbn13,
                    description=description,
                    genres=genres,
                    pages=pages,
                    rating=rating,
                    total_ratings=total_ratings,
                    book_format=book_format,
                    goodreads_url=goodreads_url,
                    goodreads_id=goodreads_id,
                    cover_image_url=cover_image_url,
                )
            )
    return books
