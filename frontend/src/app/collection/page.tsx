"use client";

import { useState, useMemo } from "react";
import {
  useCollection,
  useCollectionMissing,
  useUpdateCollection,
  useCollectionStats,
} from "@/hooks/useCollection";
import { useDecks } from "@/hooks/useDecks";
import { useCardSearch } from "@/hooks/useCards";
import { CollectionStatsBar } from "@/components/collection/CollectionStatsBar";
import { CollectionGrid } from "@/components/collection/CollectionGrid";
import { MissingCardsList } from "@/components/collection/MissingCardsList";
import { AddToCollectionModal } from "@/components/collection/AddToCollectionModal";
import { CardImage } from "@/components/deck/CardImage";
import type { Card, CardType } from "@/lib/types";
import { ENERGY_TYPES } from "@/lib/constants";

type ActiveTab = "missing" | "collection" | "add";
type SortOption = "name" | "quantity" | "set" | "recent";

export default function CollectionPage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("missing");
  const [showAddModal, setShowAddModal] = useState(false);

  // Missing tab state
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);

  // Collection tab state
  const [filterType, setFilterType] = useState<CardType | "all">("all");
  const [filterEnergyType, setFilterEnergyType] = useState<string>("all");
  const [filterSet, setFilterSet] = useState<string>("all");
  const [sortBy, setSortBy] = useState<SortOption>("name");
  const [collectionSearch, setCollectionSearch] = useState("");

  // Add tab state
  const [addSearchQuery, setAddSearchQuery] = useState("");
  const [selectedAddCard, setSelectedAddCard] = useState<Card | null>(null);
  const [addQuantity, setAddQuantity] = useState(1);

  // Hooks
  const { data: collection, isLoading: collectionLoading } = useCollection();
  const { data: decks } = useDecks();
  const { stats } = useCollectionStats();
  const updateCollection = useUpdateCollection();
  const { data: addSearchResults, isLoading: addSearching } =
    useCardSearch(addSearchQuery);

  // Select first deck automatically if none selected
  const effectiveDeckId = selectedDeckId ?? (decks && decks.length > 0 ? decks[0].id : null);

  // Single missing cards query using the effective deck ID
  const { data: displayMissing, isLoading: displayMissingLoading } =
    useCollectionMissing(effectiveDeckId);

  // Derive the missing count from the currently selected deck
  const missingCount = displayMissing?.length ?? 0;

  // Get unique set codes from collection for the filter dropdown
  const setOptions = useMemo(() => {
    if (!collection) return [];
    const sets = new Set<string>();
    collection.forEach((entry) => {
      if (entry.card.set) {
        sets.add(entry.card.set.code);
      }
    });
    return Array.from(sets).sort();
  }, [collection]);

  // Filter and sort collection entries
  const filteredCollection = useMemo(() => {
    if (!collection) return [];

    let filtered = [...collection];

    // Filter by card type
    if (filterType !== "all") {
      filtered = filtered.filter(
        (entry) => entry.card.card_type === filterType
      );
    }

    // Filter by energy type
    if (filterEnergyType !== "all") {
      filtered = filtered.filter(
        (entry) => entry.card.energy_type === filterEnergyType
      );
    }

    // Filter by set
    if (filterSet !== "all") {
      filtered = filtered.filter(
        (entry) => entry.card.set && entry.card.set.code === filterSet
      );
    }

    // Filter by search
    if (collectionSearch.length >= 2) {
      const search = collectionSearch.toLowerCase();
      filtered = filtered.filter(
        (entry) =>
          entry.card.name_en.toLowerCase().includes(search) ||
          (entry.card.name_pt &&
            entry.card.name_pt.toLowerCase().includes(search))
      );
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "name":
          return a.card.name_en.localeCompare(b.card.name_en);
        case "quantity":
          return b.quantity_owned - a.quantity_owned;
        case "set": {
          const setA = a.card.set?.code ?? "";
          const setB = b.card.set?.code ?? "";
          return setA.localeCompare(setB);
        }
        case "recent":
          return b.card_id - a.card_id;
        default:
          return 0;
      }
    });

    return filtered;
  }, [
    collection,
    filterType,
    filterEnergyType,
    filterSet,
    collectionSearch,
    sortBy,
  ]);

  const handleUpdateQuantity = (cardId: number, quantity: number) => {
    updateCollection.mutate({ cardId, quantity });
  };

  const handleMarkOwned = (cardId: number, currentOwned: number) => {
    updateCollection.mutate({ cardId, quantity: currentOwned + 1 });
  };

  const handleAddCard = () => {
    if (!selectedAddCard) return;
    updateCollection.mutate(
      { cardId: selectedAddCard.id, quantity: addQuantity },
      {
        onSuccess: () => {
          setSelectedAddCard(null);
          setAddQuantity(1);
          setAddSearchQuery("");
        },
      }
    );
  };

  const tabs: { key: ActiveTab; label: string; color: string; activeColor: string }[] = [
    {
      key: "missing",
      label: `Faltando${displayMissing ? ` (${displayMissing.length})` : ""}`,
      color: "bg-gray-100 text-gray-600",
      activeColor: "bg-red-100 text-red-700",
    },
    {
      key: "collection",
      label: `Minha Colecao${collection ? ` (${collection.length})` : ""}`,
      color: "bg-gray-100 text-gray-600",
      activeColor: "bg-green-100 text-green-700",
    },
    {
      key: "add",
      label: "Adicionar",
      color: "bg-gray-100 text-gray-600",
      activeColor: "bg-blue-100 text-blue-700",
    },
  ];

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Minha Colecao</h1>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Adicionar Cartas
        </button>
      </div>

      {/* Stats */}
      <CollectionStatsBar
        totalUnique={stats.totalUnique}
        totalCopies={stats.totalCopies}
        missingCount={missingCount}
      />

      {/* Tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === tab.key ? tab.activeColor : tab.color
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content: Faltando */}
      {activeTab === "missing" && (
        <div>
          {/* Deck selector */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Selecionar Deck
            </label>
            <select
              value={selectedDeckId ?? effectiveDeckId ?? ""}
              onChange={(e) => {
                const val = e.target.value;
                setSelectedDeckId(val ? Number(val) : null);
              }}
              className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
            >
              <option value="" disabled>
                Escolha um deck...
              </option>
              {decks?.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name}
                </option>
              ))}
            </select>
            {(!decks || decks.length === 0) && (
              <p className="text-sm text-gray-400 mt-1">
                Nenhum deck cadastrado. Importe um deck primeiro.
              </p>
            )}
          </div>

          {displayMissingLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-red-200 border-t-red-600 rounded-full animate-spin" />
              <span className="ml-3 text-gray-500">
                Verificando cartas faltando...
              </span>
            </div>
          ) : !effectiveDeckId ? (
            <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
              <svg
                className="w-16 h-16 text-gray-300 mx-auto mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-gray-500 text-lg mb-2">
                Selecione um deck para ver cartas faltando
              </p>
              <p className="text-gray-400 text-sm">
                Adicione decks e marque suas cartas como adquiridas.
              </p>
            </div>
          ) : (
            <MissingCardsList
              missing={displayMissing ?? []}
              onMarkOwned={handleMarkOwned}
            />
          )}
        </div>
      )}

      {/* Tab content: Minha Colecao */}
      {activeTab === "collection" && (
        <div>
          {/* Filters bar */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {/* Search */}
              <div className="lg:col-span-2">
                <div className="relative">
                  <svg
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
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
                    value={collectionSearch}
                    onChange={(e) => setCollectionSearch(e.target.value)}
                    placeholder="Buscar por nome..."
                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm text-gray-900"
                  />
                </div>
              </div>

              {/* Card type filter */}
              <select
                value={filterType}
                onChange={(e) =>
                  setFilterType(e.target.value as CardType | "all")
                }
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 text-gray-900 bg-white"
              >
                <option value="all">Todos os Tipos</option>
                <option value="pokemon">Pokemon</option>
                <option value="trainer">Treinador</option>
                <option value="energy">Energia</option>
              </select>

              {/* Energy type filter */}
              <select
                value={filterEnergyType}
                onChange={(e) => setFilterEnergyType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 text-gray-900 bg-white"
              >
                <option value="all">Todos os Tipos de Energia</option>
                {ENERGY_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 text-gray-900 bg-white"
              >
                <option value="name">Ordenar: Nome</option>
                <option value="quantity">Ordenar: Quantidade</option>
                <option value="set">Ordenar: Set</option>
                <option value="recent">Ordenar: Recentes</option>
              </select>
            </div>

            {/* Set filter (shown separately if sets exist) */}
            {setOptions.length > 0 && (
              <div className="mt-3">
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setFilterSet("all")}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      filterSet === "all"
                        ? "bg-green-600 text-white"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    Todos os Sets
                  </button>
                  {setOptions.map((setCode) => (
                    <button
                      key={setCode}
                      onClick={() => setFilterSet(setCode)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        filterSet === setCode
                          ? "bg-green-600 text-white"
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      }`}
                    >
                      {setCode}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {collectionLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
              <span className="ml-3 text-gray-500">
                Carregando colecao...
              </span>
            </div>
          ) : (
            <>
              {filteredCollection.length !== (collection?.length ?? 0) && (
                <p className="text-sm text-gray-500 mb-3">
                  Mostrando {filteredCollection.length} de{" "}
                  {collection?.length ?? 0} cartas
                </p>
              )}
              <CollectionGrid
                entries={filteredCollection}
                onUpdateQuantity={handleUpdateQuantity}
              />
            </>
          )}
        </div>
      )}

      {/* Tab content: Adicionar */}
      {activeTab === "add" && (
        <div>
          {/* Search */}
          <div className="mb-5">
            <div className="relative max-w-lg">
              <svg
                className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
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
                value={addSearchQuery}
                onChange={(e) => {
                  setAddSearchQuery(e.target.value);
                  setSelectedAddCard(null);
                }}
                placeholder="Buscar carta por nome (minimo 2 caracteres)..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
            </div>
          </div>

          {/* Selected card detail */}
          {selectedAddCard && (
            <div className="mb-5 p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex items-center gap-4">
                <CardImage
                  card={selectedAddCard}
                  width={80}
                  height={112}
                />
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">
                    {selectedAddCard.name_en}
                  </p>
                  {selectedAddCard.name_pt && (
                    <p className="text-sm text-gray-500">
                      {selectedAddCard.name_pt}
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {selectedAddCard.card_type}
                    {selectedAddCard.set &&
                      ` - ${selectedAddCard.set.code}`}
                    {selectedAddCard.regulation_mark &&
                      ` - Marca ${selectedAddCard.regulation_mark}`}
                  </p>

                  <div className="flex items-center gap-3 mt-3">
                    <label className="text-sm text-gray-700 font-medium">
                      Quantidade:
                    </label>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() =>
                          setAddQuantity(Math.max(1, addQuantity - 1))
                        }
                        className="w-8 h-8 bg-white border border-gray-300 rounded-lg flex items-center justify-center text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        -
                      </button>
                      <span className="w-8 text-center font-bold text-gray-900">
                        {addQuantity}
                      </span>
                      <button
                        onClick={() =>
                          setAddQuantity(Math.min(99, addQuantity + 1))
                        }
                        className="w-8 h-8 bg-white border border-gray-300 rounded-lg flex items-center justify-center text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        +
                      </button>
                    </div>
                    <button
                      onClick={handleAddCard}
                      disabled={updateCollection.isPending}
                      className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50"
                    >
                      {updateCollection.isPending
                        ? "Adicionando..."
                        : "Adicionar"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Search loading */}
          {addSearching && (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
              <span className="ml-3 text-gray-500">Buscando cartas...</span>
            </div>
          )}

          {/* No results */}
          {!addSearching &&
            addSearchQuery.length >= 2 &&
            addSearchResults &&
            addSearchResults.length === 0 && (
              <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                <p className="text-gray-500">
                  Nenhuma carta encontrada para &quot;{addSearchQuery}&quot;
                </p>
              </div>
            )}

          {/* Search results */}
          {!addSearching &&
            addSearchResults &&
            addSearchResults.length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                {addSearchResults.map((card) => (
                  <div
                    key={card.id}
                    className={`cursor-pointer rounded-lg transition-all ${
                      selectedAddCard?.id === card.id
                        ? "ring-2 ring-blue-500 scale-105"
                        : "hover:scale-105"
                    }`}
                    onClick={() => {
                      setSelectedAddCard(card);
                      setAddQuantity(1);
                    }}
                  >
                    <CardImage card={card} width={150} height={210} />
                    <p className="mt-1 text-xs text-gray-600 text-center truncate px-1">
                      {card.name_en}
                    </p>
                    {card.set && (
                      <p className="text-xs text-gray-400 text-center">
                        {card.set.code}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}

          {/* Prompt to search */}
          {addSearchQuery.length < 2 && !selectedAddCard && (
            <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
              <svg
                className="w-16 h-16 text-gray-300 mx-auto mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <p className="text-gray-500 text-lg mb-2">
                Busque cartas para adicionar
              </p>
              <p className="text-gray-400 text-sm">
                Digite pelo menos 2 caracteres para buscar
              </p>
            </div>
          )}
        </div>
      )}

      {/* Add to Collection Modal (alternative to tab) */}
      <AddToCollectionModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
      />
    </div>
  );
}
