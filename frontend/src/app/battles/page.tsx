"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Battle } from "@/lib/types";

export default function BattlesPage() {
  const { data: battles, isLoading } = useQuery<Battle[]>({
    queryKey: ["battles"],
    queryFn: async () => {
      const { data } = await api.get("/battles");
      return data;
    },
  });

  if (isLoading) {
    return <div className="text-center py-10">Carregando batalhas...</div>;
  }

  const resultColors: Record<string, string> = {
    win: "bg-green-100 text-green-700",
    loss: "bg-red-100 text-red-700",
    draw: "bg-yellow-100 text-yellow-700",
  };

  const resultLabels: Record<string, string> = {
    win: "Vitoria",
    loss: "Derrota",
    draw: "Empate",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Batalhas</h1>
        <Link
          href="/battles/new"
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Registrar Batalha
        </Link>
      </div>

      {!battles || battles.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
          <p className="text-gray-500 text-lg mb-4">
            Nenhuma batalha registrada
          </p>
          <Link
            href="/battles/new"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Registrar primeira batalha
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 divide-y">
          {battles.map((battle) => (
            <Link
              key={battle.id}
              href={`/battles/${battle.id}`}
              className="block p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">
                    vs {battle.opponent_deck_name || "Oponente desconhecido"}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(battle.played_at).toLocaleDateString("pt-BR")}
                    {battle.total_turns && ` - ${battle.total_turns} turnos`}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${resultColors[battle.result]}`}
                >
                  {resultLabels[battle.result]}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
