"use client";

import type { DeckComparison, MatchupAnalysis, Card } from "@/lib/types";

interface ComparisonViewProps {
  comparison: DeckComparison;
  matchup: MatchupAnalysis;
  deckNameA?: string;
  deckNameB?: string;
}

export function ComparisonView({
  comparison,
  matchup,
  deckNameA = "Deck A",
  deckNameB = "Deck B",
}: ComparisonViewProps) {
  return (
    <div className="space-y-8">
      {/* Deck headers side-by-side */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <h3 className="font-bold text-blue-800 text-lg">{deckNameA}</h3>
          <p className="text-sm text-blue-600 mt-1">
            {comparison.unique_to_a.length} cartas exclusivas
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <h3 className="font-bold text-red-800 text-lg">{deckNameB}</h3>
          <p className="text-sm text-red-600 mt-1">
            {comparison.unique_to_b.length} cartas exclusivas
          </p>
        </div>
      </div>

      {/* Similarity bar */}
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600 font-medium">Similaridade entre decks</span>
          <span className="font-bold text-gray-800">
            {comparison.similarity_percentage.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-700"
            style={{ width: `${comparison.similarity_percentage}%` }}
          />
        </div>
      </div>

      {/* Score comparison bars */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-800">Comparacao de atributos</h4>
        <ScoreComparisonBar
          label="Velocidade"
          scoreA={matchup.speed_score_a}
          scoreB={matchup.speed_score_b}
          nameA={deckNameA}
          nameB={deckNameB}
        />
        <ScoreComparisonBar
          label="Consistencia"
          scoreA={matchup.consistency_score_a}
          scoreB={matchup.consistency_score_b}
          nameA={deckNameA}
          nameB={deckNameB}
        />
        <ScoreComparisonBar
          label="Poder"
          scoreA={matchup.power_score_a}
          scoreB={matchup.power_score_b}
          nameA={deckNameA}
          nameB={deckNameB}
        />
      </div>

      {/* Matchup favor */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
        <span className="text-sm text-gray-500">Favorito no confronto</span>
        <div className="text-lg font-bold text-gray-900 mt-1">
          {matchup.matchup_favor}
        </div>
      </div>

      {/* Advantages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {matchup.a_advantages.length > 0 && (
          <div>
            <h4 className="font-semibold text-blue-700 mb-2">
              Vantagens de {deckNameA}
            </h4>
            <ul className="space-y-1">
              {matchup.a_advantages.map((adv, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-blue-500 mt-0.5 shrink-0">&#9679;</span>
                  {adv}
                </li>
              ))}
            </ul>
          </div>
        )}
        {matchup.b_advantages.length > 0 && (
          <div>
            <h4 className="font-semibold text-red-700 mb-2">
              Vantagens de {deckNameB}
            </h4>
            <ul className="space-y-1">
              {matchup.b_advantages.map((adv, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-red-500 mt-0.5 shrink-0">&#9679;</span>
                  {adv}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Key differences */}
      {matchup.key_differences.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2">
            Diferencas principais
          </h4>
          <ul className="space-y-1">
            {matchup.key_differences.map((diff, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-purple-500 mt-0.5 shrink-0">&#9670;</span>
                {diff}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Shared cards */}
      {comparison.shared_cards.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2">
            Cartas em comum ({comparison.shared_cards.length})
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            {comparison.shared_cards.map(({ card_a }, i) => (
              <CardChip key={i} card={card_a} variant="shared" />
            ))}
          </div>
        </div>
      )}

      {/* Unique cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {comparison.unique_to_a.length > 0 && (
          <div>
            <h4 className="font-semibold text-blue-700 mb-2">
              Exclusivas de {deckNameA} ({comparison.unique_to_a.length})
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {comparison.unique_to_a.map((card, i) => (
                <CardChip key={i} card={card} variant="a" />
              ))}
            </div>
          </div>
        )}
        {comparison.unique_to_b.length > 0 && (
          <div>
            <h4 className="font-semibold text-red-700 mb-2">
              Exclusivas de {deckNameB} ({comparison.unique_to_b.length})
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {comparison.unique_to_b.map((card, i) => (
                <CardChip key={i} card={card} variant="b" />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ScoreComparisonBar({
  label,
  scoreA,
  scoreB,
}: {
  label: string;
  scoreA: number;
  scoreB: number;
  nameA: string;
  nameB: string;
}) {
  const pctA = (scoreA / 10) * 100;
  const pctB = (scoreB / 10) * 100;

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs text-blue-600 font-medium w-12 text-right shrink-0">
            {scoreA.toFixed(1)}
          </span>
          <div className="flex-1 bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <div
              className="h-full rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${pctA}%` }}
            />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <div
              className="h-full rounded-full bg-red-500 transition-all duration-500 ml-auto"
              style={{ width: `${pctB}%` }}
            />
          </div>
          <span className="text-xs text-red-600 font-medium w-12 shrink-0">
            {scoreB.toFixed(1)}
          </span>
        </div>
      </div>
    </div>
  );
}

function CardChip({
  card,
  variant,
}: {
  card: Card;
  variant: "shared" | "a" | "b";
}) {
  const borderColor =
    variant === "shared"
      ? "border-gray-300 bg-gray-50"
      : variant === "a"
        ? "border-blue-300 bg-blue-50"
        : "border-red-300 bg-red-50";

  const typeLabel =
    card.card_type === "pokemon"
      ? "PKM"
      : card.card_type === "trainer"
        ? "TRN"
        : "NRG";

  const typeColor =
    card.card_type === "pokemon"
      ? "text-blue-600"
      : card.card_type === "trainer"
        ? "text-purple-600"
        : "text-yellow-600";

  return (
    <div
      className={`border rounded px-2 py-1.5 text-xs ${borderColor}`}
    >
      <div className="font-medium text-gray-800 truncate">
        {card.name_pt || card.name_en}
      </div>
      <div className={`text-[10px] ${typeColor} font-medium`}>{typeLabel}</div>
    </div>
  );
}
