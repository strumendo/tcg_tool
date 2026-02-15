"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { UserStats } from "@/lib/types";

export default function StatsPage() {
  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ["stats", "summary"],
    queryFn: async () => {
      const { data } = await api.get("/stats/user/summary");
      return data;
    },
  });

  if (isLoading) {
    return <div className="text-center py-10">Carregando estatisticas...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Relatorio Estatistico
      </h1>

      {!stats ? (
        <p className="text-gray-500 text-center py-10">
          Nenhum dado disponivel. Registre batalhas para ver estatisticas.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatCard
            title="Total de Batalhas"
            value={stats.total_battles.toString()}
          />
          <StatCard
            title="Taxa de Vitoria"
            value={`${stats.win_rate.toFixed(1)}%`}
            color={stats.win_rate >= 50 ? "green" : "red"}
          />
          <StatCard
            title="Total de Decks"
            value={stats.total_decks.toString()}
          />
          {stats.most_played_deck && (
            <StatCard
              title="Deck Mais Usado"
              value={stats.most_played_deck}
            />
          )}
          {stats.best_matchup && (
            <StatCard
              title="Melhor Matchup"
              value={stats.best_matchup}
              color="green"
            />
          )}
          {stats.worst_matchup && (
            <StatCard
              title="Pior Matchup"
              value={stats.worst_matchup}
              color="red"
            />
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({
  title,
  value,
  color = "gray",
}: {
  title: string;
  value: string;
  color?: string;
}) {
  const colorClasses: Record<string, string> = {
    gray: "bg-gray-50 border-gray-200",
    green: "bg-green-50 border-green-200",
    red: "bg-red-50 border-red-200",
  };

  return (
    <div className={`rounded-xl border p-6 ${colorClasses[color]}`}>
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
