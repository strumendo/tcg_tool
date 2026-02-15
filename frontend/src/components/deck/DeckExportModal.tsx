"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

interface DeckExportModalProps {
  deckId: number;
  deckName: string;
  onClose: () => void;
}

export function DeckExportModal({ deckId, deckName, onClose }: DeckExportModalProps) {
  const [exportText, setExportText] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function fetchExport() {
      try {
        setLoading(true);
        const { data } = await api.get(`/decks/${deckId}/export`);
        setExportText(typeof data === "string" ? data : data.text || JSON.stringify(data));
      } catch {
        setError("Erro ao exportar deck. Tente novamente.");
      } finally {
        setLoading(false);
      }
    }
    fetchExport();
  }, [deckId]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(exportText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement("textarea");
      textarea.value = exportText;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Exportar Deck</h2>
            <p className="text-sm text-gray-500">{deckName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="p-6 flex-1 overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
              <span className="ml-3 text-gray-500">Gerando lista...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {!loading && !error && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Formato TCG Live - cole no jogo ou em sites de deck building.
              </p>
              <textarea
                value={exportText}
                readOnly
                rows={16}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm bg-gray-50 focus:outline-none resize-none"
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-3 px-6 py-4 border-t border-gray-200">
          <button
            onClick={handleCopy}
            disabled={loading || !!error}
            className={`flex-1 py-2.5 font-medium rounded-lg transition-colors ${
              copied
                ? "bg-green-600 text-white"
                : "bg-primary-600 text-white hover:bg-primary-700"
            } disabled:bg-gray-300 disabled:cursor-not-allowed`}
          >
            {copied ? "Copiado!" : "Copiar"}
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2.5 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
