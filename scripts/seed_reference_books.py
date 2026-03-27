"""Seed the reference books table from the GoodReads 100K CSV.

Usage:
    uv run python scripts/seed_reference_books.py
"""

import os

from dotenv import load_dotenv

from src.db import bulk_insert_books, get_connection, init_db
from src.reference_book_parser import parse_reference_books

load_dotenv()

CSV_PATH = "data/GoodReads_100k_books.csv"
BATCH_SIZE = 5000


def main() -> None:
    db_path = os.environ["DB_PATH"]

    print(f"Parsing {CSV_PATH}...")
    books = parse_reference_books(CSV_PATH)
    print(f"Parsed {len(books)} books")

    # Deduplicate by goodreads_id (most reliable), then isbn13, then isbn
    seen: set[str] = set()
    unique_books = []
    for book in books:
        key = (
            (str(book.goodreads_id) if book.goodreads_id else None)
            or book.isbn13
            or book.isbn
        )
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        unique_books.append(book)

    print(f"After deduplication: {len(unique_books)} books")

    conn = get_connection(db_path)
    init_db(conn)

    # Check if books table already has data
    existing = conn.execute("SELECT COUNT(*) as n FROM books").fetchone()["n"]
    if existing > 0:
        print(f"Books table already has {existing} rows. Skipping seed.")
        print("To re-seed, delete the database and run again.")
        conn.close()
        return

    # Bulk insert in batches
    total_inserted = 0
    for i in range(0, len(unique_books), BATCH_SIZE):
        batch = unique_books[i : i + BATCH_SIZE]
        inserted = bulk_insert_books(conn, batch)
        total_inserted += inserted
        print(f"  Inserted batch {i // BATCH_SIZE + 1}: {inserted} books")

    conn.commit()

    # Summary stats
    total = conn.execute("SELECT COUNT(*) as n FROM books").fetchone()["n"]
    with_genres = conn.execute(
        "SELECT COUNT(*) as n FROM books WHERE genres IS NOT NULL"
    ).fetchone()["n"]
    with_desc = conn.execute(
        "SELECT COUNT(*) as n FROM books WHERE description IS NOT NULL"
    ).fetchone()["n"]
    with_cover = conn.execute(
        "SELECT COUNT(*) as n FROM books WHERE cover_image_url IS NOT NULL"
    ).fetchone()["n"]

    print(f"\nSeeded {total} reference books into {db_path}")
    print(f"  With genres: {with_genres} ({with_genres * 100 // total}%)")
    print(f"  With description: {with_desc} ({with_desc * 100 // total}%)")
    print(f"  With cover URL: {with_cover} ({with_cover * 100 // total}%)")

    # Top 5 most popular
    top = conn.execute(
        "SELECT title, total_ratings FROM books ORDER BY total_ratings DESC LIMIT 5"
    ).fetchall()
    print("\nTop 5 by ratings:")
    for row in top:
        print(f"  {row['title']} ({row['total_ratings']} ratings)")

    conn.close()


if __name__ == "__main__":
    main()
