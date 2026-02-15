"use client";

import { useMemo } from "react";
import type { SubstitutionSuggestion } from "@/lib/types";

interface SubstitutionListProps {
  suggestions: SubstitutionSuggestion[];
}

export function SubstitutionList({ suggestions }: SubstitutionListProps) {
  // Group suggestions by original card
  const grouped = useMemo(() => {
    const map = new Map<string, SubstitutionSuggestion[]>();
    for (const s of suggestions) {
      const key = s.original_card.name_en;
      const existing = map.get(key) || [];
      existing.push(s);
      map.set(key, existing);
    }
    return Array.from(map.entries());
  }, [suggestions]);

  if (suggestions.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p>Nenhuma substituicao sugerida</p>
        <p className="text-sm mt-1">Todas as cartas estao legais para o formato atual</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {grouped.map(([originalName, subs]) => {
        const originalCard = subs[0].original_card;
        return (
          <div key={originalName} className="border border-gray-200 rounded-lg overflow-hidden">
            {/* Original card header */}
            <div className="bg-red-50 border-b border-red-200 px-4 py-3 flex items-center gap-3">
              <div className="bg-red-100 rounded-full p-1.5">
                <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div>
                <span className="font-semibold text-red-800">
                  {originalCard.name_pt || originalCard.name_en}
                </span>
                <span className="text-xs text-red-600 ml-2">
                  ({originalCard.card_type === "pokemon" ? "Pokemon" : originalCard.card_type === "trainer" ? "Treinador" : "Energia"})
                </span>
              </div>
            </div>

            {/* Substitution options */}
            <div className="divide-y divide-gray-100">
              {subs
                .sort((a, b) => b.match_score - a.match_score)
                .map((sub, idx) => (
                  <div key={idx} className="px-4 py-3 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-3">
                      {/* Arrow */}
                      <svg className="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>

                      {/* Suggested card name */}
                      <div className="flex-1 min-w-0">
                        <span className="font-medium text-gray-900">
                          {sub.suggested_card.name_pt || sub.suggested_card.name_en}
                        </span>
                        {sub.suggested_card.set_number && (
                          <span className="text-xs text-gray-400 ml-2">
                            #{sub.suggested_card.set_number}
                          </span>
                        )}
                      </div>

                      {/* Match score */}
                      <div className="shrink-0 flex items-center gap-2 w-28">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              sub.match_score >= 80
                                ? "bg-green-500"
                                : sub.match_score >= 50
                                  ? "bg-yellow-500"
                                  : "bg-orange-500"
                            }`}
                            style={{ width: `${sub.match_score}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-gray-600 w-8 text-right">
                          {sub.match_score}%
                        </span>
                      </div>
                    </div>

                    {/* Reasons */}
                    {sub.reasons.length > 0 && (
                      <ul className="mt-2 ml-8 space-y-0.5">
                        {sub.reasons.map((reason, ri) => (
                          <li
                            key={ri}
                            className="text-xs text-gray-500 flex items-start gap-1.5"
                          >
                            <span className="text-gray-400 mt-0.5 shrink-0">&#8226;</span>
                            {reason}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
