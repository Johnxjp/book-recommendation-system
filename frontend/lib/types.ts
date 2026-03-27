export interface BookRecommendation {
  title: string;
  authors: string[];
  cover_url: string | null;
  reason: string;
}

export interface ToolCall {
  name: string;
  status: "calling" | "complete";
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  recommendations?: BookRecommendation[];
  toolCalls?: ToolCall[];
}

export interface UserBook {
  id: string | null;
  book_id: string | null;
  goodreads_id: number | null;
  title: string;
  authors: string[];
  isbn: string | null;
  description: string | null;
  genres: string[] | null;
  publisher: string | null;
  pages: number | null;
  year_published: number | null;
  shelf: string;
  my_rating: number | null;
  date_added: string | null;
  date_read: string | null;
  cover_url: string | null;
}

export type Shelf = "read" | "to-read" | "is-reading" | "did-not-finish";
