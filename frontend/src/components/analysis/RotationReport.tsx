"use client";

import type { RotationReport as RotationReportType } from "@/lib/types";
import { SEVERITY_COLORS } from "@/lib/constants";

interface RotationReportProps {
  report: RotationReportType;
}

const SEVERITY_LABELS: Record<string, string> = {
  NONE: "Nenhum",
  LOW: "Baixo",
  MODERATE: "Moderado",
  HIGH: "Alto",
  CRITICAL: "Critico",
};

export function RotationReport({ report }: RotationReportProps) {
  const severityColor = SEVERITY_COLORS[report.severity] || "#6B7280";
  const severityLabel = SEVERITY_LABELS[report.severity] || report.severity;

  return (
    <div className="space-y-6">
      {/* Severity badge */}
      <div className="flex items-center gap-3">
        <span
          className="text-sm font-bold px-3 py-1.5 rounded-full text-white"
          style={{ backgroundColor: severityColor }}
        >
          {severityLabel}
        </span>
        <span className="text-sm text-gray-600">
          Impacto da rotacao no deck
        </span>
      </div>

      {/* Overall stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total de Cartas"
          value={report.total_cards}
          color="#3B82F6"
        />
        <StatCard
          label="Cartas Rotacionando"
          value={report.rotating_cards}
          color={report.rotating_cards > 0 ? "#F97316" : "#22C55E"}
        />
        <StatCard
          label="Cartas Ilegais"
          value={report.illegal_cards}
          color={report.illegal_cards > 0 ? "#EF4444" : "#22C55E"}
        />
        <StatCard
          label="Porcentagem"
          value={`${report.rotation_percentage.toFixed(1)}%`}
          color={severityColor}
        />
      </div>

      {/* Overall progress bar */}
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600">Impacto geral da rotacao</span>
          <span className="font-semibold" style={{ color: severityColor }}>
            {report.rotation_percentage.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${report.rotation_percentage}%`,
              backgroundColor: severityColor,
            }}
          />
        </div>
      </div>

      {/* Breakdown by type */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-800">Detalhamento por tipo</h4>

        <BreakdownBar
          label="Pokemon"
          breakdown={report.breakdown.pokemon}
          icon={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 14a4 4 0 110-8 4 4 0 010 8z" />
            </svg>
          }
        />

        <BreakdownBar
          label="Treinadores"
          breakdown={report.breakdown.trainers}
          icon={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          }
        />

        <BreakdownBar
          label="Energia"
          breakdown={report.breakdown.energy}
          icon={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
        />
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number | string;
  color: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
      <div className="text-2xl font-bold" style={{ color }}>
        {value}
      </div>
      <div className="text-xs text-gray-500 mt-1">{label}</div>
    </div>
  );
}

function BreakdownBar({
  label,
  breakdown,
  icon,
}: {
  label: string;
  breakdown: { rotating: number; illegal: number; safe: number };
  icon: React.ReactNode;
}) {
  const total = breakdown.rotating + breakdown.illegal + breakdown.safe;
  if (total === 0) return null;

  const rotatingPct = (breakdown.rotating / total) * 100;
  const illegalPct = (breakdown.illegal / total) * 100;
  const safePct = (breakdown.safe / total) * 100;

  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1">
        <div className="flex items-center gap-2 text-gray-700 font-medium">
          {icon}
          {label}
        </div>
        <span className="text-gray-500 text-xs">
          {breakdown.safe} seguras / {breakdown.rotating} rotacionando / {breakdown.illegal} ilegais
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden flex">
        {safePct > 0 && (
          <div
            className="h-full bg-green-500"
            style={{ width: `${safePct}%` }}
            title={`Seguras: ${breakdown.safe}`}
          />
        )}
        {rotatingPct > 0 && (
          <div
            className="h-full bg-orange-400"
            style={{ width: `${rotatingPct}%` }}
            title={`Rotacionando: ${breakdown.rotating}`}
          />
        )}
        {illegalPct > 0 && (
          <div
            className="h-full bg-red-500"
            style={{ width: `${illegalPct}%` }}
            title={`Ilegais: ${breakdown.illegal}`}
          />
        )}
      </div>
    </div>
  );
}
