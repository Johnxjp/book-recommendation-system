from enum import StrEnum

from pydantic import BaseModel


class Shelf(StrEnum):
    READ = "read"
    TO_READ = "to-read"
    IS_READING = "is-reading"
    DID_NOT_FINISH = "did-not-finish"


class Book(BaseModel):
    """Canonical reference book from the catalog."""

    id: int | None = None
    title: str
    authors: list[str]
    isbn: str | None = None  # ISBN-10
    isbn13: str | None = None  # ISBN-13
    description: str | None = None
    genres: list[str] | None = None
    pages: int | None = None
    rating: float | None = None  # average Goodreads rating
    total_ratings: int | None = None  # number of ratings (popularity proxy)
    book_format: str | None = None
    goodreads_url: str | None = None
    goodreads_id: int | None = None
    cover_image_url: str | None = None

    def cover_url(self, size: str = "M") -> str | None:
        if self.cover_image_url:
            return self.cover_image_url
        isbn = self.isbn13 or self.isbn
        if isbn:
            return f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"
        return None


class UserBook(BaseModel):
    """A book in the user's personal library."""

    id: int | None = None
    book_id: int | None = None  # FK to books.id, NULL if unmatched
    goodreads_id: int | None = None
    title: str
    authors: list[str]
    isbn: str | None = None  # ISBN-13 format
    description: str | None = None
    genres: list[str] | None = None
    publisher: str | None = None
    pages: int | None = None
    year_published: int | None = None
    shelf: Shelf = Shelf.READ
    my_rating: int | None = None
    date_added: str | None = None
    date_read: str | None = None
