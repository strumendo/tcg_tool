"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Deck, MetaDeck, SimulationResult } from "@/lib/types";

export default function SimulationPage() {
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [selectedOpponent, setSelectedOpponent] = useState<string>("");
  const [turns, setTurns] = useState(6);

  const { data: decks } = useQuery<Deck[]>({
    queryKey: ["decks"],
    queryFn: async () => {
      const { data } = await api.get("/decks");
      return data;
    },
  });

  const { data: metaDecks } = useQuery<MetaDeck[]>({
    queryKey: ["meta", "decks"],
    queryFn: async () => {
      const { data } = await api.get("/meta/decks");
      return data;
    },
  });

  const simulate = useMutation<SimulationResult>({
    mutationFn: async () => {
      const { data } = await api.post("/simulation/play-sequence", {
        deck_id: selectedDeck,
        opponent_meta_deck_id: selectedOpponent,
        turns,
      });
      return data;
    },
  });

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">
        Simulacao de Jogadas
      </h1>
      <p className="text-gray-500 mb-6">
        Simule sequencias de jogo otimizadas contra decks do meta usando IA.
      </p>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Seu Deck
            </label>
            <select
              value={selectedDeck || ""}
              onChange={(e) => setSelectedDeck(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Selecione...</option>
              {decks?.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Deck Oponente
            </label>
            <select
              value={selectedOpponent}
              onChange={(e) => setSelectedOpponent(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Selecione...</option>
              {metaDecks?.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name_pt || d.name_en} (Tier {d.tier})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Turnos
            </label>
            <input
              type="number"
              value={turns}
              onChange={(e) => setTurns(parseInt(e.target.value) || 6)}
              min={1}
              max={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <button
          onClick={() => simulate.mutate()}
          disabled={!selectedDeck || !selectedOpponent || simulate.isPending}
          className="w-full py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-gray-300 transition-colors"
        >
          {simulate.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="w-5 h-5 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="3"
                  className="opacity-25"
                />
                <path
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  fill="currentColor"
                  className="opacity-75"
                />
              </svg>
              Simulando...
            </span>
          ) : (
            "Simular Jogadas"
          )}
        </button>
      </div>

      {/* Results */}
      {simulate.data && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-primary-600 to-indigo-600 p-6 text-white">
            <h2 className="text-xl font-bold">
              {simulate.data.deck_name} vs {simulate.data.opponent_name}
            </h2>
            <p className="text-primary-100 text-sm">
              {simulate.data.total_turns} turnos simulados
            </p>
          </div>

          {/* Analysis text */}
          <div className="p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Analise</h3>
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap mb-6">
              {simulate.data.analysis}
            </div>

            {/* Turn sequence */}
            {simulate.data.turns?.length > 0 && (
              <>
                <h3 className="font-semibold text-gray-900 mb-3">
                  Sequencia de Jogadas
                </h3>
                <div className="space-y-3 mb-6">
                  {simulate.data.turns.map((turn) => (
                    <div
                      key={turn.turn}
                      className="border-l-4 border-primary-500 pl-4 py-2 bg-gray-50 rounded-r-lg"
                    >
                      <p className="font-medium text-gray-900">
                        Turno {turn.turn}: {turn.action}
                      </p>
                      {turn.card_name && (
                        <p className="text-sm text-gray-600">
                          Carta: {turn.card_name}
                        </p>
                      )}
                      <p className="text-sm text-gray-500">{turn.reasoning}</p>
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* Insights */}
            {simulate.data.key_insights?.length > 0 && (
              <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                <h3 className="font-semibold text-purple-900 mb-2">
                  Insights Chave
                </h3>
                <ul className="space-y-1">
                  {simulate.data.key_insights.map((insight, i) => (
                    <li
                      key={i}
                      className="text-sm text-purple-700 flex gap-2"
                    >
                      <span className="text-purple-400">&bull;</span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {simulate.isError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          Erro ao simular. Verifique se o servico de IA esta disponivel.
        </div>
      )}
    </div>
  );
}
