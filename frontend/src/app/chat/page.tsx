"use client";

import { useState } from "react";
import { useChat } from "@/hooks/useChat";
import ChatWindow from "@/components/chat/ChatWindow";
import ChatInput from "@/components/chat/ChatInput";

export default function ChatPage() {
  const {
    messages,
    sendMessage,
    clearHistory,
    stopStreaming,
    isLoading,
    streamingContent,
  } = useChat();
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chat IA</h1>
          <p className="text-sm text-gray-500">
            Assistente especializado em Pokemon TCG
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isLoading && (
            <button
              onClick={stopStreaming}
              className="text-sm px-3 py-1.5 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
            >
              Parar
            </button>
          )}
          {messages.length > 0 && (
            <button
              onClick={clearHistory}
              className="text-sm px-3 py-1.5 text-gray-500 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Limpar conversa
            </button>
          )}
        </div>
      </div>

      {/* Chat container */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-[calc(100%-4rem)]">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          streamingContent={streamingContent}
        />
        <ChatInput
          onSend={sendMessage}
          isLoading={isLoading}
          selectedDeckId={selectedDeckId}
          onDeckChange={setSelectedDeckId}
        />
      </div>
    </div>
  );
}
