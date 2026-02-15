"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useDeck, useDeleteDeck, useDeckMissingCards } from "@/hooks/useDecks";
import { DeckGrid } from "@/components/deck/DeckGrid";
import { CardDetailPanel } from "@/components/deck/CardDetailPanel";
import { DeckExportModal } from "@/components/deck/DeckExportModal";
import type { DeckCard, Card, MissingCard } from "@/lib/types";

export default function DeckDetailPage() {
  const params = useParams();
  const router = useRouter();
  const deckId = Number(params.id);

  const { data: deck, isLoading, error } = useDeck(deckId);
  const { data: missingCards } = useDeckMissingCards(deckId);
  const deleteDeck = useDeleteDeck();

  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [showExportModal, setShowExportModal] = useState(false);

  const handleCardClick = (deckCard: DeckCard) => {
    setSelectedCard(deckCard.card);
  };

  const handleDelete = () => {
    if (confirm("Tem certeza que deseja deletar este deck?")) {
      deleteDeck.mutate(deckId, {
        onSuccess: () => router.push("/decks"),
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" />
        <span className="ml-3 text-gray-500 text-lg">Carregando deck...</span>
      </div>
    );
  }

  if (error || !deck) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600 text-lg mb-4">Erro ao carregar deck</p>
        <Link
          href="/decks"
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Voltar para Meus Decks
        </Link>
      </div>
    );
  }

  const hasMissing = missingCards && Array.isArray(missingCards) && (missingCards as MissingCard[]).length > 0;
  const missingCount = hasMissing ? (missingCards as MissingCard[]).reduce((sum: number, mc: MissingCard) => sum + mc.quantity_missing, 0) : 0;

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Deck info */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900">{deck.name}</h1>
              {deck.is_valid ? (
                <span className="bg-green-100 text-green-700 text-xs font-medium px-2.5 py-1 rounded-full">
                  Valido
                </span>
              ) : (
                <span className="bg-red-100 text-red-700 text-xs font-medium px-2.5 py-1 rounded-full">
                  Invalido
                </span>
              )}
              {deck.is_active && (
                <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full">
                  Ativo
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
              {deck.archetype && (
                <span className="bg-purple-100 text-purple-700 px-2.5 py-0.5 rounded-full font-medium">
                  {deck.archetype}
                </span>
              )}
              <span>{deck.total_cards} cartas</span>
              <span>
                Criado em{" "}
                {new Date(deck.created_at).toLocaleDateString("pt-BR")}
              </span>
            </div>

            {deck.notes && (
              <p className="text-sm text-gray-600 mt-2">{deck.notes}</p>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setShowExportModal(true)}
              className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
            >
              Exportar
            </button>
            <Link
              href={`/decks/${deckId}/analysis`}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Analisar
            </Link>
            <Link
              href={`/decks/${deckId}/edit`}
              className="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
            >
              Editar
            </Link>
            <button
              onClick={handleDelete}
              disabled={deleteDeck.isPending}
              className="px-4 py-2 bg-red-100 text-red-700 text-sm font-medium rounded-lg hover:bg-red-200 transition-colors disabled:opacity-50"
            >
              {deleteDeck.isPending ? "Deletando..." : "Deletar"}
            </button>
          </div>
        </div>
      </div>

      {/* Missing cards alert */}
      {hasMissing && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl px-5 py-4 mb-6 flex items-center gap-3">
          <svg className="w-5 h-5 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.27 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div>
            <p className="text-sm font-medium text-amber-800">
              {missingCount} carta{missingCount !== 1 ? "s" : ""} faltando na sua colecao
            </p>
            <p className="text-xs text-amber-600">
              Cartas nao encontradas na sua colecao estao marcadas em vermelho
            </p>
          </div>
        </div>
      )}

      {/* Deck grid */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        {deck.cards.length > 0 ? (
          <DeckGrid
            cards={deck.cards}
            onCardClick={handleCardClick}
            showMissing={!!hasMissing}
          />
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">Deck vazio</p>
            <p className="text-sm">Este deck ainda nao possui cartas</p>
          </div>
        )}
      </div>

      {/* Card detail panel */}
      <CardDetailPanel
        card={selectedCard}
        onClose={() => setSelectedCard(null)}
      />

      {/* Export modal */}
      {showExportModal && (
        <DeckExportModal
          deckId={deckId}
          deckName={deck.name}
          onClose={() => setShowExportModal(false)}
        />
      )}
    </div>
  );
}
