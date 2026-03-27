"use client";

import ReactMarkdown from "react-markdown";
import type { Message } from "@/lib/types";
import { ToolCallIndicator } from "./ToolCallIndicator";
import { BookGrid } from "@/components/Books/BookGrid";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl rounded-2xl px-5 py-3.5 ${
          isUser
            ? "bg-sage text-white"
            : "bg-warm-white shadow-sm"
        }`}
      >
        <div className={`text-sm leading-relaxed ${isUser ? "text-white" : "text-charcoal"}`}>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {message.toolCalls && message.toolCalls.length > 0 && (
          <ToolCallIndicator toolCalls={message.toolCalls} />
        )}

        {message.recommendations && message.recommendations.length > 0 && (
          <BookGrid recommendations={message.recommendations} />
        )}
      </div>
    </div>
  );
}
