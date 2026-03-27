"""FastAPI application — entry point for the book recommendation API."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes import books, chat
from server.sessions import SessionStore
from src.db import get_connection, init_db

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: open DB connection
    db_path = os.getenv("DB_PATH", "data/books.db")
    conn = get_connection(db_path)
    init_db(conn)
    app.state.db_conn = conn
    app.state.session_store = SessionStore(conn)
    yield
    # Shutdown: close DB connection
    conn.close()


app = FastAPI(title="Book Recommendation API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(books.router)


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    deleted = app.state.session_store.delete(session_id)
    return {"deleted": deleted}
