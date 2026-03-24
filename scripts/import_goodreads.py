"""Import a Goodreads library export CSV into the local SQLite database.

Usage:
    uv run python scripts/import_goodreads.py <csv_path>
"""

import os
import sys

from dotenv import load_dotenv

from src.db import get_connection, init_db, upsert_user_book
from src.goodreads_parser import parse_goodreads

load_dotenv()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/import_goodreads.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    db_path = os.environ["DB_PATH"]

    user_books = parse_goodreads(csv_path)
    print(f"Parsed {len(user_books)} books from {csv_path}")

    conn = get_connection(db_path)
    init_db(conn)

    for ub in user_books:
        upsert_user_book(conn, ub)
    conn.commit()

    # Summary
    counts = conn.execute(
        "SELECT shelf, COUNT(*) as n FROM user_books GROUP BY shelf ORDER BY n DESC"
    ).fetchall()
    for row in counts:
        print(f"  {row['shelf']}: {row['n']}")

    total = conn.execute("SELECT COUNT(*) FROM user_books").fetchone()[0]
    matched = conn.execute(
        "SELECT COUNT(*) FROM user_books WHERE book_id IS NOT NULL"
    ).fetchone()[0]
    print(f"\nMatching: {matched}/{total} linked to reference catalog")
    print(f"Unmatched: {total - matched} (enrichment queue)")

    print(f"Imported to {db_path}")
    conn.close()


if __name__ == "__main__":
    main()
