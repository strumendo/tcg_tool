"use client";

import { useCardUsage } from "@/hooks/useCards";

interface CardUsageChartProps {
  cardId: number;
}

export function CardUsageChart({ cardId }: CardUsageChartProps) {
  const { data: usage, isLoading, error } = useCardUsage(cardId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-500">Carregando estatisticas...</p>
        </div>
      </div>
    );
  }

  if (error || !usage) {
    return (
      <div className="text-center py-12">
        <svg
          className="w-12 h-12 text-gray-300 mx-auto mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
        <p className="text-gray-500 text-sm">
          Dados de uso ainda nao disponiveis
        </p>
        <p className="text-gray-400 text-xs mt-1">
          Estatisticas serao exibidas quando houver dados suficientes
        </p>
      </div>
    );
  }

  const usagePercent = Math.min(usage.usage_percentage, 100);

  return (
    <div className="space-y-6">
      {/* Main stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Usage percentage */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
            Taxa de Uso
          </p>
          <p className="text-3xl font-bold text-gray-900">
            {usage.usage_percentage.toFixed(1)}%
          </p>
          <div className="mt-3 w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${usagePercent}%`,
                backgroundColor: getUsageColor(usagePercent),
              }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-1.5">dos decks do meta</p>
        </div>

        {/* Average copies */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
            Media de Copias
          </p>
          <p className="text-3xl font-bold text-gray-900">
            {usage.avg_copies.toFixed(1)}
          </p>
          <div className="flex gap-1 mt-3">
            {[1, 2, 3, 4].map((n) => (
              <div
                key={n}
                className={`flex-1 h-2.5 rounded-full ${
                  n <= Math.round(usage.avg_copies)
                    ? "bg-primary-500"
                    : "bg-gray-100"
                }`}
              />
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-1.5">copias por deck</p>
        </div>

        {/* Sample size */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
            Amostra
          </p>
          <p className="text-3xl font-bold text-gray-900">
            {usage.sample_size}
          </p>
          <div className="mt-3 flex items-center gap-1.5">
            <svg
              className="w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <p className="text-xs text-gray-400">decks analisados</p>
          </div>
        </div>
      </div>

      {/* Usage bar visualization */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4">
          Distribuicao de Uso
        </h4>
        <div className="space-y-3">
          <UsageBar
            label="Uso no meta"
            value={usage.usage_percentage}
            maxValue={100}
            color={getUsageColor(usage.usage_percentage)}
          />
          <UsageBar
            label="Copias (media)"
            value={usage.avg_copies}
            maxValue={4}
            color="#6366F1"
          />
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-xs text-gray-500">Baixo (&lt;25%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-xs text-gray-500">Medio (25-60%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-xs text-gray-500">Alto (&gt;60%)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function UsageBar({
  label,
  value,
  maxValue,
  color,
}: {
  label: string;
  value: number;
  maxValue: number;
  color: string;
}) {
  const percentage = Math.min((value / maxValue) * 100, 100);

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-600">{label}</span>
        <span className="text-sm font-medium text-gray-900">
          {value.toFixed(1)}
          {maxValue === 100 ? "%" : `/${maxValue}`}
        </span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
          }}
        />
      </div>
    </div>
  );
}

function getUsageColor(percentage: number): string {
  if (percentage > 60) return "#EF4444";
  if (percentage > 25) return "#EAB308";
  return "#22C55E";
}
