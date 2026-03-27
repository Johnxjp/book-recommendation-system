"use client";

import type { ToolCall } from "@/lib/types";

const toolLabels: Record<string, string> = {
  get_reading_history: "Checking your reading history",
  get_book_details: "Looking up book details",
  web_search_tool: "Searching the web",
  web_extract_tool: "Reading a web page",
};

interface ToolCallIndicatorProps {
  toolCalls: ToolCall[];
}

export function ToolCallIndicator({ toolCalls }: ToolCallIndicatorProps) {
  const activeCalls = toolCalls.filter((tc) => tc.status === "calling");
  if (activeCalls.length === 0) return null;

  return (
    <div className="flex flex-col gap-1 mt-2">
      {activeCalls.map((tc, i) => (
        <div
          key={`${tc.name}-${i}`}
          className="flex items-center gap-2 text-xs text-stone"
        >
          <span className="inline-block w-3 h-3 rounded-full bg-sage-light animate-pulse" />
          {toolLabels[tc.name] || tc.name}...
        </div>
      ))}
    </div>
  );
}
