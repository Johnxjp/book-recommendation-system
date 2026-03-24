"""Parser for the GoodReads 100K Kaggle dataset (GoodReads_100k_books.csv)."""

import csv
import re

from src.models import Book


def _parse_isbn13(raw: str) -> str | None:
    """Parse isbn13, discarding scientific notation which loses precision."""
    raw = raw.strip()
    if not raw:
        return None
    # Scientific notation (e.g. 9.78E+12) loses lower digits — discard
    if "E" in raw or "e" in raw:
        return None
    # Already a plain number string
    digits = raw.replace("-", "").replace(" ", "")
    if digits.isdigit() and len(digits) == 13:
        return digits
    return None


def _parse_genres(raw: str) -> list[str] | None:
    """Parse comma-separated genre string, stripping truncation markers."""
    raw = raw.strip()
    if not raw:
        return None
    genres = [g.strip().rstrip(".") for g in raw.split(",") if g.strip()]
    # Remove empty strings from truncated entries
    genres = [g for g in genres if g]
    return genres if genres else None


def _extract_goodreads_id(link: str) -> int | None:
    """Extract goodreads_id from link like '/book/show/1001053.Title'."""
    match = re.search(r"/book/show/(\d+)", link)
    if match:
        return int(match.group(1))
    return None


def _parse_int(raw: str) -> int | None:
    """Parse int, returning None for empty/zero/invalid."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        val = int(raw)
        return val if val > 0 else None
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


def parse_reference_books(csv_path: str) -> list[Book]:
    """Parse GoodReads 100K CSV into a list of Book models."""
    books = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            authors = [a.strip() for a in row["author"].split(",") if a.strip()]
            if not authors:
                continue

            title = row.get("title", "").strip()
            if not title:
                continue

            isbn = row.get("isbn", "").strip() or None
            isbn13 = _parse_isbn13(row.get("isbn13", ""))

            books.append(
                Book(
                    title=title,
                    authors=authors,
                    isbn=isbn,
                    isbn13=isbn13,
                    description=row.get("desc", "").strip() or None,
                    genres=_parse_genres(row.get("genre", "")),
                    pages=_parse_int(row.get("pages", "")),
                    rating=_parse_float(row.get("rating", "")),
                    total_ratings=_parse_int(row.get("totalratings", "")),
                    book_format=row.get("bookformat", "").strip() or None,
                    goodreads_url=row.get("link", "").strip() or None,
                    goodreads_id=_extract_goodreads_id(row.get("link", "")),
                    cover_image_url=row.get("img", "").strip() or None,
                )
            )
    return books
