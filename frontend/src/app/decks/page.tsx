"use client";

import Link from "next/link";
import { useDecks, useDeleteDeck } from "@/hooks/useDecks";

export default function DecksPage() {
  const { data: decks, isLoading } = useDecks();
  const deleteDeck = useDeleteDeck();

  if (isLoading) {
    return <div className="text-center py-10">Carregando decks...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Meus Decks</h1>
        <div className="flex gap-3">
          <Link
            href="/decks/import"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Importar Deck
          </Link>
          <Link
            href="/decks/new"
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Novo Deck
          </Link>
        </div>
      </div>

      {!decks || decks.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
          <p className="text-gray-500 text-lg mb-4">
            Voce ainda nao tem decks salvos
          </p>
          <Link
            href="/decks/import"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Importar primeiro deck
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {decks.map((deck) => (
            <div
              key={deck.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-3">
                <Link
                  href={`/decks/${deck.id}`}
                  className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                >
                  {deck.name}
                </Link>
                {deck.is_active && (
                  <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">
                    Ativo
                  </span>
                )}
              </div>

              {deck.archetype && (
                <p className="text-sm text-gray-500 mb-2">{deck.archetype}</p>
              )}

              <div className="flex gap-3 text-sm text-gray-600 mb-4">
                <span>
                  {deck.cards.filter((c) => c.card.card_type === "pokemon").reduce((s, c) => s + c.quantity, 0)} Pokemon
                </span>
                <span>
                  {deck.cards.filter((c) => c.card.card_type === "trainer").reduce((s, c) => s + c.quantity, 0)} Trainers
                </span>
                <span>
                  {deck.cards.filter((c) => c.card.card_type === "energy").reduce((s, c) => s + c.quantity, 0)} Energy
                </span>
              </div>

              <div className="flex gap-2">
                <Link
                  href={`/decks/${deck.id}`}
                  className="flex-1 text-center py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors"
                >
                  Visualizar
                </Link>
                <Link
                  href={`/decks/${deck.id}/analysis`}
                  className="flex-1 text-center py-2 bg-blue-100 text-blue-700 rounded-lg text-sm hover:bg-blue-200 transition-colors"
                >
                  Analisar
                </Link>
                <button
                  onClick={() => {
                    if (confirm("Deletar este deck?")) {
                      deleteDeck.mutate(deck.id);
                    }
                  }}
                  className="px-3 py-2 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200 transition-colors"
                >
                  X
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
