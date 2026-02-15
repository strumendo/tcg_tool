"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface DeckImportFormProps {
  onImportSuccess?: (deckId: number) => void;
}

export function DeckImportForm({ onImportSuccess }: DeckImportFormProps) {
  const [text, setText] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleImport = async () => {
    if (!text.trim()) {
      setError("Cole o texto do deck no formato TCG Live");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post("/decks/import", {
        text: text.trim(),
        name: name.trim() || undefined,
      });
      onImportSuccess?.(response.data.id);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Erro ao importar deck";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const exampleDeck = `Pokemon: 22
4 Dreepy TWM 128
4 Drakloak TWM 129
3 Dragapult ex TWM 130
2 Duskull PRE 35

Trainer: 31
4 Lillie's Determination MEG 119
4 Buddy-Buddy Poffin TEF 144
4 Ultra Ball MEG 131

Energy: 7
3 Fire Energy MEE 2
3 Psychic Energy MEE 5
1 Darkness Energy MEE 7`;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Importar Deck
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nome do Deck (opcional)
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex: Dragapult ex"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Lista do Deck (formato TCG Live)
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={exampleDeck}
            rows={16}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleImport}
          disabled={loading || !text.trim()}
          className="w-full py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Importando..." : "Importar Deck"}
        </button>
      </div>
    </div>
  );
}
