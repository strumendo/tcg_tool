"use client";

import { useRef, useEffect } from "react";
import type { ChatMessage as ChatMessageType } from "@/lib/types";
import ChatMessageComponent from "./ChatMessage";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  streamingContent: string;
}

export default function ChatWindow({
  messages,
  isLoading,
  streamingContent,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && !isLoading && (
        <div className="text-center py-20">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">IA</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            Assistente Pokemon TCG
          </h2>
          <p className="text-gray-400 max-w-md mx-auto">
            Pergunte sobre estrategias, cartas, decks, matchups, rotacao ou
            qualquer duvida sobre o Pokemon TCG competitivo.
          </p>
        </div>
      )}

      {messages.map((msg, i) => (
        <ChatMessageComponent
          key={i}
          role={msg.role}
          content={msg.content}
          timestamp={msg.timestamp}
        />
      ))}

      {/* Streaming response */}
      {isLoading && streamingContent && (
        <ChatMessageComponent
          role="assistant"
          content={streamingContent}
          timestamp={new Date().toISOString()}
          isStreaming
        />
      )}

      {/* Loading indicator when no streaming content yet */}
      {isLoading && !streamingContent && (
        <div className="flex justify-start">
          <div className="flex items-end gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              IA
            </div>
            <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
