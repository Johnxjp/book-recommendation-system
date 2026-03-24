import json
import sqlite3
from pathlib import Path

from src.models import Book, Shelf, UserBook


def get_connection(db_path: str | Path) -> sqlite3.Connection:
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT NOT NULL,           -- JSON list
            isbn TEXT,                       -- ISBN-10
            isbn13 TEXT,                     -- ISBN-13
            description TEXT,
            genres TEXT,                     -- JSON list
            pages INTEGER,
            rating REAL,                     -- average Goodreads rating
            total_ratings INTEGER,           -- number of ratings (popularity proxy)
            book_format TEXT,
            goodreads_url TEXT,
            goodreads_id INTEGER,
            cover_image_url TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
        CREATE INDEX IF NOT EXISTS idx_books_isbn13 ON books(isbn13);
        CREATE INDEX IF NOT EXISTS idx_books_goodreads_id ON books(goodreads_id);
        CREATE INDEX IF NOT EXISTS idx_books_popularity ON books(total_ratings DESC);

        CREATE TABLE IF NOT EXISTS user_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER REFERENCES books(id),  -- NULL if unmatched
            goodreads_id INTEGER,
            title TEXT NOT NULL,
            authors TEXT NOT NULL,                  -- JSON list
            isbn TEXT,                              -- ISBN-13 format
            description TEXT,
            genres TEXT,                            -- JSON list
            publisher TEXT,
            pages INTEGER,
            year_published INTEGER,
            shelf TEXT NOT NULL DEFAULT 'read',
            my_rating INTEGER,
            date_added TEXT,
            date_read TEXT,
            CHECK (my_rating BETWEEN 1 AND 5 OR my_rating IS NULL),
            CHECK (shelf IN ('read', 'to-read', 'is-reading', 'did-not-finish'))
        );

        CREATE INDEX IF NOT EXISTS idx_user_books_book_id ON user_books(book_id);
        CREATE INDEX IF NOT EXISTS idx_user_books_isbn ON user_books(isbn);
    """
    )


# ── Reference book CRUD ──────────────────────────────────────────────


def bulk_insert_books(conn: sqlite3.Connection, books: list[Book]) -> int:
    """Insert reference books in bulk. Returns number inserted."""
    rows = [
        (
            b.title,
            json.dumps(b.authors),
            b.isbn,
            b.isbn13,
            b.description,
            json.dumps(b.genres) if b.genres else None,
            b.pages,
            b.rating,
            b.total_ratings,
            b.book_format,
            b.goodreads_url,
            b.goodreads_id,
            b.cover_image_url,
        )
        for b in books
    ]
    conn.executemany(
        """
        INSERT INTO books (title, authors, isbn, isbn13, description, genres, pages,
                           rating, total_ratings, book_format, goodreads_url,
                           goodreads_id, cover_image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def get_popular_books(
    conn: sqlite3.Connection, limit: int = 50, offset: int = 0
) -> list[Book]:
    """Return books ordered by popularity (total_ratings DESC)."""
    rows = conn.execute(
        "SELECT * FROM books ORDER BY total_ratings DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    return [_row_to_book(row) for row in rows]


def search_books(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[Book]:
    """Search reference books by title (LIKE match)."""
    rows = conn.execute(
        "SELECT * FROM books WHERE title LIKE ? ORDER BY total_ratings DESC LIMIT ?",
        (f"%{query}%", limit),
    ).fetchall()
    return [_row_to_book(row) for row in rows]


def get_reference_book(conn: sqlite3.Connection, book_id: int) -> Book | None:
    """Get a reference book by its id."""
    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    return _row_to_book(row) if row else None


# ── User book CRUD ───────────────────────────────────────────────────


def upsert_user_book(conn: sqlite3.Connection, ub: UserBook) -> None:
    """Insert or update a user book. Attempts to match against reference catalog."""
    # Try to match against reference catalog by ISBN or goodreads_id
    book_id = ub.book_id
    if book_id is None and ub.isbn:
        row = conn.execute(
            "SELECT id FROM books WHERE isbn13 = ? OR isbn = ?",
            (ub.isbn, ub.isbn),
        ).fetchone()
        if row:
            book_id = row["id"]

    if book_id is None and ub.goodreads_id:
        row = conn.execute(
            "SELECT id FROM books WHERE goodreads_id = ?",
            (ub.goodreads_id,),
        ).fetchone()
        if row:
            book_id = row["id"]

    # If matched, pull genres/description from reference book
    genres = json.dumps(ub.genres) if ub.genres else None
    description = ub.description
    if book_id is not None:
        ref = conn.execute(
            "SELECT genres, description FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        if ref:
            if not genres and ref["genres"]:
                genres = ref["genres"]
            if not description and ref["description"]:
                description = ref["description"]

    conn.execute(
        """
        INSERT INTO user_books (book_id, goodreads_id, title, authors, isbn,
                                description, genres, publisher, pages, year_published,
                                shelf, my_rating, date_added, date_read)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            book_id=excluded.book_id,
            title=excluded.title,
            authors=excluded.authors,
            isbn=excluded.isbn,
            description=excluded.description,
            genres=excluded.genres,
            publisher=excluded.publisher,
            pages=excluded.pages,
            year_published=excluded.year_published,
            shelf=excluded.shelf,
            my_rating=excluded.my_rating,
            date_added=excluded.date_added,
            date_read=excluded.date_read
        """,
        (
            book_id,
            ub.goodreads_id,
            ub.title,
            json.dumps(ub.authors),
            ub.isbn,
            description,
            genres,
            ub.publisher,
            ub.pages,
            ub.year_published,
            ub.shelf,
            ub.my_rating,
            ub.date_added,
            ub.date_read,
        ),
    )


def get_user_books(
    conn: sqlite3.Connection, shelf: Shelf | None = None
) -> list[UserBook]:
    query = "SELECT * FROM user_books"
    params: list = []
    if shelf:
        query += " WHERE shelf = ?"
        params.append(shelf)

    rows = conn.execute(query, params).fetchall()
    return [_row_to_user_book(row) for row in rows]


def get_user_book(conn: sqlite3.Connection, user_book_id: int) -> UserBook | None:
    """Get a user book by its id."""
    row = conn.execute(
        "SELECT * FROM user_books WHERE id = ?", (user_book_id,)
    ).fetchone()
    return _row_to_user_book(row) if row else None


def get_user_book_by_goodreads_id(
    conn: sqlite3.Connection, goodreads_id: int
) -> UserBook | None:
    """Get a user book by its Goodreads ID."""
    row = conn.execute(
        "SELECT * FROM user_books WHERE goodreads_id = ?", (goodreads_id,)
    ).fetchone()
    return _row_to_user_book(row) if row else None


def get_unmatched_user_books(conn: sqlite3.Connection) -> list[UserBook]:
    """Return user books where book_id IS NULL (not yet matched to reference catalog)."""
    rows = conn.execute("SELECT * FROM user_books WHERE book_id IS NULL").fetchall()
    return [_row_to_user_book(row) for row in rows]


def link_user_books(conn: sqlite3.Connection) -> int:
    """Attempt to match unmatched user_books to books by ISBN. Returns count linked."""
    unmatched = conn.execute(
        "SELECT id, isbn, goodreads_id FROM user_books WHERE book_id IS NULL"
    ).fetchall()

    linked = 0
    for row in unmatched:
        book_row = None
        if row["isbn"]:
            book_row = conn.execute(
                "SELECT id FROM books WHERE isbn13 = ? OR isbn = ?",
                (row["isbn"], row["isbn"]),
            ).fetchone()
        if not book_row and row["goodreads_id"]:
            book_row = conn.execute(
                "SELECT id FROM books WHERE goodreads_id = ?",
                (row["goodreads_id"],),
            ).fetchone()
        if book_row:
            conn.execute(
                "UPDATE user_books SET book_id = ? WHERE id = ?",
                (book_row["id"], row["id"]),
            )
            linked += 1

    conn.commit()
    return linked


# ── Row converters ───────────────────────────────────────────────────


def _row_to_book(row: sqlite3.Row) -> Book:
    return Book(
        id=row["id"],
        title=row["title"],
        authors=json.loads(row["authors"]),
        isbn=row["isbn"],
        isbn13=row["isbn13"],
        description=row["description"],
        genres=json.loads(row["genres"]) if row["genres"] else None,
        pages=row["pages"],
        rating=row["rating"],
        total_ratings=row["total_ratings"],
        book_format=row["book_format"],
        goodreads_url=row["goodreads_url"],
        goodreads_id=row["goodreads_id"],
        cover_image_url=row["cover_image_url"],
    )


def _row_to_user_book(row: sqlite3.Row) -> UserBook:
    return UserBook(
        id=row["id"],
        book_id=row["book_id"],
        goodreads_id=row["goodreads_id"],
        title=row["title"],
        authors=json.loads(row["authors"]),
        isbn=row["isbn"],
        description=row["description"],
        genres=json.loads(row["genres"]) if row["genres"] else None,
        publisher=row["publisher"],
        pages=row["pages"],
        year_published=row["year_published"],
        shelf=row["shelf"],
        my_rating=row["my_rating"],
        date_added=row["date_added"],
        date_read=row["date_read"],
    )
