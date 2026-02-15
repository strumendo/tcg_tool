"use client";

import Link from "next/link";
import { useCardAlternatives } from "@/hooks/useCards";
import { CardImage } from "@/components/deck/CardImage";
import { REGULATION_MARKS } from "@/lib/constants";
import type { Card } from "@/lib/types";

interface CardAlternativesProps {
  cardId: number;
}

const FUNCTION_LABELS: Record<string, string> = {
  draw: "Compra",
  search: "Busca",
  recovery: "Recuperacao",
  removal: "Remocao",
  switching: "Troca",
  energy_accel: "Aceleracao de Energia",
  damage: "Dano",
  healing: "Cura",
  disruption: "Disrupcao",
  setup: "Setup",
  protection: "Protecao",
  other: "Outro",
};

export function CardAlternatives({ cardId }: CardAlternativesProps) {
  const { data: alternatives, isLoading, error } = useCardAlternatives(cardId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-500">Carregando alternativas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 text-sm">Erro ao carregar alternativas</p>
      </div>
    );
  }

  if (!alternatives || alternatives.length === 0) {
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
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
        <p className="text-gray-500 text-sm">
          Nenhuma alternativa encontrada para esta carta
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      {alternatives.map((alt) => (
        <AlternativeCard key={alt.id} card={alt} />
      ))}
    </div>
  );
}

function AlternativeCard({ card }: { card: Card }) {
  const regMark = card.regulation_mark as keyof typeof REGULATION_MARKS | null;
  const regInfo = regMark ? REGULATION_MARKS[regMark] : null;

  return (
    <Link
      href={`/cards/${card.id}`}
      className="group block bg-white rounded-xl border border-gray-200 p-3 hover:shadow-md hover:border-primary-300 transition-all"
    >
      <div className="flex justify-center mb-3">
        <CardImage card={card} width={100} height={140} />
      </div>

      <div className="space-y-1.5">
        <p className="text-sm font-medium text-gray-900 truncate group-hover:text-primary-600 transition-colors">
          {card.name_pt || card.name_en}
        </p>
        <p className="text-xs text-gray-500">
          {card.set?.code || `Set #${card.set_id}`} {card.set_number}
        </p>

        {/* Regulation mark badge */}
        {card.regulation_mark && (
          <span
            className="inline-block text-xs font-bold px-1.5 py-0.5 rounded text-white"
            style={{ backgroundColor: regInfo?.color || "#6B7280" }}
          >
            {card.regulation_mark}
          </span>
        )}

        {/* Shared functions */}
        {card.functions && card.functions.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {card.functions.map((fn) => (
              <span
                key={fn}
                className="text-[10px] bg-primary-50 text-primary-700 px-1.5 py-0.5 rounded-full font-medium"
              >
                {FUNCTION_LABELS[fn] || fn}
              </span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}
