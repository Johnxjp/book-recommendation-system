import json
import sqlite3
from pathlib import Path

from src.models import Book, Shelf, UserBook


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Check tables exist"""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS books (
            goodreads_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            authors TEXT NOT NULL,          -- JSON list
            isbn TEXT,                     -- ISBN-13 format
            publisher TEXT,
            genres TEXT,                    -- JSON list
            pages INTEGER,
            year_published INTEGER
        );

        CREATE TABLE IF NOT EXISTS user_books (
            goodreads_id INTEGER PRIMARY KEY REFERENCES books(goodreads_id),
            shelf TEXT NOT NULL DEFAULT 'read',
            my_rating INTEGER,
            date_added TEXT,
            date_read TEXT,
            CHECK (my_rating BETWEEN 1 AND 5 OR my_rating IS NULL),
            CHECK (shelf IN ('read', 'to-read', 'is-reading', 'did-not-finish'))
        );
    """
    )


def upsert_user_book(conn: sqlite3.Connection, ub: UserBook) -> None:
    conn.execute(
        """
        INSERT INTO books (goodreads_id, title, authors, isbn, publisher, genres, pages, year_published)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(goodreads_id) DO UPDATE SET
            title=excluded.title,
            authors=excluded.authors,
            isbn=excluded.isbn,
            publisher=excluded.publisher,
            genres=excluded.genres,
            pages=excluded.pages,
            year_published=excluded.year_published
        """,
        (
            ub.book.goodreads_id,
            ub.book.title,
            json.dumps(ub.book.authors),
            ub.book.isbn,
            ub.book.publisher,
            json.dumps(ub.book.genres) if ub.book.genres else None,
            ub.book.pages,
            ub.book.year_published,
        ),
    )
    conn.execute(
        """
        INSERT INTO user_books (goodreads_id, shelf, my_rating, date_added, date_read)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(goodreads_id) DO UPDATE SET
            shelf=excluded.shelf,
            my_rating=excluded.my_rating,
            date_added=excluded.date_added,
            date_read=excluded.date_read
        """,
        (ub.book.goodreads_id, ub.shelf, ub.my_rating, ub.date_added, ub.date_read),
    )


def get_user_books(conn: sqlite3.Connection, shelf: Shelf | None = None) -> list[UserBook]:
    query = """
        SELECT b.*, ub.shelf, ub.my_rating, ub.date_added, ub.date_read
        FROM books b JOIN user_books ub ON b.goodreads_id = ub.goodreads_id
    """
    params: list = []
    if shelf:
        query += " WHERE ub.shelf = ?"
        params.append(shelf)

    rows = conn.execute(query, params).fetchall()
    return [_row_to_user_book(row) for row in rows]


def get_book(conn: sqlite3.Connection, goodreads_id: int) -> UserBook | None:
    row = conn.execute(
        """
        SELECT b.*, ub.shelf, ub.my_rating, ub.date_added, ub.date_read
        FROM books b JOIN user_books ub ON b.goodreads_id = ub.goodreads_id
        WHERE b.goodreads_id = ?
        """,
        (goodreads_id,),
    ).fetchone()
    return _row_to_user_book(row) if row else None


def _row_to_user_book(row: sqlite3.Row) -> UserBook:
    return UserBook(
        book=Book(
            goodreads_id=row["goodreads_id"],
            title=row["title"],
            authors=json.loads(row["authors"]),
            isbn=row["isbn"],
            publisher=row["publisher"],
            genres=json.loads(row["genres"]) if row["genres"] else None,
            pages=row["pages"],
            year_published=row["year_published"],
        ),
        shelf=row["shelf"],
        my_rating=row["my_rating"],
        date_added=row["date_added"],
        date_read=row["date_read"],
    )
