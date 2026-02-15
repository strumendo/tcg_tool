"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useMetaDeck } from "@/hooks/useMeta";
import { WinRateBadge } from "@/components/meta/WinRateBadge";
import { DeckGrid } from "@/components/deck/DeckGrid";
import { ENERGY_COLORS } from "@/lib/constants";

export default function MetaDeckDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const { data: deck, isLoading, error } = useMetaDeck(id);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4" />
        <p className="text-gray-500">Carregando detalhes do deck...</p>
      </div>
    );
  }

  if (error || !deck) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <svg className="w-10 h-10 text-red-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.27 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <p className="text-red-700 font-medium">Deck nao encontrado</p>
        <Link href="/meta" className="text-blue-600 hover:underline text-sm mt-2 inline-block">
          Voltar para Meta
        </Link>
      </div>
    );
  }

  const tierConfig: Record<number, { bg: string; text: string; label: string }> = {
    1: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Tier 1" },
    2: { bg: "bg-slate-100", text: "text-slate-700", label: "Tier 2" },
    3: { bg: "bg-amber-100", text: "text-amber-800", label: "Tier 3" },
  };

  const tier = tierConfig[deck.tier] || tierConfig[3];

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-500">
        <Link href="/meta" className="hover:text-blue-600 transition-colors">
          Meta
        </Link>
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span className="text-gray-800 font-medium">
          {deck.name_pt || deck.name_en}
        </span>
      </nav>

      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-gray-900">
                {deck.name_pt || deck.name_en}
              </h1>
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${tier.bg} ${tier.text}`}>
                {tier.label}
              </span>
            </div>

            {deck.name_pt && deck.name_en && (
              <p className="text-sm text-gray-400 mt-1">{deck.name_en}</p>
            )}

            {(deck.description_pt || deck.description_en) && (
              <p className="text-gray-600 mt-3">
                {deck.description_pt || deck.description_en}
              </p>
            )}
          </div>

          {/* Stats badges */}
          <div className="flex flex-wrap gap-3 shrink-0">
            <StatPill label="Meta Share" value={`${deck.meta_share}%`} />
            {deck.difficulty && <StatPill label="Dificuldade" value={deck.difficulty} />}
          </div>
        </div>

        {/* Energy type badges */}
        {deck.energy_types && deck.energy_types.length > 0 && (
          <div className="flex gap-2 mt-4">
            {deck.energy_types.map((type) => (
              <span
                key={type}
                className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full text-white"
                style={{
                  backgroundColor: ENERGY_COLORS[type] || "#A8A878",
                }}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full bg-white/30"
                />
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </span>
            ))}
          </div>
        )}

        {/* Key Pokemon */}
        {deck.key_pokemon && deck.key_pokemon.length > 0 && (
          <div className="mt-4">
            <span className="text-xs text-gray-500 font-medium uppercase tracking-wider">
              Pokemon Principais
            </span>
            <div className="flex flex-wrap gap-2 mt-1.5">
              {deck.key_pokemon.map((pkm) => (
                <span
                  key={pkm}
                  className="bg-blue-50 text-blue-700 text-sm font-medium px-3 py-1 rounded-lg border border-blue-200"
                >
                  {pkm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Strategy */}
      {(deck.strategy_pt || deck.strategy_en) && (
        <section className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Estrategia
          </h2>
          <p className="text-gray-600 leading-relaxed whitespace-pre-line">
            {deck.strategy_pt || deck.strategy_en}
          </p>
        </section>
      )}

      {/* Strengths and Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths */}
        {(deck.strengths_pt?.length > 0 || deck.strengths_en?.length > 0) && (
          <section className="bg-white border border-gray-200 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              Pontos Fortes
            </h2>
            <ul className="space-y-2">
              {(deck.strengths_pt?.length > 0 ? deck.strengths_pt : deck.strengths_en).map(
                (str, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-gray-700"
                  >
                    <span className="bg-green-100 text-green-600 rounded-full p-0.5 mt-0.5 shrink-0">
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </span>
                    {str}
                  </li>
                )
              )}
            </ul>
          </section>
        )}

        {/* Weaknesses */}
        {(deck.weaknesses_pt?.length > 0 || deck.weaknesses_en?.length > 0) && (
          <section className="bg-white border border-gray-200 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              Pontos Fracos
            </h2>
            <ul className="space-y-2">
              {(deck.weaknesses_pt?.length > 0 ? deck.weaknesses_pt : deck.weaknesses_en).map(
                (wk, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-gray-700"
                  >
                    <span className="bg-red-100 text-red-600 rounded-full p-0.5 mt-0.5 shrink-0">
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </span>
                    {wk}
                  </li>
                )
              )}
            </ul>
          </section>
        )}
      </div>

      {/* Matchups */}
      {deck.matchups && deck.matchups.length > 0 && (
        <section className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            Matchups
          </h2>
          <div className="space-y-3">
            {deck.matchups
              .sort((a, b) => b.win_rate_a - a.win_rate_a)
              .map((mu, i) => {
                const opponentId =
                  mu.deck_a_id === id ? mu.deck_b_id : mu.deck_a_id;
                const rate =
                  mu.deck_a_id === id ? mu.win_rate_a : 100 - mu.win_rate_a;
                const notes = mu.notes_pt || mu.notes_en;

                return (
                  <div
                    key={i}
                    className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0"
                  >
                    {/* Matchup indicator */}
                    <MatchupIndicator rate={rate} />

                    {/* Opponent name */}
                    <Link
                      href={`/meta/${opponentId}`}
                      className="flex-1 text-sm font-medium text-gray-800 hover:text-blue-600 transition-colors"
                    >
                      vs {opponentId}
                    </Link>

                    {/* Notes */}
                    {notes && (
                      <span className="text-xs text-gray-400 hidden md:inline max-w-xs truncate">
                        {notes}
                      </span>
                    )}

                    {/* Win rate badge */}
                    <WinRateBadge rate={rate} size="sm" />
                  </div>
                );
              })}
          </div>
        </section>
      )}

      {/* Card list */}
      {deck.cards && deck.cards.length > 0 && (
        <section className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Lista de Cartas
          </h2>
          <DeckGrid cards={deck.cards} />
        </section>
      )}

      {/* Back link */}
      <div className="pt-2">
        <Link
          href="/meta"
          className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Voltar para Meta
        </Link>
      </div>
    </div>
  );
}

function StatPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-center">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-sm font-bold text-gray-800">{value}</div>
    </div>
  );
}

function MatchupIndicator({ rate }: { rate: number }) {
  if (rate > 55) {
    return (
      <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" title="Favoravel" />
    );
  }
  if (rate >= 45) {
    return (
      <span className="w-2 h-2 rounded-full bg-yellow-400 shrink-0" title="Equilibrado" />
    );
  }
  return (
    <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" title="Desfavoravel" />
  );
}
