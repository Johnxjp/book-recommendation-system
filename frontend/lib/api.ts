import type { UserBook, Shelf } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchUserBooks(shelf?: Shelf): Promise<UserBook[]> {
  const params = shelf ? `?shelf=${shelf}` : "";
  const res = await fetch(`${API_BASE}/api/books/user${params}`);
  if (!res.ok) throw new Error("Failed to fetch books");
  return res.json();
}

export async function fetchUserBook(bookId: string): Promise<UserBook | null> {
  const res = await fetch(`${API_BASE}/api/books/user/${bookId}`);
  if (!res.ok) throw new Error("Failed to fetch book");
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/api/sessions/${sessionId}`, { method: "DELETE" });
}

export function chatUrl(): string {
  return `${API_BASE}/api/chat`;
}
