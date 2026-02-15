"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { UserStats } from "@/lib/types";
import { useBattleStats } from "@/hooks/useBattles";

export default function StatsPage() {
  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ["stats", "user"],
    queryFn: async () => {
      const { data } = await api.get("/stats/user");
      return data;
    },
  });

  const { data: battleStats } = useBattleStats();

  if (isLoading) {
    return (
      <div className="text-center py-10">Carregando estatisticas...</div>
    );
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
        <div className="space-y-6">
          {/* Overview cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="Batalhas"
              value={stats.total_battles.toString()}
            />
            <StatCard
              title="Taxa de Vitoria"
              value={`${stats.win_rate.toFixed(1)}%`}
              color={stats.win_rate >= 50 ? "green" : "red"}
            />
            <StatCard title="Decks" value={stats.total_decks.toString()} />
            {stats.most_played_deck && (
              <StatCard
                title="Deck Favorito"
                value={stats.most_played_deck}
              />
            )}
          </div>

          {/* Win/Loss bar */}
          {stats.total_battles > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="font-semibold text-gray-900 mb-4">
                Distribuicao de Resultados
              </h2>
              <div className="flex h-8 rounded-lg overflow-hidden mb-3">
                {stats.win_rate > 0 && (
                  <div
                    className="bg-green-500 flex items-center justify-center text-white text-xs font-bold"
                    style={{ width: `${stats.win_rate}%` }}
                  >
                    {stats.win_rate > 10
                      ? `${stats.win_rate.toFixed(0)}%`
                      : ""}
                  </div>
                )}
                {stats.total_battles -
                  (stats.total_battles * stats.win_rate) / 100 >
                  0 && (
                  <div className="bg-red-500 flex-1 flex items-center justify-center text-white text-xs font-bold">
                    {stats.win_rate < 90
                      ? `${(100 - stats.win_rate).toFixed(0)}%`
                      : ""}
                  </div>
                )}
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-green-600 font-medium">Vitorias</span>
                <span className="text-red-600 font-medium">Derrotas</span>
              </div>
            </div>
          )}

          {/* Battle detailed stats */}
          {battleStats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* First/Second stats */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h2 className="font-semibold text-gray-900 mb-4">
                  Comecando Primeiro vs Segundo
                </h2>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Comecando primeiro</span>
                    <span className="font-bold text-gray-900">
                      {battleStats.went_first_win_rate}% WR
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-primary-500 h-3 rounded-full"
                      style={{
                        width: `${battleStats.went_first_win_rate}%`,
                      }}
                    />
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Comecando segundo</span>
                    <span className="font-bold text-gray-900">
                      {battleStats.went_second_win_rate}% WR
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-indigo-500 h-3 rounded-full"
                      style={{
                        width: `${battleStats.went_second_win_rate}%`,
                      }}
                    />
                  </div>
                </div>
                {battleStats.avg_turns > 0 && (
                  <p className="text-sm text-gray-500 mt-4">
                    Media de turnos: {battleStats.avg_turns}
                  </p>
                )}
              </div>

              {/* By opponent */}
              {battleStats.results_by_opponent?.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h2 className="font-semibold text-gray-900 mb-4">
                    Resultados por Oponente
                  </h2>
                  <div className="space-y-2">
                    {battleStats.results_by_opponent
                      .slice(0, 8)
                      .map(
                        (
                          opp: {
                            opponent: string;
                            wins: number;
                            losses: number;
                            ties: number;
                            total: number;
                          },
                          i: number
                        ) => {
                          const wr =
                            opp.total > 0
                              ? Math.round((opp.wins / opp.total) * 100)
                              : 0;
                          return (
                            <div
                              key={i}
                              className="flex items-center justify-between py-1"
                            >
                              <span className="text-sm text-gray-700 truncate max-w-[60%]">
                                {opp.opponent}
                              </span>
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-gray-500">
                                  {opp.wins}V {opp.losses}D
                                </span>
                                <span
                                  className={`text-sm font-bold ${
                                    wr >= 50
                                      ? "text-green-600"
                                      : "text-red-600"
                                  }`}
                                >
                                  {wr}%
                                </span>
                              </div>
                            </div>
                          );
                        }
                      )}
                  </div>
                </div>
              )}
            </div>
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
