"""Seed the books table from the GoodReads 100K Kaggle dataset.

Usage: uv run python -m src.seed_reference_books
"""

from pathlib import Path

from src.db import bulk_insert_books, get_connection, init_db
from src.reference_book_parser import parse_reference_books

CSV_PATH = Path("data/GoodReads_100k_books.csv")
DB_PATH = Path("data/books.db")
BATCH_SIZE = 5000


def seed():
    print(f"Parsing {CSV_PATH}...")
    books = parse_reference_books(str(CSV_PATH))
    print(f"  Parsed {len(books)} books")

    # Deduplicate by isbn13 (prefer first occurrence), fall back to goodreads_id
    seen_isbn13: set[str] = set()
    seen_gr_id: set[int] = set()
    unique = []
    for b in books:
        if b.isbn13 and b.isbn13 in seen_isbn13:
            continue
        if b.goodreads_id and b.goodreads_id in seen_gr_id:
            continue
        if b.isbn13:
            seen_isbn13.add(b.isbn13)
        if b.goodreads_id:
            seen_gr_id.add(b.goodreads_id)
        unique.append(b)

    print(f"  After dedup: {len(unique)} unique books")

    conn = get_connection(DB_PATH)
    init_db(conn)

    # Bulk insert in batches
    total = 0
    for i in range(0, len(unique), BATCH_SIZE):
        batch = unique[i : i + BATCH_SIZE]
        inserted = bulk_insert_books(conn, batch)
        total += inserted
        print(f"  Inserted batch {i // BATCH_SIZE + 1}: {inserted} books")

    # Summary stats
    count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    with_genres = conn.execute(
        "SELECT COUNT(*) FROM books WHERE genres IS NOT NULL"
    ).fetchone()[0]
    with_desc = conn.execute(
        "SELECT COUNT(*) FROM books WHERE description IS NOT NULL"
    ).fetchone()[0]
    with_cover = conn.execute(
        "SELECT COUNT(*) FROM books WHERE cover_image_url IS NOT NULL"
    ).fetchone()[0]

    print("\nSummary:")
    print(f"  Total books in DB: {count}")
    print(f"  With genres: {with_genres} ({with_genres * 100 // count}%)")
    print(f"  With description: {with_desc} ({with_desc * 100 // count}%)")
    print(f"  With cover image: {with_cover} ({with_cover * 100 // count}%)")

    # Top 5 by popularity
    top = conn.execute(
        "SELECT title, total_ratings FROM books ORDER BY total_ratings DESC LIMIT 5"
    ).fetchall()
    print("\nTop 5 by popularity:")
    for row in top:
        print(f"  {row[0]} ({row[1]} ratings)")

    conn.close()


if __name__ == "__main__":
    seed()
