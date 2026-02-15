"use client";

import type { Tournament } from "@/lib/types";

interface TournamentCardProps {
  tournament: Tournament;
}

export default function TournamentCard({ tournament }: TournamentCardProps) {
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const startDate = formatDate(tournament.date);
  const endDate = formatDate(tournament.end_date);
  const dateDisplay = startDate
    ? endDate && endDate !== startDate
      ? `${startDate} - ${endDate}`
      : startDate
    : "Data a definir";

  const eventTypeColors: Record<string, string> = {
    tournament: "bg-blue-100 text-blue-700",
    league: "bg-green-100 text-green-700",
    cup: "bg-purple-100 text-purple-700",
    challenge: "bg-orange-100 text-orange-700",
    regional: "bg-red-100 text-red-700",
    international: "bg-indigo-100 text-indigo-700",
    worlds: "bg-yellow-100 text-yellow-800",
  };

  const typeColor = eventTypeColors[tournament.event_type?.toLowerCase() || ""] || "bg-gray-100 text-gray-700";

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{tournament.name}</h3>
          <div className="mt-2 space-y-1">
            <p className="text-sm text-gray-600 flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {dateDisplay}
            </p>
            {tournament.location && (
              <p className="text-sm text-gray-600 flex items-center gap-2">
                <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {tournament.location}
                {tournament.country && `, ${tournament.country}`}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          {tournament.event_type && (
            <span className={`text-xs px-2.5 py-1 rounded-full font-medium capitalize ${typeColor}`}>
              {tournament.event_type}
            </span>
          )}
          <span className="text-xs px-2.5 py-1 rounded-full bg-gray-100 text-gray-600">
            {tournament.format}
          </span>
        </div>
      </div>

      {tournament.url && (
        <a
          href={tournament.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Ver detalhes
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}
    </div>
  );
}
