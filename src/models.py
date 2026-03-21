from enum import StrEnum

from pydantic import BaseModel


class Shelf(StrEnum):
    READ = "read"
    TO_READ = "to-read"
    IS_READING = "is-reading"
    DID_NOT_FINISH = "did-not-finish"


class Book(BaseModel):
    goodreads_id: int
    title: str
    authors: list[str]
    isbn: str | None = None  # ISBN-13 format
    publisher: str | None = None
    genres: list[str] | None = None
    pages: int | None = None
    year_published: int | None = None


class UserBook(BaseModel):
    book: Book
    shelf: Shelf = Shelf.READ
    my_rating: int | None = None
    date_added: str | None = None
    date_read: str | None = None
