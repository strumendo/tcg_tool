"use client";

import { useState } from "react";
import type { CollectionEntry } from "@/lib/types";
import { CardImage } from "@/components/deck/CardImage";

interface CollectionGridProps {
  entries: CollectionEntry[];
  onUpdateQuantity: (cardId: number, quantity: number) => void;
}

export function CollectionGrid({
  entries,
  onUpdateQuantity,
}: CollectionGridProps) {
  const [editingCardId, setEditingCardId] = useState<number | null>(null);
  const [editQuantity, setEditQuantity] = useState<number>(0);

  const handleCardClick = (entry: CollectionEntry) => {
    setEditingCardId(entry.card_id);
    setEditQuantity(entry.quantity_owned);
  };

  const handleSave = (cardId: number) => {
    onUpdateQuantity(cardId, editQuantity);
    setEditingCardId(null);
  };

  const handleCancel = () => {
    setEditingCardId(null);
  };

  if (entries.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
        <svg
          className="w-16 h-16 text-gray-300 mx-auto mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
        <p className="text-gray-500 text-lg mb-2">Colecao vazia</p>
        <p className="text-gray-400 text-sm">
          Use a aba &quot;Adicionar&quot; para incluir cartas na sua colecao.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {entries.map((entry) => (
        <div key={entry.card_id} className="relative group">
          {/* Quantity badge */}
          <div className="absolute top-2 left-2 z-10 bg-gray-900/80 text-white text-xs font-bold px-2 py-1 rounded-full min-w-[28px] text-center">
            x{entry.quantity_owned}
          </div>

          <CardImage
            card={entry.card}
            width={150}
            height={210}
            onClick={() => handleCardClick(entry)}
          />

          <p
            className="mt-1 text-xs text-gray-700 font-medium truncate text-center"
            title={entry.card.name_en}
          >
            {entry.card.name_en}
          </p>

          {entry.card.set && (
            <p className="text-xs text-gray-400 text-center truncate">
              {entry.card.set.code} {entry.card.set_number}
            </p>
          )}

          {/* Inline quantity editor */}
          {editingCardId === entry.card_id && (
            <div className="absolute inset-0 bg-black/60 rounded-lg flex flex-col items-center justify-center z-20">
              <p className="text-white text-sm font-medium mb-3 px-2 text-center truncate max-w-full">
                {entry.card.name_en}
              </p>
              <div className="flex items-center gap-2 mb-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditQuantity(Math.max(0, editQuantity - 1));
                  }}
                  className="w-8 h-8 bg-white text-gray-900 rounded-full flex items-center justify-center font-bold hover:bg-gray-200 transition-colors"
                >
                  -
                </button>
                <span className="text-white text-xl font-bold w-8 text-center">
                  {editQuantity}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditQuantity(editQuantity + 1);
                  }}
                  className="w-8 h-8 bg-white text-gray-900 rounded-full flex items-center justify-center font-bold hover:bg-gray-200 transition-colors"
                >
                  +
                </button>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSave(entry.card_id);
                  }}
                  className="px-3 py-1 bg-green-500 text-white rounded text-sm font-medium hover:bg-green-600 transition-colors"
                >
                  Salvar
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleCancel();
                  }}
                  className="px-3 py-1 bg-gray-500 text-white rounded text-sm font-medium hover:bg-gray-600 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
