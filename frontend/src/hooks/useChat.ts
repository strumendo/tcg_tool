import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ChatMessage, ChatRequest } from "@/lib/types";
import { useState, useCallback } from "react";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const sendMutation = useMutation({
    mutationFn: async (request: ChatRequest) => {
      const { data } = await api.post("/chat/message", request);
      return data;
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          timestamp: new Date().toISOString(),
        },
      ]);
    },
  });

  const sendMessage = useCallback(
    (content: string, deckId?: number) => {
      const userMessage: ChatMessage = {
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      sendMutation.mutate({ message: content, deck_id: deckId });
    },
    [sendMutation]
  );

  const clearHistory = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    sendMessage,
    clearHistory,
    isLoading: sendMutation.isPending,
  };
}
