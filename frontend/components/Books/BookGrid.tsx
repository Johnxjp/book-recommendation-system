import type { BookRecommendation } from "@/lib/types";
import { BookCard } from "./BookCard";

interface BookGridProps {
  recommendations: BookRecommendation[];
}

export function BookGrid({ recommendations }: BookGridProps) {
  if (recommendations.length === 0) return null;

  return (
    <div className="flex gap-4 overflow-x-auto py-3 mt-2">
      {recommendations.map((rec, i) => (
        <BookCard
          key={`${rec.title}-${i}`}
          title={rec.title}
          authors={rec.authors}
          coverUrl={rec.cover_url}
          reason={rec.reason}
        />
      ))}
    </div>
  );
}
