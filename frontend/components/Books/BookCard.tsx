"use client";

import { useState } from "react";

interface BookCardProps {
  title: string;
  authors: string[];
  coverUrl: string | null;
  reason?: string;
  rating?: number | null;
  shelf?: string;
}

export function BookCard({
  title,
  authors,
  coverUrl,
  reason,
  rating,
  shelf,
}: BookCardProps) {
  const [imgError, setImgError] = useState(false);

  return (
    <div className="flex flex-col w-36">
      <div className="w-36 h-52 rounded-xl overflow-hidden bg-earth-light/30 shadow-sm flex-shrink-0">
        {coverUrl && !imgError ? (
          <img
            src={coverUrl}
            alt={title}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center p-3">
            <span className="text-xs text-stone text-center leading-tight">
              {title}
            </span>
          </div>
        )}
      </div>
      <div className="mt-2">
        <p className="text-sm font-medium text-charcoal leading-tight line-clamp-2">
          {title}
        </p>
        <p className="text-xs text-stone mt-0.5 line-clamp-1">
          {authors.join(", ")}
        </p>
        {rating && (
          <p className="text-xs text-gold mt-1">
            {"*".repeat(rating)}
          </p>
        )}
        {shelf && (
          <span className="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full bg-sage-light/30 text-sage">
            {shelf}
          </span>
        )}
        {reason && (
          <p className="text-xs text-stone mt-1.5 leading-relaxed line-clamp-3">
            {reason}
          </p>
        )}
      </div>
    </div>
  );
}
