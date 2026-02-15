"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useDeck, useDecks } from "@/hooks/useDecks";
import {
  useRotationAnalysis,
  useDeckComparison,
  useMatchupAnalysis,
  useSubstitutions,
} from "@/hooks/useAnalysis";
import type {
  DeckComparisonOut,
  MatchupAnalysisOut,
  SubstitutionSuggestionOut,
  RotationCardOut,
} from "@/hooks/useAnalysis";
import { SEVERITY_COLORS, REGULATION_MARKS } from "@/lib/constants";
import type { Severity } from "@/lib/types";

type AnalysisTab = "rotacao" | "comparacao" | "substituicoes";

export default function DeckAnalysisPage() {
  const params = useParams();
  const deckId = Number(params.id);
  const [activeTab, setActiveTab] = useState<AnalysisTab>("rotacao");

  const { data: deck, isLoading: isDeckLoading } = useDeck(deckId);

  if (isDeckLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" />
        <span className="ml-3 text-gray-500 text-lg">Carregando...</span>
      </div>
    );
  }

  if (!deck) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600 text-lg mb-4">Deck nao encontrado</p>
        <Link
          href="/decks"
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Voltar para Meus Decks
        </Link>
      </div>
    );
  }

  const tabs: { key: AnalysisTab; label: string }[] = [
    { key: "rotacao", label: "Rotacao" },
    { key: "comparacao", label: "Comparacao" },
    { key: "substituicoes", label: "Substituicoes" },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href={`/decks/${deckId}`}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          &larr; Voltar para {deck.name}
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">
          Analise - {deck.name}
        </h1>
        {deck.archetype && (
          <p className="text-sm text-gray-500 mt-1">{deck.archetype}</p>
        )}
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="flex border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "text-primary-700 border-b-2 border-primary-600 bg-primary-50"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === "rotacao" && <RotationTab deckId={deckId} />}
          {activeTab === "comparacao" && (
            <ComparisonTab deckId={deckId} deckName={deck.name} />
          )}
          {activeTab === "substituicoes" && <SubstitutionsTab deckId={deckId} />}
        </div>
      </div>
    </div>
  );
}

/* ===== Rotation Tab ===== */

