"use client";

import { useState, useEffect } from "react";
import type { UserBook, Shelf } from "@/lib/types";
import { fetchUserBooks } from "@/lib/api";
import { ShelfTabs } from "@/components/Books/ShelfTabs";
import { ShelfBookList } from "@/components/Books/ShelfBookList";

export default function LibraryPage() {
  const [books, setBooks] = useState<UserBook[]>([]);
  const [activeShelf, setActiveShelf] = useState<Shelf | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchUserBooks(activeShelf ?? undefined)
      .then(setBooks)
      .catch(() => setBooks([]))
      .finally(() => setLoading(false));
  }, [activeShelf]);

  return (
    <div className="flex-1 flex flex-col h-screen">
      <div className="px-6 py-4 border-b border-earth-light/40">
        <h2 className="font-serif text-lg text-charcoal">My Library</h2>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-6xl mx-auto">
          <ShelfTabs active={activeShelf} onSelect={setActiveShelf} />

          <div className="mt-6">
            {loading ? (
              <p className="text-sm text-stone py-8 text-center">Loading...</p>
            ) : (
              <ShelfBookList books={books} />
            )}
          </div>

          <p className="text-xs text-stone mt-6">
            {books.length} {books.length === 1 ? "book" : "books"}
          </p>
        </div>
      </div>
    </div>
  );
}
