"use client";

import { useState } from "react";
import { useMetaDecks, useMetaMatchups } from "@/hooks/useMeta";
import { TierList } from "@/components/meta/TierList";
import { MatchupMatrix } from "@/components/meta/MatchupMatrix";

type TabView = "tiers" | "matchups";

export default function MetaPage() {
  const { data: metaDecks, isLoading: loadingDecks, error: decksError } = useMetaDecks();
  const { data: matchups, isLoading: loadingMatchups, error: matchupsError } = useMetaMatchups();
  const [activeTab, setActiveTab] = useState<TabView>("tiers");

  if (loadingDecks) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4" />
        <p className="text-gray-500">Carregando meta decks...</p>
      </div>
    );
  }

  if (decksError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <svg className="w-10 h-10 text-red-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.27 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <p className="text-red-700 font-medium">Erro ao carregar meta decks</p>
        <p className="text-red-500 text-sm mt-1">Verifique sua conexao e tente novamente</p>
      </div>
    );
  }

  if (!metaDecks || metaDecks.length === 0) {
    return (
      <div className="text-center py-20 text-gray-500">
        <p className="text-lg">Nenhum meta deck encontrado</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Meta Game</h1>
        <p className="text-gray-500 text-sm mt-1">
          Analise dos melhores decks do formato competitivo atual
        </p>
      </div>

      {/* Tab navigation */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        <button
          onClick={() => setActiveTab("tiers")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === "tiers"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
            </svg>
            Tier List
          </span>
        </button>
        <button
          onClick={() => setActiveTab("matchups")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === "matchups"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18M10 3v18M14 3v18" />
            </svg>
            Matriz de Matchups
          </span>
        </button>
      </div>

      {/* Tab content */}
      {activeTab === "tiers" && (
        <TierList metaDecks={metaDecks} />
      )}

      {activeTab === "matchups" && (
        <div>
          {loadingMatchups ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3" />
              <p className="text-gray-500 text-sm">Carregando matchups...</p>
            </div>
          ) : matchupsError ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <p className="text-red-700 text-sm">Erro ao carregar matchups</p>
            </div>
          ) : matchups && matchups.length > 0 ? (
            <div className="bg-white border border-gray-200 rounded-lg p-4 overflow-hidden">
              <h2 className="font-semibold text-gray-800 mb-4">
                Matriz de Confrontos
              </h2>
              <MatchupMatrix matchups={matchups} metaDecks={metaDecks} />
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Nenhum dado de matchup disponivel</p>
            </div>
          )}
        </div>
      )}

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          label="Total de Decks"
          value={metaDecks.length}
          icon={
            <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          }
        />
        <SummaryCard
          label="Tier 1"
          value={metaDecks.filter((d) => d.tier === 1).length}
          icon={
            <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          }
        />
        <SummaryCard
          label="Matchups"
          value={matchups?.length || 0}
          icon={
            <svg className="w-5 h-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          }
        />
        <SummaryCard
          label="Meta Share Total"
          value={`${metaDecks.reduce((sum, d) => sum + d.meta_share, 0).toFixed(0)}%`}
          icon={
            <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            </svg>
          }
        />
      </div>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: number | string;
  icon: React.ReactNode;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 flex items-center gap-3">
      <div className="bg-gray-50 rounded-lg p-2">{icon}</div>
      <div>
        <div className="text-lg font-bold text-gray-900">{value}</div>
        <div className="text-xs text-gray-500">{label}</div>
      </div>
    </div>
  );
}
