"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Deck, MetaDeck, SimulationResult } from "@/lib/types";

export default function SimulationPage() {
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [selectedOpponent, setSelectedOpponent] = useState<string>("");

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
        turns: 6,
      });
      return data;
    },
  });

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Simulacao de Jogadas
      </h1>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Seu Deck
            </label>
            <select
              value={selectedDeck || ""}
              onChange={(e) => setSelectedDeck(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
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
              Deck Oponente (Meta)
            </label>
            <select
              value={selectedOpponent}
              onChange={(e) => setSelectedOpponent(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Selecione...</option>
              {metaDecks?.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name_pt || d.name_en} (Tier {d.tier})
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={() => simulate.mutate()}
          disabled={!selectedDeck || !selectedOpponent || simulate.isPending}
          className="w-full py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-gray-300 transition-colors"
        >
          {simulate.isPending ? "Simulando..." : "Simular Jogadas"}
        </button>
      </div>

      {/* Results */}
      {simulate.data && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">
            {simulate.data.deck_name} vs {simulate.data.opponent_name}
          </h2>

          <div className="space-y-4 mb-6">
            {simulate.data.turns.map((turn) => (
              <div
                key={turn.turn}
                className="border-l-4 border-primary-500 pl-4 py-2"
              >
                <p className="font-medium text-gray-900">
                  Turno {turn.turn}: {turn.action}
                </p>
                {turn.card_name && (
                  <p className="text-sm text-gray-600">Carta: {turn.card_name}</p>
                )}
                <p className="text-sm text-gray-500">{turn.reasoning}</p>
              </div>
            ))}
          </div>

          {simulate.data.key_insights.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Insights</h3>
              <ul className="list-disc list-inside text-sm text-gray-600">
                {simulate.data.key_insights.map((insight, i) => (
                  <li key={i}>{insight}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
