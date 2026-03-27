"use client";

import { useState, useCallback, useRef } from "react";
import type { Message, BookRecommendation, ToolCall } from "@/lib/types";
import { parseSSE } from "@/lib/sse";
import { chatUrl, deleteSession } from "@/lib/api";

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const sessionIdRef = useRef<string | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    const userMessage: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setIsStreaming(true);

    // Add empty assistant message that we'll stream into
    const assistantMessage: Message = {
      role: "assistant",
      content: "",
      toolCalls: [],
      recommendations: [],
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const response = await fetch(chatUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionIdRef.current,
          message: text,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      for await (const event of parseSSE(response)) {
        switch (event.event) {
          case "session": {
            const { session_id } = event.data as { session_id: string };
            sessionIdRef.current = session_id;
            break;
          }
          case "text": {
            const { content } = event.data as { content: string };
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = {
                ...last,
                content: last.content + content,
              };
              return updated;
            });
            break;
          }
          case "tool_call": {
            const toolCall = event.data as ToolCall;
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              const toolCalls = [...(last.toolCalls || [])];

              if (toolCall.status === "calling") {
                toolCalls.push(toolCall);
              } else {
                // Update existing tool call status
                const idx = toolCalls.findIndex(
                  (tc) => tc.name === toolCall.name && tc.status === "calling"
                );
                if (idx >= 0) toolCalls[idx] = toolCall;
              }

              updated[updated.length - 1] = { ...last, toolCalls };
              return updated;
            });
            break;
          }
          case "recommendation": {
            const recommendations = event.data as BookRecommendation[];
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = { ...last, recommendations };
              return updated;
            });
            break;
          }
          case "done":
            break;
        }
      }
    } catch (error) {
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        updated[updated.length - 1] = {
          ...last,
          content:
            last.content ||
            "Sorry, something went wrong. Please try again.",
        };
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  }, []);

  const resetChat = useCallback(async () => {
    if (sessionIdRef.current) {
      await deleteSession(sessionIdRef.current);
    }
    sessionIdRef.current = null;
    setMessages([]);
  }, []);

  return { messages, isStreaming, sendMessage, resetChat };
}
