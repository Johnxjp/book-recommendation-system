"""API request/response Pydantic models."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class UserBookResponse(BaseModel):
    id: str | None = None
    book_id: str | None = None
    goodreads_id: int | None = None
    title: str
    authors: list[str]
    isbn: str | None = None
    description: str | None = None
    genres: list[str] | None = None
    publisher: str | None = None
    pages: int | None = None
    year_published: int | None = None
    shelf: str
    my_rating: int | None = None
    date_added: str | None = None
    date_read: str | None = None
    cover_url: str | None = None


class BookResponse(BaseModel):
    id: str | None = None
    title: str
    authors: list[str]
    isbn: str | None = None
    isbn13: str | None = None
    description: str | None = None
    genres: list[str] | None = None
    pages: int | None = None
    rating: float | None = None
    total_ratings: int | None = None
    cover_url: str | None = None
