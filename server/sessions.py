"""In-memory session store for chat conversations."""

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field

from server.streaming import StreamingAgent
from src.prompts.base import build_system_prompt
from src.tools.user_reading_history import make_handlers as make_history_handlers
from src.tools.user_reading_history import user_history_tools_schema
from src.tools.web_tools import (
    web_extract_tool,
    web_search_tool,
    web_tools_schema,
)

SESSION_TTL_SECONDS = 2 * 60 * 60  # 2 hours


@dataclass
class Session:
    agent: StreamingAgent
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)


class SessionStore:
    def __init__(self, conn: sqlite3.Connection):
        self._sessions: dict[str, Session] = {}
        self._conn = conn

    def get_or_create(self, session_id: str | None) -> tuple[str, StreamingAgent]:
        """Get existing session or create a new one. Returns (session_id, agent)."""
        self._cleanup_expired()

        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            session.last_accessed = time.time()
            return session_id, session.agent

        # Create new session
        if not session_id:
            session_id = str(uuid.uuid4())

        tools = user_history_tools_schema + web_tools_schema
        history_handlers = make_history_handlers(self._conn)
        tool_handlers = {
            **history_handlers,
            "web_search_tool": web_search_tool,
            "web_extract_tool": web_extract_tool,
        }

        reading_context = _build_reading_context(self._conn)
        agent = StreamingAgent(
            system_prompt=build_system_prompt(reading_context),
            tools=tools,
            tool_handlers=tool_handlers,
        )

        self._sessions[session_id] = Session(agent=agent)
        return session_id, agent

    def delete(self, session_id: str) -> bool:
        """Delete a session. Returns True if it existed."""
        return self._sessions.pop(session_id, None) is not None

    def _cleanup_expired(self):
        now = time.time()
        expired = [
            sid
            for sid, session in self._sessions.items()
            if now - session.last_accessed > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            del self._sessions[sid]


def _build_reading_context(conn: sqlite3.Connection) -> str:
    """Build a reading snapshot string from the user's current and recent books."""
    sections = []

    # Currently reading
    reading_rows = conn.execute(
        "SELECT title, authors, genres FROM user_books WHERE shelf = 'is-reading'"
    ).fetchall()
    if reading_rows:
        lines = []
        for row in reading_rows:
            authors = ", ".join(json.loads(row["authors"]))
            genres = json.loads(row["genres"]) if row["genres"] else []
            genre_str = f" ({', '.join(genres[:3])})" if genres else ""
            lines.append(f"- *{row['title']}* by {authors}{genre_str}")
        sections.append("**Currently reading:**\n" + "\n".join(lines))

    # Last 5 books read (most recently read first)
    read_rows = conn.execute(
        "SELECT title, authors, genres, my_rating FROM user_books "
        "WHERE shelf = 'read' ORDER BY date_read DESC LIMIT 5"
    ).fetchall()
    if read_rows:
        lines = []
        for row in read_rows:
            authors = ", ".join(json.loads(row["authors"]))
            genres = json.loads(row["genres"]) if row["genres"] else []
            genre_str = f" ({', '.join(genres[:3])})" if genres else ""
            rating = f" — rated {row['my_rating']}/5" if row["my_rating"] else ""
            lines.append(f"- *{row['title']}* by {authors}{genre_str}{rating}")
        sections.append("**Recently read:**\n" + "\n".join(lines))

    return "\n\n".join(sections)
