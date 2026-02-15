"use client";

import { useState } from "react";
import { useTournaments, useNews } from "@/hooks/useTournaments";
import TournamentCard from "@/components/tournament/TournamentCard";
import NewsCard from "@/components/tournament/NewsCard";

export default function TournamentsPage() {
  const [activeTab, setActiveTab] = useState<"tournaments" | "news">("tournaments");
  const { data: tournaments, isLoading: tournamentsLoading } = useTournaments();
  const { data: news, isLoading: newsLoading } = useNews();

  const tabs = [
    { id: "tournaments" as const, label: "Calendario", count: tournaments?.length },
    { id: "news" as const, label: "Noticias", count: news?.length },
  ];

  // Split tournaments into upcoming and past
  const now = new Date();
  const upcoming = tournaments?.filter((t) => {
    if (!t.date) return true;
    return new Date(t.date) >= now;
  }) || [];
  const past = tournaments?.filter((t) => {
    if (!t.date) return false;
    return new Date(t.date) < now;
  }) || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Torneios e Noticias</h1>
      <p className="text-gray-500 mb-6">Calendario de torneios Pokemon TCG e ultimas noticias.</p>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 mb-6 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span className="ml-1.5 text-xs text-gray-400">({tab.count})</span>
            )}
          </button>
        ))}
      </div>

      {/* Tournaments Tab */}
      {activeTab === "tournaments" && (
        <div>
          {tournamentsLoading ? (
            <div className="text-center py-10 text-gray-500">Carregando torneios...</div>
          ) : tournaments?.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
              <p className="text-gray-500 text-lg">Nenhum torneio encontrado</p>
              <p className="text-gray-400 text-sm mt-1">Os torneios serao sincronizados automaticamente.</p>
            </div>
          ) : (
            <div className="space-y-8">
              {upcoming.length > 0 && (
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500" />
                    Proximos
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {upcoming.map((t) => (
                      <TournamentCard key={t.id} tournament={t} />
                    ))}
                  </div>
                </div>
              )}

              {past.length > 0 && (
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gray-400" />
                    Anteriores
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {past.map((t) => (
                      <TournamentCard key={t.id} tournament={t} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* News Tab */}
      {activeTab === "news" && (
        <div>
          {newsLoading ? (
            <div className="text-center py-10 text-gray-500">Carregando noticias...</div>
          ) : news?.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
              <p className="text-gray-500 text-lg">Nenhuma noticia encontrada</p>
              <p className="text-gray-400 text-sm mt-1">As noticias serao sincronizadas automaticamente.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {news?.map((article) => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
