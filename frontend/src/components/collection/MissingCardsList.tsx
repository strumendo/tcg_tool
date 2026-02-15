"use client";

import type { MissingCard } from "@/lib/types";

interface MissingCardsListProps {
  missing: MissingCard[];
  onMarkOwned: (cardId: number, currentOwned: number) => void;
}

export function MissingCardsList({
  missing,
  onMarkOwned,
}: MissingCardsListProps) {
  if (missing.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
        <svg
          className="w-16 h-16 text-green-300 mx-auto mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-gray-500 text-lg mb-2">Nenhuma carta faltando!</p>
        <p className="text-gray-400 text-sm">
          Voce tem todas as cartas necessarias para este deck.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
      {missing.map((m) => {
        const bgClass =
          m.quantity_missing > 2
            ? "bg-red-50"
            : m.quantity_missing === 1
              ? "bg-yellow-50"
              : "bg-white";

        const borderClass =
          m.quantity_missing > 2
            ? "border-l-4 border-l-red-400"
            : m.quantity_missing === 1
              ? "border-l-4 border-l-yellow-400"
              : "";

        return (
          <div
            key={m.card_id}
            className={`p-4 flex items-center justify-between ${bgClass} ${borderClass} first:rounded-t-xl last:rounded-b-xl`}
          >
            <div className="flex items-center gap-3 min-w-0">
              {/* Card info */}
              <div className="min-w-0">
                <p className="font-medium text-gray-900 truncate">
                  {m.card_name || `Carta #${m.card_id}`}
                </p>
                <div className="flex items-center gap-3 text-sm mt-1">
                  <span className="text-blue-600">
                    Precisa: {m.quantity_needed}
                  </span>
                  <span className="text-green-600">
                    Tem: {m.quantity_owned}
                  </span>
                  <span className="text-red-600 font-semibold">
                    Falta: {m.quantity_missing}
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => onMarkOwned(m.card_id, m.quantity_owned)}
              className="flex-shrink-0 ml-4 px-3 py-1.5 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
            >
              +1 Adquirida
            </button>
          </div>
        );
      })}
    </div>
  );
}
