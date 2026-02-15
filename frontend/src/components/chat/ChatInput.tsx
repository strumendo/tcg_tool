"use client";

import { useState, useRef, useEffect } from "react";
import { useDecks } from "@/hooks/useDecks";

interface ChatInputProps {
  onSend: (message: string, deckId?: number) => void;
  isLoading: boolean;
  selectedDeckId: number | null;
  onDeckChange: (deckId: number | null) => void;
}

const SUGGESTION_CHIPS = [
  { label: "Melhor deck do meta", prompt: "Qual o melhor deck do meta atual?" },
  { label: "Dicas de rotacao", prompt: "Quais cartas serao afetadas pela rotacao de marco 2026?" },
  { label: "Como melhorar meu deck", prompt: "Analise meu deck e sugira melhorias" },
  { label: "Matchups", prompt: "Quais sao os melhores e piores matchups do meu deck?" },
  { label: "Budget alternativas", prompt: "Quais alternativas mais baratas posso usar no meu deck?" },
  { label: "Estrategia contra Charizard", prompt: "Como jogar contra Charizard ex?" },
];

export default function ChatInput({
  onSend,
  isLoading,
  selectedDeckId,
  onDeckChange,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { data: decks } = useDecks();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  }, [input]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim(), selectedDeckId ?? undefined);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChipClick = (prompt: string) => {
    onSend(prompt, selectedDeckId ?? undefined);
  };

  return (
    <div className="border-t border-gray-200 bg-white">
      {/* Suggestion chips - only show when no messages context needed */}
      <div className="px-4 pt-3 flex flex-wrap gap-2">
        {SUGGESTION_CHIPS.map((chip) => (
          <button
            key={chip.label}
            onClick={() => handleChipClick(chip.prompt)}
            disabled={isLoading}
            className="text-xs px-3 py-1.5 rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 hover:border-gray-400 transition-colors disabled:opacity-50"
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* Deck selector + input */}
      <div className="p-4 space-y-3">
        {/* Deck context selector */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-500 whitespace-nowrap">
            Contexto do deck:
          </label>
          <select
            value={selectedDeckId ?? ""}
            onChange={(e) =>
              onDeckChange(e.target.value ? Number(e.target.value) : null)
            }
            className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 max-w-xs"
          >
            <option value="">Nenhum deck selecionado</option>
            {decks?.map((deck) => (
              <option key={deck.id} value={deck.id}>
                {deck.name}
              </option>
            ))}
          </select>
          {selectedDeckId && (
            <span className="text-xs text-primary-600 bg-primary-50 px-2 py-1 rounded-full">
              Deck ativo
            </span>
          )}
        </div>

        {/* Input area */}
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua pergunta sobre Pokemon TCG..."
            rows={1}
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none text-sm leading-relaxed"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-5 py-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:bg-gray-300 transition-colors flex items-center gap-2 font-medium text-sm"
          >
            {isLoading ? (
              <svg
                className="w-4 h-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="3"
                  className="opacity-25"
                />
                <path
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  fill="currentColor"
                  className="opacity-75"
                />
              </svg>
            ) : (
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}
