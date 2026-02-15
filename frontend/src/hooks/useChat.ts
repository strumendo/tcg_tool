import { useState, useCallback, useRef } from "react";
import type { ChatMessage } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string, deckId?: number) => {
      const userMessage: ChatMessage = {
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setStreamingContent("");

      // Build history from existing messages (exclude the just-added user message)
      const history = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      try {
        abortControllerRef.current = new AbortController();

        const response = await fetch(`${API_URL}/chat/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: content,
            deck_id: deckId,
            history,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let fullText = "";

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.slice(6));
                  if (data.type === "text") {
                    fullText += data.content;
                    setStreamingContent(fullText);
                  } else if (data.type === "error") {
                    throw new Error(data.content);
                  }
                } catch (e) {
                  if (e instanceof SyntaxError) continue;
                  throw e;
                }
              }
            }
          }
        }

        // Add completed message
        if (fullText) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: fullText,
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      } catch (error) {
        if ((error as Error).name === "AbortError") return;

        // Fallback to non-streaming endpoint
        try {
          const response = await fetch(`${API_URL}/chat/message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: content,
              deck_id: deckId,
              history,
            }),
          });
          const data = await response.json();
          if (data.response) {
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: data.response,
                timestamp: new Date().toISOString(),
              },
            ]);
          }
        } catch {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.",
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      } finally {
        setIsLoading(false);
        setStreamingContent("");
        abortControllerRef.current = null;
      }
    },
    [messages]
  );

  const stopStreaming = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  const clearHistory = useCallback(() => {
    setMessages([]);
    setStreamingContent("");
  }, []);

  return {
    messages,
    sendMessage,
    clearHistory,
    stopStreaming,
    isLoading,
    streamingContent,
  };
}
