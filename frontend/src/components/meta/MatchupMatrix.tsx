"use client";

import { useState, useMemo } from "react";
import type { MetaDeck, MetaMatchup } from "@/lib/types";

interface MatchupMatrixProps {
  matchups: MetaMatchup[];
  metaDecks: MetaDeck[];
}

function getWinRateBg(rate: number): string {
  // Gradient from red (30%) through yellow (50%) to green (70%)
  if (rate >= 70) return "#16a34a";
  if (rate >= 60) return "#4ade80";
  if (rate >= 55) return "#86efac";
  if (rate >= 50) return "#fde047";
  if (rate >= 45) return "#fbbf24";
  if (rate >= 40) return "#f87171";
  return "#dc2626";
}

export function MatchupMatrix({ matchups, metaDecks }: MatchupMatrixProps) {
  const [hoveredCell, setHoveredCell] = useState<{
    row: string;
    col: string;
    matchup: MetaMatchup;
  } | null>(null);

  // Build a lookup map: deck_a_id -> deck_b_id -> matchup
  const matchupMap = useMemo(() => {
    const map: Record<string, Record<string, MetaMatchup>> = {};
    for (const m of matchups) {
      if (!map[m.deck_a_id]) map[m.deck_a_id] = {};
      map[m.deck_a_id][m.deck_b_id] = m;
    }
    return map;
  }, [matchups]);

  // Sort decks by tier then by meta share
  const sortedDecks = useMemo(() => {
    return [...metaDecks].sort((a, b) => {
      if (a.tier !== b.tier) return a.tier - b.tier;
      return b.meta_share - a.meta_share;
    });
  }, [metaDecks]);

  const getDeckShortName = (deck: MetaDeck): string => {
    const name = deck.name_pt || deck.name_en;
    if (name.length > 14) return name.slice(0, 12) + "...";
    return name;
  };

  const getMatchupRate = (rowId: string, colId: string): number | null => {
    if (rowId === colId) return null;
    const m = matchupMap[rowId]?.[colId];
    if (m) return m.win_rate_a;
    // Check reverse matchup
    const rev = matchupMap[colId]?.[rowId];
    if (rev) return 100 - rev.win_rate_a;
    return null;
  };

  const getMatchupData = (rowId: string, colId: string): MetaMatchup | null => {
    return matchupMap[rowId]?.[colId] || matchupMap[colId]?.[rowId] || null;
  };

  return (
    <div className="relative">
      <div className="overflow-x-auto">
        <table className="border-collapse text-sm">
          <thead>
            <tr>
              <th className="p-2 text-left text-xs font-semibold text-gray-500 sticky left-0 bg-gray-50 z-10 min-w-[120px]">
                Matchup
              </th>
              {sortedDecks.map((deck) => (
                <th
                  key={deck.id}
                  className="p-1.5 text-center text-xs font-medium text-gray-600 min-w-[60px] max-w-[80px]"
                >
                  <div className="writing-mode-vertical transform -rotate-45 origin-center whitespace-nowrap">
                    {getDeckShortName(deck)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedDecks.map((rowDeck) => (
              <tr key={rowDeck.id} className="border-t border-gray-100">
                <td className="p-2 font-medium text-gray-700 text-xs sticky left-0 bg-white z-10 border-r border-gray-200">
                  {getDeckShortName(rowDeck)}
                </td>
                {sortedDecks.map((colDeck) => {
                  const isDiagonal = rowDeck.id === colDeck.id;
                  const rate = getMatchupRate(rowDeck.id, colDeck.id);

                  if (isDiagonal) {
                    return (
                      <td
                        key={colDeck.id}
                        className="p-1.5 text-center bg-gray-200"
                      >
                        <span className="text-xs text-gray-400">--</span>
                      </td>
                    );
                  }

                  return (
                    <td
                      key={colDeck.id}
                      className="p-1.5 text-center cursor-pointer transition-all hover:ring-2 hover:ring-blue-400 hover:z-20 relative"
                      style={{
                        backgroundColor: rate !== null ? getWinRateBg(rate) : "#f3f4f6",
                      }}
                      onMouseEnter={() => {
                        const matchup = getMatchupData(rowDeck.id, colDeck.id);
                        if (matchup) {
                          setHoveredCell({
                            row: rowDeck.id,
                            col: colDeck.id,
                            matchup,
                          });
                        }
                      }}
                      onMouseLeave={() => setHoveredCell(null)}
                    >
                      <span className="text-xs font-semibold">
                        {rate !== null ? `${rate}` : "?"}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Tooltip on hover */}
      {hoveredCell && (
        <MatchupTooltip
          matchup={hoveredCell.matchup}
          deckA={metaDecks.find((d) => d.id === hoveredCell.matchup.deck_a_id)}
          deckB={metaDecks.find((d) => d.id === hoveredCell.matchup.deck_b_id)}
        />
      )}

      {/* Legend */}
      <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
        <span>Legenda:</span>
        <div className="flex items-center gap-1">
          <span className="inline-block w-4 h-4 rounded" style={{ backgroundColor: "#dc2626" }} />
          <span>&lt;40%</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="inline-block w-4 h-4 rounded" style={{ backgroundColor: "#fde047" }} />
          <span>45-55%</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="inline-block w-4 h-4 rounded" style={{ backgroundColor: "#16a34a" }} />
          <span>&gt;60%</span>
        </div>
      </div>
    </div>
  );
}

function MatchupTooltip({
  matchup,
  deckA,
  deckB,
}: {
  matchup: MetaMatchup;
  deckA?: MetaDeck;
  deckB?: MetaDeck;
}) {
  const nameA = deckA?.name_pt || deckA?.name_en || matchup.deck_a_id;
  const nameB = deckB?.name_pt || deckB?.name_en || matchup.deck_b_id;

  return (
    <div className="absolute z-30 bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-900 text-white rounded-lg shadow-xl p-3 min-w-[250px] pointer-events-none">
      <div className="text-sm font-semibold mb-1">
        {nameA} vs {nameB}
      </div>
      <div className="text-xs space-y-1">
        <div>
          {nameA}: <span className="font-bold text-green-400">{matchup.win_rate_a}%</span>
        </div>
        <div>
          {nameB}: <span className="font-bold text-red-400">{100 - matchup.win_rate_a}%</span>
        </div>
        {matchup.notes_pt && (
          <div className="mt-1 text-gray-300 border-t border-gray-700 pt-1">
            {matchup.notes_pt}
          </div>
        )}
        {!matchup.notes_pt && matchup.notes_en && (
          <div className="mt-1 text-gray-300 border-t border-gray-700 pt-1">
            {matchup.notes_en}
          </div>
        )}
      </div>
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-gray-900 rotate-45" />
    </div>
  );
}
