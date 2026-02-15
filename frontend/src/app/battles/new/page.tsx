"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useDecks } from "@/hooks/useDecks";
import { useCreateBattle } from "@/hooks/useBattles";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { MetaDeck, BattleResult } from "@/lib/types";

export default function NewBattlePage() {
  const router = useRouter();
  const { data: decks } = useDecks();
  const { data: metaDecks } = useQuery<MetaDeck[]>({
    queryKey: ["meta", "decks"],
    queryFn: async () => {
      const { data } = await api.get("/meta/decks");
      return data;
    },
  });
  const createBattle = useCreateBattle();

  const [deckId, setDeckId] = useState<number | null>(null);
  const [opponentName, setOpponentName] = useState("");
  const [opponentMetaId, setOpponentMetaId] = useState("");
  const [result, setResult] = useState<BattleResult | null>(null);
  const [totalTurns, setTotalTurns] = useState<string>("");
  const [wentFirst, setWentFirst] = useState<boolean | null>(null);
  const [notes, setNotes] = useState("");

  const handleSubmit = () => {
    if (!deckId || !result) return;
    createBattle.mutate(
      {
        deck_id: deckId,
        opponent_deck_name: opponentName || undefined,
        opponent_meta_deck_id: opponentMetaId || undefined,
        result,
        total_turns: totalTurns ? parseInt(totalTurns) : undefined,
        went_first: wentFirst ?? undefined,
        notes: notes || undefined,
      },
      { onSuccess: () => router.push("/battles") }
    );
  };

  const resultOptions: {
    value: BattleResult;
    label: string;
    color: string;
    activeColor: string;
  }[] = [
    {
      value: "win",
      label: "Vitoria",
      color: "border-green-300 text-green-700 hover:bg-green-50",
      activeColor:
        "bg-green-100 border-green-500 text-green-800 ring-2 ring-green-500",
    },
    {
      value: "loss",
      label: "Derrota",
      color: "border-red-300 text-red-700 hover:bg-red-50",
      activeColor:
        "bg-red-100 border-red-500 text-red-800 ring-2 ring-red-500",
    },
    {
      value: "draw",
      label: "Empate",
      color: "border-yellow-300 text-yellow-700 hover:bg-yellow-50",
      activeColor:
        "bg-yellow-100 border-yellow-500 text-yellow-800 ring-2 ring-yellow-500",
    },
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Registrar Batalha
      </h1>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
        {/* Deck */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Seu Deck *
          </label>
          <select
            value={deckId ?? ""}
            onChange={(e) => setDeckId(Number(e.target.value) || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Selecione um deck...</option>
            {decks?.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>

        {/* Opponent */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Oponente
          </label>
          <input
            type="text"
            value={opponentName}
            onChange={(e) => setOpponentName(e.target.value)}
            placeholder="Nome do deck oponente..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 mb-2"
          />
          <select
            value={opponentMetaId}
            onChange={(e) => {
              setOpponentMetaId(e.target.value);
              if (e.target.value) {
                const meta = metaDecks?.find(
                  (m) => String(m.id) === e.target.value
                );
                if (meta) setOpponentName(meta.name_pt || meta.name_en);
              }
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Ou selecione deck do meta...</option>
            {metaDecks?.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name_pt || d.name_en} (Tier {d.tier})
              </option>
            ))}
          </select>
        </div>

        {/* Result */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resultado *
          </label>
          <div className="flex gap-3">
            {resultOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setResult(opt.value)}
                className={`flex-1 py-3 rounded-lg border-2 font-medium transition-all ${
                  result === opt.value ? opt.activeColor : opt.color
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Turns + Went First */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Turnos
            </label>
            <input
              type="number"
              value={totalTurns}
              onChange={(e) => setTotalTurns(e.target.value)}
              placeholder="Ex: 8"
              min="1"
              max="50"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quem comecou?
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setWentFirst(true)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-all ${
                  wentFirst === true
                    ? "bg-primary-100 border-primary-500 text-primary-800 ring-2 ring-primary-500"
                    : "border-gray-300 text-gray-600 hover:bg-gray-50"
                }`}
              >
                Eu
              </button>
              <button
                onClick={() => setWentFirst(false)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-all ${
                  wentFirst === false
                    ? "bg-primary-100 border-primary-500 text-primary-800 ring-2 ring-primary-500"
                    : "border-gray-300 text-gray-600 hover:bg-gray-50"
                }`}
              >
                Oponente
              </button>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notas
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Observacoes sobre a partida..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 resize-none"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!deckId || !result || createBattle.isPending}
          className="w-full py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-gray-300 transition-colors"
        >
          {createBattle.isPending ? "Salvando..." : "Registrar Batalha"}
        </button>
      </div>
    </div>
  );
}
