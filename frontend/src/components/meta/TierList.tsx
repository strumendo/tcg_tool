"use client";

import Link from "next/link";
import type { MetaDeck } from "@/lib/types";
import { ENERGY_COLORS } from "@/lib/constants";

interface TierListProps {
  metaDecks: MetaDeck[];
}

const TIER_CONFIG: Record<number, { label: string; bgHeader: string; textHeader: string; border: string }> = {
  1: {
    label: "Tier 1",
    bgHeader: "bg-yellow-400",
    textHeader: "text-yellow-900",
    border: "border-yellow-300",
  },
  2: {
    label: "Tier 2",
    bgHeader: "bg-slate-400",
    textHeader: "text-slate-900",
    border: "border-slate-300",
  },
  3: {
    label: "Tier 3",
    bgHeader: "bg-amber-600",
    textHeader: "text-amber-50",
    border: "border-amber-500",
  },
};

export function TierList({ metaDecks }: TierListProps) {
  const tiers = [1, 2, 3];

  return (
    <div className="space-y-8">
      {tiers.map((tier) => {
        const tierDecks = metaDecks.filter((d) => d.tier === tier);
        if (tierDecks.length === 0) return null;

        const config = TIER_CONFIG[tier];

        return (
          <section key={tier}>
            {/* Tier header */}
            <div
              className={`${config.bgHeader} ${config.textHeader} px-4 py-2 rounded-t-lg font-bold text-lg flex items-center gap-2`}
            >
              <TierIcon tier={tier} />
              {config.label}
              <span className="text-sm font-normal opacity-80 ml-1">
                ({tierDecks.length} {tierDecks.length === 1 ? "deck" : "decks"})
              </span>
            </div>

            {/* Deck entries */}
            <div className={`border ${config.border} border-t-0 rounded-b-lg divide-y divide-gray-100`}>
              {tierDecks.map((deck) => (
                <Link
                  key={deck.id}
                  href={`/meta/${deck.id}`}
                  className="flex items-center gap-4 px-4 py-3 hover:bg-gray-50 transition-colors group first:rounded-none last:rounded-b-lg"
                >
                  {/* Energy type color dots */}
                  <div className="flex gap-1 shrink-0">
                    {deck.energy_types?.map((type) => (
                      <span
                        key={type}
                        className="w-5 h-5 rounded-full border border-white shadow-sm"
                        style={{
                          backgroundColor: ENERGY_COLORS[type] || "#A8A878",
                        }}
                        title={type}
                      />
                    ))}
                  </div>

                  {/* Deck info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                        {deck.name_pt || deck.name_en}
                      </span>
                      {deck.difficulty && (
                        <DifficultyBadge difficulty={deck.difficulty} />
                      )}
                    </div>
                    {deck.key_pokemon && deck.key_pokemon.length > 0 && (
                      <p className="text-xs text-gray-500 mt-0.5 truncate">
                        {deck.key_pokemon.join(", ")}
                      </p>
                    )}
                  </div>

                  {/* Meta share bar */}
                  <div className="flex items-center gap-2 shrink-0 w-32">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-blue-500 transition-all"
                        style={{ width: `${Math.min(deck.meta_share * 5, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600 w-10 text-right">
                      {deck.meta_share}%
                    </span>
                  </div>

                  {/* Arrow */}
                  <svg
                    className="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors shrink-0"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </Link>
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}

function TierIcon({ tier }: { tier: number }) {
  if (tier === 1) {
    return (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    );
  }
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M13 10V3L4 14h7v7l9-11h-7z"
      />
    </svg>
  );
}

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const lower = difficulty.toLowerCase();
  const colorClass =
    lower === "easy" || lower === "facil"
      ? "bg-green-100 text-green-700"
      : lower === "medium" || lower === "medio" || lower === "moderado"
        ? "bg-yellow-100 text-yellow-700"
        : "bg-red-100 text-red-700";

  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${colorClass}`}>
      {difficulty}
    </span>
  );
}
