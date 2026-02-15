"use client";

import type { DeckCard } from "@/lib/types";
import { CardImage } from "./CardImage";

interface DeckGridProps {
  cards: DeckCard[];
  onCardClick?: (deckCard: DeckCard) => void;
  showMissing?: boolean;
}

export function DeckGrid({ cards, onCardClick, showMissing = false }: DeckGridProps) {
  const pokemon = cards.filter((dc) => dc.card.card_type === "pokemon");
  const trainers = cards.filter((dc) => dc.card.card_type === "trainer");
  const energy = cards.filter((dc) => dc.card.card_type === "energy");

  const totalCards = cards.reduce((sum, dc) => sum + dc.quantity, 0);

  return (
    <div className="space-y-6">
      {/* Deck summary */}
      <div className="flex gap-4 text-sm font-medium">
        <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
          Pokemon: {pokemon.reduce((s, c) => s + c.quantity, 0)}
        </span>
        <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
          Trainer: {trainers.reduce((s, c) => s + c.quantity, 0)}
        </span>
        <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">
          Energy: {energy.reduce((s, c) => s + c.quantity, 0)}
        </span>
        <span
          className={`px-3 py-1 rounded-full ${
            totalCards === 60
              ? "bg-green-100 text-green-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          Total: {totalCards}/60
        </span>
      </div>

      {/* Pokemon section */}
      {pokemon.length > 0 && (
        <CardSection
          title={`Pokemon (${pokemon.reduce((s, c) => s + c.quantity, 0)})`}
          cards={pokemon}
          onCardClick={onCardClick}
          showMissing={showMissing}
        />
      )}

      {/* Trainer section */}
      {trainers.length > 0 && (
        <CardSection
          title={`Trainer (${trainers.reduce((s, c) => s + c.quantity, 0)})`}
          cards={trainers}
          onCardClick={onCardClick}
          showMissing={showMissing}
        />
      )}

      {/* Energy section */}
      {energy.length > 0 && (
        <CardSection
          title={`Energy (${energy.reduce((s, c) => s + c.quantity, 0)})`}
          cards={energy}
          onCardClick={onCardClick}
          showMissing={showMissing}
        />
      )}
    </div>
  );
}

function CardSection({
  title,
  cards,
  onCardClick,
  showMissing,
}: {
  title: string;
  cards: DeckCard[];
  onCardClick?: (dc: DeckCard) => void;
  showMissing: boolean;
}) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-800 mb-3">{title}</h3>
      <div className="card-grid">
        {cards.map((dc) =>
          Array.from({ length: dc.quantity }, (_, i) => (
            <div key={`${dc.card_id}-${i}`} className="text-center">
              <CardImage
                card={dc.card}
                onClick={() => onCardClick?.(dc)}
                showOverlay={showMissing}
                isOwned={dc.is_owned}
              />
              {i === 0 && (
                <p className="text-xs text-gray-600 mt-1 truncate">
                  {dc.quantity}x {dc.card.name_en}
                </p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
