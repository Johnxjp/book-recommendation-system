"""
Tools for looking up the user's reading history.

Each tool is defined as an OpenAI-format schema + a handler function.
The handlers are created via make_handlers() which bakes in the db connection.
"""

import json
import sqlite3

from src.db import get_reference_book, get_user_book_by_goodreads_id, get_user_books


user_history_tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_reading_history",
            "description": (
                "Look up the user's reading history, optionally filtered by shelf. "
                "Use 'concise' format (default) to scan the full library efficiently — "
                "returns title, authors, genres, shelf, and rating only. "
                "Use 'detailed' format when you need full metadata for a smaller set — "
                "returns all fields including genres, pages, year published, ISBN, "
                "publisher, and dates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "shelf": {
                        "type": "string",
                        "enum": ["read", "to-read", "is-reading", "did-not-finish"],
                        "description": "Filter by shelf. Omit to get all books.",
                    },
                    "response_format": {
                        "type": "string",
                        "enum": ["concise", "detailed"],
                        "description": (
                            "Controls response detail level. "
                            "'concise': title, authors, shelf "
                            "'detailed': all fields including genres, rating, pages, "
                            "year published, ISBN, publisher, dates."
                        ),
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_book_details",
            "description": (
                "Get full details for a specific book by its Goodreads ID. "
                "Includes title, authors, ISBN, publisher, genres, pages, year published, "
                "the user's rating, shelf, and dates. If the book is linked to the "
                "reference catalog, also includes cover image URL and description."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "goodreads_id": {
                        "type": "integer",
                        "description": "The Goodreads ID of the book.",
                    }
                },
                "required": ["goodreads_id"],
            },
        },
    },
]


def make_handlers(conn: sqlite3.Connection) -> dict:
    """Return {name: callable} with the db connection baked in via closures."""

    def get_reading_history(
        shelf: str | None = None,
        response_format: str = "concise",
    ) -> str:
        """Return user's reading history, optionally filtered by shelf and detail level."""
        try:
            books = get_user_books(conn, shelf=shelf)
            if response_format == "concise":
                return json.dumps(
                    [
                        {
                            "title": b.title,
                            "authors": b.authors,
                            "genres": b.genres,
                            "shelf": b.shelf,
                            "my_rating": b.my_rating,
                        }
                        for b in books
                    ]
                )
            return json.dumps([b.model_dump() for b in books])
        except Exception as e:
            return json.dumps({"error": f"{type(e).__name__}: {e}"})

    def get_book_details(goodreads_id: int) -> str:
        """Return full details for a specific book by its Goodreads ID."""
        try:
            ub = get_user_book_by_goodreads_id(conn, goodreads_id)
            if not ub:
                return json.dumps({"error": "Book not found"})

            result = ub.model_dump()

            # Enrich with reference catalog data if linked
            if ub.book_id:
                ref = get_reference_book(conn, ub.book_id)
                if ref:
                    result["cover_image_url"] = ref.cover_url()
                    result["description"] = ref.description or ub.description
                    result["genres"] = ref.genres or ub.genres
                    result["average_rating"] = ref.rating

            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": f"{type(e).__name__}: {e}"})

    return {
        "get_reading_history": get_reading_history,
        "get_book_details": get_book_details,
    }
