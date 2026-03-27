"use client";

import { useRef, useEffect } from "react";
import { useChat } from "@/hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";

export function ChatContainer() {
  const { messages, isStreaming, sendMessage, resetChat } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col h-screen">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-earth-light/40">
        <h2 className="font-serif text-lg text-charcoal">Chat</h2>
        <button
          onClick={resetChat}
          className="text-sm text-stone hover:text-charcoal transition-colors px-3 py-1.5 rounded-lg hover:bg-earth-light/20"
        >
          New chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-3xl mx-auto flex flex-col gap-4">
          {messages.length === 0 && (
            <div className="flex-1 flex items-center justify-center min-h-[60vh]">
              <div className="text-center">
                <h3 className="font-serif text-2xl text-charcoal mb-2">
                  What would you like to read?
                </h3>
                <p className="text-sm text-stone">
                  Tell me about your reading tastes and I'll find your next great book.
                </p>
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
