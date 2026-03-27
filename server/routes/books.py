"""REST endpoints for books and user library."""

from fastapi import APIRouter, Query, Request

from server.schemas import BookResponse, UserBookResponse
from src.db import get_user_book, get_user_books, search_books
from src.models import Shelf

router = APIRouter()


def _user_book_to_response(ub) -> UserBookResponse:
    isbn = ub.isbn
    cover_url = None
    if isbn:
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
    return UserBookResponse(
        id=ub.id,
        book_id=ub.book_id,
        goodreads_id=ub.goodreads_id,
        title=ub.title,
        authors=ub.authors,
        isbn=ub.isbn,
        description=ub.description,
        genres=ub.genres,
        publisher=ub.publisher,
        pages=ub.pages,
        year_published=ub.year_published,
        shelf=ub.shelf,
        my_rating=ub.my_rating,
        date_added=ub.date_added,
        date_read=ub.date_read,
        cover_url=cover_url,
    )


def _book_to_response(b) -> BookResponse:
    return BookResponse(
        id=b.id,
        title=b.title,
        authors=b.authors,
        isbn=b.isbn,
        isbn13=b.isbn13,
        description=b.description,
        genres=b.genres,
        pages=b.pages,
        rating=b.rating,
        total_ratings=b.total_ratings,
        cover_url=b.cover_url(),
    )


@router.get("/api/books/user", response_model=list[UserBookResponse])
async def list_user_books(
    request: Request,
    shelf: Shelf | None = Query(None),
):
    conn = request.app.state.db_conn
    books = get_user_books(conn, shelf=shelf)
    return [_user_book_to_response(b) for b in books]


@router.get("/api/books/user/{book_id}", response_model=UserBookResponse | None)
async def get_single_user_book(request: Request, book_id: int):
    conn = request.app.state.db_conn
    book = get_user_book(conn, book_id)
    if not book:
        return None
    return _user_book_to_response(book)


@router.get("/api/books/search", response_model=list[BookResponse])
async def search_catalog(
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
):
    conn = request.app.state.db_conn
    books = search_books(conn, q, limit=limit)
    return [_book_to_response(b) for b in books]
