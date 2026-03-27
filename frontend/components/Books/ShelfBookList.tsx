"use client";

import type { UserBook } from "@/lib/types";
import { BookCard } from "./BookCard";

interface ShelfBookListProps {
  books: UserBook[];
}

export function ShelfBookList({ books }: ShelfBookListProps) {
  if (books.length === 0) {
    return (
      <p className="text-sm text-stone py-8 text-center">
        No books on this shelf yet.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
      {books.map((book) => (
        <BookCard
          key={book.id || book.title}
          title={book.title}
          authors={book.authors}
          coverUrl={book.cover_url}
          rating={book.my_rating}
          shelf={book.shelf}
        />
      ))}
    </div>
  );
}
