"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { useCard } from "@/hooks/useCards";
import { ENERGY_COLORS, REGULATION_MARKS } from "@/lib/constants";
import { EnergyBadge } from "@/components/cards/EnergyBadge";
import { CardAlternatives } from "@/components/cards/CardAlternatives";
import { CardUsageChart } from "@/components/cards/CardUsageChart";

type TabKey = "detalhes" | "alternativas" | "estatisticas";

const TABS: { key: TabKey; label: string }[] = [
  { key: "detalhes", label: "Detalhes" },
  { key: "alternativas", label: "Alternativas" },
  { key: "estatisticas", label: "Estatisticas" },
];

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

function formatCardType(type: string, subtype: string | null): string {
  const typeMap: Record<string, string> = {
    pokemon: "Pokemon",
    trainer: "Treinador",
    energy: "Energia",
  };
  const subtypeMap: Record<string, string> = {
    supporter: "Apoiador",
    item: "Item",
    stadium: "Estadio",
    tool: "Ferramenta",
  };
  const base = typeMap[type] || type;
  if (subtype && subtypeMap[subtype]) {
    return `${base} - ${subtypeMap[subtype]}`;
  }
  return base;
}

export default function CardDetailPage() {
  const params = useParams();
  const cardId = Number(params.id);
  const { data: card, isLoading, error } = useCard(cardId);
  const [activeTab, setActiveTab] = useState<TabKey>("detalhes");
  const [imageError, setImageError] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-3 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-500">Carregando carta...</p>
        </div>
      </div>
    );
  }

  if (error || !card) {
    return (
      <div className="text-center py-24">
        <svg
          className="w-16 h-16 text-gray-300 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
          />
        </svg>
        <p className="text-gray-500 text-lg mb-2">Carta nao encontrada</p>
        <Link
          href="/cards"
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          Voltar para busca
        </Link>
      </div>
    );
  }

  const regMark = card.regulation_mark as keyof typeof REGULATION_MARKS | null;
  const regInfo = regMark ? REGULATION_MARKS[regMark] : null;
  const isRotating = card.regulation_mark === "G";
  const imageUrl = card.image_url_hires || card.image_url;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-500 mb-6">
        <Link href="/cards" className="hover:text-primary-600 transition-colors">
          Cartas
        </Link>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span className="text-gray-900 font-medium truncate">
          {card.name_pt || card.name_en}
        </span>
      </nav>

      {/* Header section */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Card image */}
          <div className="flex-shrink-0 flex justify-center md:justify-start">
            <div className="relative">
              <Image
                src={imageError || !imageUrl ? "/images/card-back.png" : imageUrl}
                alt={card.name_en}
                width={280}
                height={392}
                className="rounded-xl shadow-lg"
                onError={() => setImageError(true)}
                priority
              />
              {/* Regulation mark overlay on image */}
              {card.regulation_mark && (
                <span
                  className="absolute top-2 right-2 text-sm font-bold px-2 py-1 rounded text-white shadow-md"
                  style={{ backgroundColor: regInfo?.color || "#6B7280" }}
                >
                  {card.regulation_mark}
                </span>
              )}
            </div>
          </div>

          {/* Card info */}
          <div className="flex-1 min-w-0">
            {/* Names */}
            <div className="mb-4">
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                {card.name_en}
              </h1>
              {card.name_pt && card.name_pt !== card.name_en && (
                <p className="text-lg text-gray-500 mt-1">{card.name_pt}</p>
              )}
            </div>

            {/* Badges row */}
            <div className="flex flex-wrap items-center gap-2 mb-5">
              {/* Card type badge */}
              <span className="bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full font-medium">
                {formatCardType(card.card_type, card.trainer_subtype)}
              </span>

              {/* Energy type badge */}
              {card.energy_type && (
                <EnergyBadge type={card.energy_type} size="md" />
              )}

              {/* EX badge */}
              {card.is_ex && (
                <span className="bg-yellow-100 text-yellow-800 text-sm px-3 py-1 rounded-full font-semibold">
                  Pokemon ex
                </span>
              )}

              {/* HP badge */}
              {card.hp && (
                <span className="bg-red-50 text-red-700 text-sm px-3 py-1 rounded-full font-medium">
                  {card.hp} HP
                </span>
              )}
            </div>

            {/* Info grid */}
            <div className="grid grid-cols-2 gap-3 mb-5">
              <InfoItem
                label="Set"
                value={card.set?.name_en || `Set #${card.set_id}`}
              />
              <InfoItem label="Numero" value={card.set_number} />
              {card.stage && (
                <InfoItem
                  label="Estagio"
                  value={card.stage.charAt(0).toUpperCase() + card.stage.slice(1)}
                />
              )}
              {card.energy_type && (
                <InfoItem
                  label="Tipo de Energia"
                  value={card.energy_type.charAt(0).toUpperCase() + card.energy_type.slice(1)}
                />
              )}
            </div>

            {/* Regulation mark status */}
            {card.regulation_mark && (
              <div
                className={`flex items-center gap-3 p-3 rounded-lg ${
                  isRotating ? "bg-red-50 border border-red-100" : "bg-green-50 border border-green-100"
                }`}
              >
                <span
                  className="text-sm font-bold px-2.5 py-1 rounded text-white flex-shrink-0"
                  style={{ backgroundColor: regInfo?.color || "#6B7280" }}
                >
                  {card.regulation_mark}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Marca de Regulacao {card.regulation_mark}
                  </p>
                  <p
                    className={`text-xs font-medium ${
                      isRotating ? "text-red-600" : "text-green-600"
                    }`}
                  >
                    {isRotating ? "Rotacionando em Marco 2026" : "Legal"}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Tab header */}
        <div className="flex border-b border-gray-200">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors relative ${
                activeTab === tab.key
                  ? "text-primary-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
              {activeTab === tab.key && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600" />
              )}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="p-6">
          {activeTab === "detalhes" && <DetailsTab card={card} />}
          {activeTab === "alternativas" && <CardAlternatives cardId={card.id} />}
          {activeTab === "estatisticas" && <CardUsageChart cardId={card.id} />}
        </div>
      </div>
    </div>
  );
}