function RotationTab({ deckId }: { deckId: number }) {
  const { data: report, isLoading, error } = useRotationAnalysis(deckId);

  if (isLoading) {
    return <LoadingSpinner text="Analisando rotacao..." />;
  }

  if (error || !report) {
    return <ErrorMessage text="Erro ao analisar rotacao" />;
  }

  const severityColor = SEVERITY_COLORS[report.severity as Severity] || "#6B7280";

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard label="Total de Cartas" value={String(report.total_cards)} />
        <StatCard
          label="Cartas Rotacionando"
          value={String(report.rotating_cards)}
          highlight={report.rotating_cards > 0}
        />
        <StatCard
          label="Cartas Ilegais"
          value={String(report.illegal_cards)}
          highlight={report.illegal_cards > 0}
        />
        <StatCard label="Cartas Seguras" value={String(report.safe_cards)} />
      </div>

      {/* Severity badge */}
      <div className="flex items-center gap-4 p-4 rounded-xl bg-gray-50">
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center text-white text-xl font-bold flex-shrink-0"
          style={{ backgroundColor: severityColor }}
        >
          {Math.round(report.rotation_percentage)}%
        </div>
        <div>
          <p className="text-lg font-semibold text-gray-900">
            Severidade:{" "}
            <span style={{ color: severityColor }}>
              {formatSeverity(report.severity)}
            </span>
          </p>
          <p className="text-sm text-gray-500">
            {report.rotation_percentage.toFixed(1)}% do deck sera afetado pela
            rotacao
          </p>
          {report.problem_percentage > 0 && (
            <p className="text-sm text-red-600">
              {report.problem_percentage.toFixed(1)}% de cartas com problemas
            </p>
          )}
        </div>
      </div>

      {/* Breakdown by type */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Detalhamento por Tipo
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <BreakdownCard
            title="Pokemon"
            breakdown={report.breakdown.pokemon}
            color="blue"
          />
          <BreakdownCard
            title="Treinadores"
            breakdown={report.breakdown.trainers}
            color="purple"
          />
          <BreakdownCard
            title="Energias"
            breakdown={report.breakdown.energy}
            color="yellow"
          />
        </div>
      </div>

      {/* Rotating cards list */}
      {report.rotating_card_list && report.rotating_card_list.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Cartas Rotacionando ({report.rotating_card_list.length})
          </h3>
          <div className="bg-red-50 rounded-xl border border-red-100 divide-y divide-red-100">
            {report.rotating_card_list.map((card, idx) => (
              <RotatingCardRow key={idx} card={card} />
            ))}
          </div>
        </div>
      )}

      {/* Regulation marks legend */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Marcas de Regulacao
        </h3>
        <div className="flex flex-wrap gap-3">
          {(
            Object.entries(REGULATION_MARKS) as [
              string,
              { label: string; color: string },
            ][]
          ).map(([mark, info]) => (
            <div
              key={mark}
              className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2"
            >
              <span
                className="w-6 h-6 rounded flex items-center justify-center text-white text-xs font-bold"
                style={{ backgroundColor: info.color }}
              >
                {mark}
              </span>
              <span className="text-sm text-gray-700">{info.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RotatingCardRow({ card }: { card: RotationCardOut }) {
  return (
    <div className="flex items-center justify-between px-4 py-2.5">
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-gray-600 w-6 text-right">
          {card.quantity}x
        </span>
        <span className="text-sm text-gray-900">{card.name}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500 capitalize">{card.card_type}</span>
        <span className="text-xs text-gray-400">
          {card.set_code} {card.set_number}
        </span>
        <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-red-500 text-white">
          {card.regulation_mark}
        </span>
      </div>
    </div>
  );
}

/* ===== Comparison Tab ===== */

function ComparisonTab({
  deckId,
  deckName,
}: {
  deckId: number;
  deckName: string;
}) {
  const { data: decks } = useDecks();
  const comparison = useDeckComparison();
  const matchup = useMatchupAnalysis();
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);

  const otherDecks = decks?.filter((d) => d.id !== deckId) || [];
  const selectedDeck = otherDecks.find((d) => d.id === selectedDeckId);

  const handleCompare = () => {
    if (!selectedDeckId) return;
    const params = {
      deck_a_id: deckId,
      deck_b_id: selectedDeckId,
      deck_a_name: deckName,
      deck_b_name: selectedDeck?.name || "Deck B",
    };
    comparison.mutate(params);
    matchup.mutate(params);
  };

  const isPending = comparison.isPending || matchup.isPending;

  return (
    <div className="space-y-6">
      {/* Deck selector */}
      <div className="flex flex-col sm:flex-row gap-3">
        <select
          value={selectedDeckId ?? ""}
          onChange={(e) =>
            setSelectedDeckId(e.target.value ? Number(e.target.value) : null)
          }
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="">Selecione um deck para comparar...</option>
          {otherDecks.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name} {d.archetype ? `(${d.archetype})` : ""}
            </option>
          ))}
        </select>
        <button
          onClick={handleCompare}
          disabled={!selectedDeckId || isPending}
          className="px-6 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isPending ? "Comparando..." : "Comparar"}
        </button>
      </div>

      {otherDecks.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          <p>Voce precisa de pelo menos dois decks para comparar.</p>
          <Link
            href="/decks/new"
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Criar outro deck
          </Link>
        </div>
      )}

      {(comparison.isError || matchup.isError) && (
        <ErrorMessage text="Erro ao comparar decks. Tente novamente." />
      )}

      {/* Results */}
      {comparison.data && (
        <ComparisonResults
          comparison={comparison.data}
          matchup={matchup.data || null}
        />
      )}
    </div>
  );
}

function ComparisonResults({
  comparison,
  matchup,
}: {
  comparison: DeckComparisonOut;
  matchup: MatchupAnalysisOut | null;
}) {
  return (
    <div className="space-y-6">
      {/* Similarity */}
      <div className="flex items-center gap-4 p-4 rounded-xl bg-gray-50">
        <div className="w-16 h-16 rounded-full flex items-center justify-center bg-blue-600 text-white text-xl font-bold flex-shrink-0">
          {Math.round(comparison.similarity_percentage)}%
        </div>
        <div>
          <p className="text-lg font-semibold text-gray-900">Similaridade</p>
          <p className="text-sm text-gray-500">
            {comparison.shared_count} cartas em comum entre{" "}
            <strong>{comparison.deck_a_name}</strong> e{" "}
            <strong>{comparison.deck_b_name}</strong>
          </p>
        </div>
      </div>

      {/* Matchup scores */}
      {matchup && (
        <>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Pontuacoes
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <ScoreBar
                label="Velocidade"
                scoreA={matchup.speed_score_a}
                scoreB={matchup.speed_score_b}
                nameA={comparison.deck_a_name}
                nameB={comparison.deck_b_name}
              />
              <ScoreBar
                label="Consistencia"
                scoreA={matchup.consistency_score_a}
                scoreB={matchup.consistency_score_b}
                nameA={comparison.deck_a_name}
                nameB={comparison.deck_b_name}
              />
              <ScoreBar
                label="Poder"
                scoreA={matchup.power_score_a}
                scoreB={matchup.power_score_b}
                nameA={comparison.deck_a_name}
                nameB={comparison.deck_b_name}
              />
            </div>
          </div>

          {/* Matchup favor */}
          {matchup.matchup_favor && (
            <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
              <p className="text-sm font-medium text-blue-900">
                Favorecimento: {matchup.matchup_favor}
              </p>
            </div>
          )}

          {/* Advantages */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {matchup.a_advantages.length > 0 && (
              <div className="bg-green-50 rounded-xl p-4 border border-green-100">
                <h4 className="font-semibold text-green-800 mb-2">
                  Vantagens de {comparison.deck_a_name}
                </h4>
                <ul className="space-y-1">
                  {matchup.a_advantages.map((adv, i) => (
                    <li
                      key={i}
                      className="text-sm text-green-700 flex items-start gap-2"
                    >
                      <span className="mt-1.5 w-1.5 h-1.5 bg-green-500 rounded-full flex-shrink-0" />
                      {adv}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {matchup.b_advantages.length > 0 && (
              <div className="bg-orange-50 rounded-xl p-4 border border-orange-100">
                <h4 className="font-semibold text-orange-800 mb-2">
                  Vantagens de {comparison.deck_b_name}
                </h4>
                <ul className="space-y-1">
                  {matchup.b_advantages.map((adv, i) => (
                    <li
                      key={i}
                      className="text-sm text-orange-700 flex items-start gap-2"
                    >
                      <span className="mt-1.5 w-1.5 h-1.5 bg-orange-500 rounded-full flex-shrink-0" />
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
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Diferencas Principais
              </h3>
              <ul className="space-y-2">
                {matchup.key_differences.map((diff, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-gray-700"
                  >
                    <span className="mt-1.5 w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                    {diff}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {/* Shared cards */}
      {comparison.shared_cards.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Cartas em Comum ({comparison.shared_cards.length})
          </h3>
          <div className="bg-gray-50 rounded-xl border border-gray-100 divide-y divide-gray-100 max-h-64 overflow-y-auto">
            {comparison.shared_cards.map((sc, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between px-4 py-2.5"
              >
                <span className="text-sm text-gray-900">{sc.name}</span>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span>{sc.quantity_a}x em A</span>
                  <span>{sc.quantity_b}x em B</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unique cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {comparison.unique_to_a.length > 0 && (
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-800 mb-2">
              Exclusivas de {comparison.deck_a_name} (
              {comparison.unique_to_a.length})
            </h4>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {comparison.unique_to_a.map((card, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{card.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{card.quantity}x</span>
                    <span className="text-xs text-gray-400 capitalize">
                      {card.card_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {comparison.unique_to_b.length > 0 && (
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-800 mb-2">
              Exclusivas de {comparison.deck_b_name} (
              {comparison.unique_to_b.length})
            </h4>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {comparison.unique_to_b.map((card, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{card.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{card.quantity}x</span>
                    <span className="text-xs text-gray-400 capitalize">
                      {card.card_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ===== Substitutions Tab ===== */

function SubstitutionsTab({ deckId }: { deckId: number }) {
  const { data: substitutions, isLoading, error } = useSubstitutions(deckId);

  if (isLoading) {
    return <LoadingSpinner text="Buscando substituicoes..." />;
  }

  if (error) {
    return <ErrorMessage text="Erro ao buscar substituicoes" />;
  }

  if (!substitutions || substitutions.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
          <svg
            className="w-8 h-8 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <p className="text-lg font-medium text-gray-900">
          Nenhuma substituicao necessaria
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Seu deck nao possui cartas que precisem de substituicao.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 mb-4">
        Sugestoes de substituicao para cartas que serao rotacionadas ou precisam
        de alternativa.
      </p>
      {substitutions.map((sub, index) => (
        <SubstitutionCard key={index} substitution={sub} />
      ))}
    </div>
  );
}

function SubstitutionCard({
  substitution,
}: {
  substitution: SubstitutionSuggestionOut;
}) {
  const matchPercentage = Math.round(substitution.match_score);

  return (
    <div className="border border-gray-200 rounded-xl p-4 hover:shadow-sm transition-shadow">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        {/* Original card */}
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">
            Original
          </p>
          <p className="font-medium text-gray-900 truncate">
            {substitution.original_name}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            {substitution.original_set_code} {substitution.original_set_number}
          </p>
        </div>

        {/* Arrow */}
        <div className="hidden sm:flex items-center">
          <svg
            className="w-8 h-8 text-gray-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </div>
        <div className="sm:hidden text-center text-gray-300 text-lg">
          &darr;
        </div>

        {/* Suggested card */}
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">
            Sugestao
          </p>
          <p className="font-medium text-primary-700 truncate">
            {substitution.suggested_name}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            {substitution.suggested_set_code}{" "}
            {substitution.suggested_set_number}
          </p>
        </div>

        {/* Match score */}
        <div className="flex-shrink-0">
          <div
            className={`w-14 h-14 rounded-full flex items-center justify-center text-white text-sm font-bold ${
              matchPercentage >= 80
                ? "bg-green-500"
                : matchPercentage >= 60
                  ? "bg-yellow-500"
                  : "bg-orange-500"
            }`}
          >
            {matchPercentage}%
          </div>
        </div>
      </div>

      {/* Reasons */}
      {substitution.reasons.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <ul className="flex flex-wrap gap-2">
            {substitution.reasons.map((reason, i) => (
              <li
                key={i}
                className="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full"
              >
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/* ===== Shared Components ===== */

function StatCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-xl p-4 text-center ${
        highlight ? "bg-red-50 border border-red-100" : "bg-gray-50"
      }`}
    >
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function BreakdownCard({
  title,
  breakdown,
  color,
}: {
  title: string;
  breakdown: { rotating: number; illegal: number; safe: number };
  color: string;
}) {
  const total = breakdown.rotating + breakdown.illegal + breakdown.safe;
  const colorClasses: Record<string, string> = {
    blue: "bg-blue-50 border-blue-100",
    purple: "bg-purple-50 border-purple-100",
    yellow: "bg-yellow-50 border-yellow-100",
  };

  return (
    <div
      className={`rounded-xl p-4 border ${colorClasses[color] || "bg-gray-50"}`}
    >
      <h4 className="font-semibold text-gray-800 mb-3">{title}</h4>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-green-600">Seguras</span>
          <span className="font-medium">{breakdown.safe}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-red-500">Rotacionando</span>
          <span className="font-medium">{breakdown.rotating}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Ilegais</span>
          <span className="font-medium">{breakdown.illegal}</span>
        </div>
        {total > 0 && (
          <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden flex">
            {breakdown.safe > 0 && (
              <div
                className="bg-green-500 h-full"
                style={{ width: `${(breakdown.safe / total) * 100}%` }}
              />
            )}
            {breakdown.rotating > 0 && (
              <div
                className="bg-red-500 h-full"
                style={{ width: `${(breakdown.rotating / total) * 100}%` }}
              />
            )}
            {breakdown.illegal > 0 && (
              <div
                className="bg-gray-400 h-full"
                style={{ width: `${(breakdown.illegal / total) * 100}%` }}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ScoreBar({
  label,
  scoreA,
  scoreB,
  nameA = "Deck A",
  nameB = "Deck B",
}: {
  label: string;
  scoreA: number;
  scoreB: number;
  nameA?: string;
  nameB?: string;
}) {
  const maxScore = Math.max(scoreA, scoreB, 1);

  return (
    <div className="bg-gray-50 rounded-xl p-4">
      <p className="text-sm font-semibold text-gray-700 mb-3">{label}</p>
      <div className="space-y-2">
        <div>
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span className="truncate max-w-[120px]">{nameA}</span>
            <span>{scoreA}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all"
              style={{ width: `${(scoreA / maxScore) * 100}%` }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span className="truncate max-w-[120px]">{nameB}</span>
            <span>{scoreB}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-orange-500 rounded-full transition-all"
              style={{ width: `${(scoreB / maxScore) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingSpinner({ text }: { text: string }) {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      <span className="ml-3 text-gray-500">{text}</span>
    </div>
  );
}

function ErrorMessage({ text }: { text: string }) {
  return (
    <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm text-center">
      {text}
    </div>
  );
}

function formatSeverity(severity: string): string {
  const map: Record<string, string> = {
    NONE: "Nenhuma",
    LOW: "Baixa",
    MODERATE: "Moderada",
    HIGH: "Alta",
    CRITICAL: "Critica",
  };
  return map[severity] || severity;
}
