"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useCardSearch, useAbilityCategories } from "@/hooks/useCards";
import { ENERGY_COLORS, ENERGY_TYPES, REGULATION_MARKS } from "@/lib/constants";
import { CardImage } from "@/components/deck/CardImage";
import { EnergyBadge } from "@/components/cards/EnergyBadge";
import type { Card } from "@/lib/types";

type ViewMode = "list" | "grid";

const ITEMS_PER_PAGE = 24;

const CARD_TYPE_LABELS: Record<string, string> = {
  pokemon: "Pokemon",
  trainer: "Treinador",
  energy: "Energia",
};

const TRAINER_SUBTYPE_LABELS: Record<string, string> = {
  supporter: "Apoiador",
  item: "Item",
  stadium: "Estadio",
  tool: "Ferramenta",
};

export default function CardsPage() {
  const [query, setQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("");
  const [selectedAbility, setSelectedAbility] = useState<string>("");
  const [selectedEnergy, setSelectedEnergy] = useState<string>("");
  const [selectedRegMark, setSelectedRegMark] = useState<string>("");
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);

  const filters: Record<string, string> = {};
  if (selectedType) filters.type = selectedType;
  if (selectedAbility) filters.ability = selectedAbility;
  if (selectedEnergy) filters.energy_type = selectedEnergy;
  if (selectedRegMark) filters.regulation_mark = selectedRegMark;

  const { data: cards, isLoading } = useCardSearch(query, filters);
  const { data: abilities } = useAbilityCategories();

  const visibleCards = useMemo(() => {
    if (!cards) return [];
    return cards.slice(0, visibleCount);
  }, [cards, visibleCount]);

  const hasMore = cards ? visibleCount < cards.length : false;
  const totalCount = cards?.length || 0;

  const clearFilters = () => {
    setSelectedType("");
    setSelectedAbility("");
    setSelectedEnergy("");
    setSelectedRegMark("");
    setVisibleCount(ITEMS_PER_PAGE);
  };

  const hasActiveFilters =
    selectedType || selectedAbility || selectedEnergy || selectedRegMark;

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Buscar Cartas</h1>
        {/* View mode toggle */}
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode("list")}
            className={`p-2 rounded-md transition-colors ${
              viewMode === "list"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
            title="Visualizacao em lista"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
          <button
            onClick={() => setViewMode("grid")}
            className={`p-2 rounded-md transition-colors ${
              viewMode === "grid"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
            title="Visualizacao em grade"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        {/* Search bar */}
        <div className="relative mb-3">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setVisibleCount(ITEMS_PER_PAGE);
            }}
            placeholder="Nome da carta..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
          />
        </div>

        {/* Filter row */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Type filter */}
          <select
            value={selectedType}
            onChange={(e) => {
              setSelectedType(e.target.value);
              setVisibleCount(ITEMS_PER_PAGE);
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          >
            <option value="">Todos os tipos</option>
            <option value="pokemon">Pokemon</option>
            <option value="trainer">Treinador</option>
            <option value="energy">Energia</option>
          </select>

          {/* Ability filter */}
          <select
            value={selectedAbility}
            onChange={(e) => {
              setSelectedAbility(e.target.value);
              setVisibleCount(ITEMS_PER_PAGE);
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          >
            <option value="">Todas habilidades</option>
            {abilities?.map((cat) => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1).replace("_", " ")}
              </option>
            ))}
          </select>

          {/* Energy type filter */}
          <select
            value={selectedEnergy}
            onChange={(e) => {
              setSelectedEnergy(e.target.value);
              setVisibleCount(ITEMS_PER_PAGE);
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          >
            <option value="">Todos os tipos de energia</option>
            {ENERGY_TYPES.map((energy) => (
              <option key={energy} value={energy}>
                {energy.charAt(0).toUpperCase() + energy.slice(1)}
              </option>
            ))}
          </select>

          {/* Regulation mark filter */}
          <select
            value={selectedRegMark}
            onChange={(e) => {
              setSelectedRegMark(e.target.value);
              setVisibleCount(ITEMS_PER_PAGE);
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          >
            <option value="">Todas as marcas</option>
            <option value="G">G - Rotacionando</option>
            <option value="H">H - Legal</option>
            <option value="I">I - Legal (Nova)</option>
          </select>

          {/* Clear filters */}
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1.5"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
              Limpar
            </button>
          )}
        </div>
      </div>

      {/* Results */}
      {query.length < 2 ? (
        <div className="text-center py-16">
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
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <p className="text-gray-500">
            Digite pelo menos 2 caracteres para buscar
          </p>
        </div>
      ) : isLoading ? (
        <div className="flex items-center justify-center py-16">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-500">Buscando...</p>
          </div>
        </div>
      ) : !cards || cards.length === 0 ? (
        <div className="text-center py-16">
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
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-gray-500">Nenhuma carta encontrada</p>
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Limpar filtros e tentar novamente
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Result count */}
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-500">
              {totalCount} {totalCount === 1 ? "carta encontrada" : "cartas encontradas"}
              {visibleCount < totalCount && (
                <span className="text-gray-400">
                  {" "}(exibindo {Math.min(visibleCount, totalCount)})
                </span>
              )}
            </p>
          </div>

          {/* Grid view */}
          {viewMode === "grid" ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {visibleCards.map((card) => (
                <GridCardItem key={card.id} card={card} />
              ))}
            </div>
          ) : (
            /* List view */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {visibleCards.map((card) => (
                <ListCardItem key={card.id} card={card} />
              ))}
            </div>
          )}

          {/* Load more */}
          {hasMore && (
            <div className="flex justify-center mt-8">
              <button
                onClick={() => setVisibleCount((prev) => prev + ITEMS_PER_PAGE)}
                className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium text-sm"
              >
                Carregar mais cartas
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ListCardItem({ card }: { card: Card }) {
  const regMark = card.regulation_mark as keyof typeof REGULATION_MARKS | null;
  const regInfo = regMark ? REGULATION_MARKS[regMark] : null;

  return (
    <Link
      href={`/cards/${card.id}`}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 hover:shadow-md hover:border-primary-300 transition-all block group"
    >
      <div className="flex items-start gap-3">
        {/* Energy color dot */}
        <div
          className="w-3 h-3 rounded-full mt-1.5 flex-shrink-0"
          style={{
            backgroundColor: card.energy_type
              ? ENERGY_COLORS[card.energy_type.toLowerCase()] || "#A8A878"
              : "#A8A878",
          }}
        />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 group-hover:text-primary-600 transition-colors truncate">
            {card.name_en}
          </p>
          {card.name_pt && card.name_pt !== card.name_en && (
            <p className="text-xs text-gray-400 truncate">{card.name_pt}</p>
          )}
          <div className="flex items-center gap-2 mt-1">
            <p className="text-sm text-gray-500">
              {card.set?.code || `Set #${card.set_id}`} {card.set_number}
              {card.hp ? ` - ${card.hp} HP` : ""}
            </p>
            {card.regulation_mark && (
              <span
                className="text-[10px] font-bold px-1.5 py-0.5 rounded text-white"
                style={{ backgroundColor: regInfo?.color || "#6B7280" }}
              >
                {card.regulation_mark}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-xs text-gray-400">
              {CARD_TYPE_LABELS[card.card_type] || card.card_type}
              {card.trainer_subtype &&
                ` - ${TRAINER_SUBTYPE_LABELS[card.trainer_subtype] || card.trainer_subtype}`}
            </span>
            {card.is_ex && (
              <span className="text-[10px] bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded-full font-medium">
                ex
              </span>
            )}
          </div>
        </div>
        {/* Arrow */}
        <svg
          className="w-5 h-5 text-gray-300 group-hover:text-primary-400 transition-colors flex-shrink-0 mt-1"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </div>
    </Link>
  );
}

function GridCardItem({ card }: { card: Card }) {
  return (
    <Link
      href={`/cards/${card.id}`}
      className="group block"
    >
      <div className="flex justify-center">
        <CardImage card={card} width={140} height={196} />
      </div>
      <div className="mt-2 text-center">
        <p className="text-sm font-medium text-gray-900 truncate group-hover:text-primary-600 transition-colors">
          {card.name_pt || card.name_en}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">
          {card.set?.code || ""} {card.set_number}
        </p>
      </div>
    </Link>
  );
}