function DetailsTab({ card }: { card: NonNullable<ReturnType<typeof useCard>["data"]> }) {
  return (
    <div className="space-y-8">
      {/* Abilities */}
      {card.abilities && card.abilities.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3">
            Habilidades
          </h3>
          <div className="space-y-3">
            {card.abilities.map((ability) => (
              <div
                key={ability.id}
                className="bg-purple-50 rounded-xl p-4 border border-purple-100"
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="font-semibold text-purple-900 text-base">
                    {ability.name_pt || ability.name_en}
                  </p>
                  {ability.category && (
                    <span className="inline-block text-xs bg-purple-200 text-purple-800 px-2.5 py-0.5 rounded-full font-medium flex-shrink-0">
                      {ability.category}
                    </span>
                  )}
                </div>
                {ability.name_pt && ability.name_en !== ability.name_pt && (
                  <p className="text-xs text-purple-400 mt-0.5">
                    {ability.name_en}
                  </p>
                )}
                {(ability.effect_pt || ability.effect_en) && (
                  <p className="text-sm text-gray-600 mt-2 leading-relaxed">
                    {ability.effect_pt || ability.effect_en}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Attacks */}
      {card.attacks && card.attacks.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3">
            Ataques
          </h3>
          <div className="space-y-3">
            {card.attacks.map((attack) => (
              <div
                key={attack.id}
                className="bg-blue-50 rounded-xl p-4 border border-blue-100"
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold text-blue-900 text-base">
                      {attack.name_pt || attack.name_en}
                    </p>
                    {attack.name_pt && attack.name_en !== attack.name_pt && (
                      <p className="text-xs text-blue-400 mt-0.5">
                        {attack.name_en}
                      </p>
                    )}
                  </div>
                  {attack.damage && (
                    <span className="text-2xl font-bold text-blue-700 flex-shrink-0">
                      {attack.damage}
                    </span>
                  )}
                </div>

                {/* Energy cost icons */}
                {attack.energy_cost && attack.energy_cost.length > 0 && (
                  <div className="flex gap-1.5 mt-2">
                    {attack.energy_cost.map((cost, idx) => {
                      const color =
                        ENERGY_COLORS[cost.toLowerCase()] || "#A8A878";
                      return (
                        <span
                          key={idx}
                          className="w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold shadow-sm"
                          style={{ backgroundColor: color }}
                          title={cost}
                        >
                          {cost.charAt(0).toUpperCase()}
                        </span>
                      );
                    })}
                  </div>
                )}

                {(attack.effect_pt || attack.effect_en) && (
                  <p className="text-sm text-gray-600 mt-2 leading-relaxed">
                    {attack.effect_pt || attack.effect_en}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Functions */}
      {card.functions && card.functions.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3">
            Funcoes
          </h3>
          <div className="flex flex-wrap gap-2">
            {card.functions.map((fn) => (
              <span
                key={fn}
                className="bg-gray-100 text-gray-700 text-sm px-3 py-1.5 rounded-full font-medium"
              >
                {FUNCTION_LABELS[fn] || fn}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Empty state for cards with no details */}
      {(!card.abilities || card.abilities.length === 0) &&
        (!card.attacks || card.attacks.length === 0) &&
        (!card.functions || card.functions.length === 0) && (
          <div className="text-center py-8">
            <p className="text-gray-500 text-sm">
              Nenhum detalhe adicional disponivel para esta carta
            </p>
          </div>
        )}
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-sm font-medium text-gray-900 truncate mt-0.5">
        {value}
      </p>
    </div>
  );
}
