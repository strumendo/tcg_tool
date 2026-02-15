"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useCreateDeck } from "@/hooks/useDecks";
import { useCardSearch } from "@/hooks/useCards";
import { MAX_DECK_SIZE, MAX_CARD_COPIES } from "@/lib/constants";
import type { Card, DeckCreate } from "@/lib/types";

interface DeckCardEntry {
  card: Card;
  quantity: number;
}

const COMMON_ARCHETYPES = [
  "Charizard ex",
  "Dragapult ex",
  "Lugia VSTAR",
  "Gardevoir ex",
  "Raging Bolt ex",
  "Regidrago VSTAR",
  "Snorlax Stall",
  "Lost Box",
];

export default function NewDeckPage() {
  const router = useRouter();
  const createDeck = useCreateDeck();

  const [name, setName] = useState("");
  const [archetype, setArchetype] = useState("");
  const [notes, setNotes] = useState("");
  const [cards, setCards] = useState<DeckCardEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showArchetypeList, setShowArchetypeList] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { data: searchResults, isLoading: isSearching } = useCardSearch(searchQuery);

  const totalCards = cards.reduce((sum, entry) => sum + entry.quantity, 0);
  const pokemonCount = cards
    .filter((e) => e.card.card_type === "pokemon")
    .reduce((s, e) => s + e.quantity, 0);
  const trainerCount = cards
    .filter((e) => e.card.card_type === "trainer")
    .reduce((s, e) => s + e.quantity, 0);
  const energyCount = cards
    .filter((e) => e.card.card_type === "energy")
    .reduce((s, e) => s + e.quantity, 0);

  const addCard = useCallback(
    (card: Card) => {
      setCards((prev) => {
        const existing = prev.find((e) => e.card.id === card.id);
        if (existing) {
          if (existing.quantity >= MAX_CARD_COPIES) return prev;
          const newTotal = prev.reduce((s, e) => s + e.quantity, 0) + 1;
          if (newTotal > MAX_DECK_SIZE) return prev;
          return prev.map((e) =>
            e.card.id === card.id ? { ...e, quantity: e.quantity + 1 } : e
          );
        }
        const newTotal = prev.reduce((s, e) => s + e.quantity, 0) + 1;
        if (newTotal > MAX_DECK_SIZE) return prev;
        return [...prev, { card, quantity: 1 }];
      });
    },
    []
  );

  const removeCard = useCallback((cardId: number) => {
    setCards((prev) => {
      const existing = prev.find((e) => e.card.id === cardId);
      if (!existing) return prev;
      if (existing.quantity <= 1) {
        return prev.filter((e) => e.card.id !== cardId);
      }
      return prev.map((e) =>
        e.card.id === cardId ? { ...e, quantity: e.quantity - 1 } : e
      );
    });
  }, []);

  const removeAllCopies = useCallback((cardId: number) => {
    setCards((prev) => prev.filter((e) => e.card.id !== cardId));
  }, []);

  const handleSubmit = async () => {
    if (!name.trim()) {
      setSubmitError("Nome do deck e obrigatorio");
      return;
    }
    if (totalCards !== MAX_DECK_SIZE) {
      setSubmitError(`O deck deve ter exatamente ${MAX_DECK_SIZE} cartas (atual: ${totalCards})`);
      return;
    }

    setSubmitError(null);

    const deckData: DeckCreate = {
      name: name.trim(),
      archetype: archetype.trim() || undefined,
      notes: notes.trim() || undefined,
      cards: cards.map((entry) => ({
        card_id: entry.card.id,
        quantity: entry.quantity,
      })),
    };

    createDeck.mutate(deckData, {
      onSuccess: (data) => {
        router.push(`/decks/${data.id}`);
      },
      onError: (error) => {
        setSubmitError(
          error instanceof Error ? error.message : "Erro ao criar deck"
        );
      },
    });
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Novo Deck</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Form and search */}
        <div className="lg:col-span-2 space-y-6">
          {/* Deck info */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Informacoes do Deck
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome do Deck *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ex: Charizard ex / Pidgeot ex"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Arquetipo
                </label>
                <input
                  type="text"
                  value={archetype}
                  onChange={(e) => {
                    setArchetype(e.target.value);
                    setShowArchetypeList(true);
                  }}
                  onFocus={() => setShowArchetypeList(true)}
                  onBlur={() => setTimeout(() => setShowArchetypeList(false), 200)}
                  placeholder="Ex: Charizard ex"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                {showArchetypeList && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {COMMON_ARCHETYPES.filter((a) =>
                      a.toLowerCase().includes(archetype.toLowerCase())
                    ).map((a) => (
                      <button
                        key={a}
                        type="button"
                        onClick={() => {
                          setArchetype(a);
                          setShowArchetypeList(false);
                        }}
                        className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
                      >
                        {a}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notas
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Anotacoes sobre o deck..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                />
              </div>
            </div>
          </div>

          {/* Card search */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Buscar Cartas
            </h2>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Digite o nome da carta (min. 2 caracteres)..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 mb-4"
            />

            {isSearching && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600" />
                <span className="ml-2 text-sm text-gray-500">Buscando...</span>
              </div>
            )}

            {searchResults && searchResults.length > 0 && (
              <div className="max-h-96 overflow-y-auto space-y-2">
                {searchResults.map((card) => {
                  const inDeck = cards.find((e) => e.card.id === card.id);
                  return (
                    <div
                      key={card.id}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="w-10 h-14 relative flex-shrink-0 bg-gray-100 rounded overflow-hidden">
                        {card.image_url ? (
                          <Image
                            src={card.image_url}
                            alt={card.name_en}
                            fill
                            className="object-cover"
                            sizes="40px"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                            ?
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {card.name_pt || card.name_en}
                        </p>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span className="capitalize">{card.card_type}</span>
                          {card.set?.code && <span>{card.set.code}</span>}
                          <span>#{card.set_number}</span>
                          {card.regulation_mark && (
                            <span
                              className={`font-bold ${
                                card.regulation_mark === "G"
                                  ? "text-red-500"
                                  : "text-green-500"
                              }`}
                            >
                              {card.regulation_mark}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {inDeck && (
                          <span className="text-xs text-gray-500 font-medium">
                            {inDeck.quantity}x
                          </span>
                        )}
                        <button
                          onClick={() => addCard(card)}
                          disabled={
                            totalCards >= MAX_DECK_SIZE ||
                            (inDeck ? inDeck.quantity >= MAX_CARD_COPIES : false)
                          }
                          className="px-2.5 py-1 bg-primary-600 text-white text-xs font-medium rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                        >
                          + Adicionar
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {searchResults && searchResults.length === 0 && searchQuery.length >= 2 && (
              <p className="text-center text-gray-500 text-sm py-8">
                Nenhuma carta encontrada para &quot;{searchQuery}&quot;
              </p>
            )}

            {searchQuery.length > 0 && searchQuery.length < 2 && (
              <p className="text-center text-gray-400 text-sm py-4">
                Digite pelo menos 2 caracteres para buscar
              </p>
            )}
          </div>
        </div>

        {/* Right: Card list sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Lista do Deck
              </h2>
              <span
                className={`text-sm font-bold px-2.5 py-1 rounded-full ${
                  totalCards === MAX_DECK_SIZE
                    ? "bg-green-100 text-green-700"
                    : totalCards > MAX_DECK_SIZE
                      ? "bg-red-100 text-red-700"
                      : "bg-gray-100 text-gray-700"
                }`}
              >
                {totalCards}/{MAX_DECK_SIZE}
              </span>
            </div>

            {/* Category counts */}
            <div className="flex gap-2 mb-4 text-xs">
              <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                Pokemon: {pokemonCount}
              </span>
              <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                Trainer: {trainerCount}
              </span>
              <span className="bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                Energy: {energyCount}
              </span>
            </div>

            {/* Card list */}
            {cards.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-8">
                Use a busca para adicionar cartas ao deck
              </p>
            ) : (
              <div className="space-y-1 max-h-[60vh] overflow-y-auto">
                {/* Pokemon */}
                {cards.filter((e) => e.card.card_type === "pokemon").length > 0 && (
                  <CardListSection
                    title="Pokemon"
                    entries={cards.filter((e) => e.card.card_type === "pokemon")}
                    onAdd={addCard}
                    onRemove={removeCard}
                    onRemoveAll={removeAllCopies}
                    totalCards={totalCards}
                  />
                )}
                {/* Trainers */}
                {cards.filter((e) => e.card.card_type === "trainer").length > 0 && (
                  <CardListSection
                    title="Treinadores"
                    entries={cards.filter((e) => e.card.card_type === "trainer")}
                    onAdd={addCard}
                    onRemove={removeCard}
                    onRemoveAll={removeAllCopies}
                    totalCards={totalCards}
                  />
                )}
                {/* Energy */}
                {cards.filter((e) => e.card.card_type === "energy").length > 0 && (
                  <CardListSection
                    title="Energias"
                    entries={cards.filter((e) => e.card.card_type === "energy")}
                    onAdd={addCard}
                    onRemove={removeCard}
                    onRemoveAll={removeAllCopies}
                    totalCards={totalCards}
                  />
                )}
              </div>
            )}

            {/* Submit */}
            {submitError && (
              <div className="bg-red-50 text-red-700 px-3 py-2 rounded-lg text-sm mt-4">
                {submitError}
              </div>
            )}

            <button
              onClick={handleSubmit}
              disabled={createDeck.isPending || totalCards !== MAX_DECK_SIZE || !name.trim()}
              className="w-full mt-4 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {createDeck.isPending ? "Criando..." : "Criar Deck"}
            </button>

            {totalCards > 0 && totalCards !== MAX_DECK_SIZE && (
              <p className="text-xs text-center text-gray-400 mt-2">
                {totalCards < MAX_DECK_SIZE
                  ? `Faltam ${MAX_DECK_SIZE - totalCards} cartas`
                  : `${totalCards - MAX_DECK_SIZE} cartas a mais`}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function CardListSection({
  title,
  entries,
  onAdd,
  onRemove,
  onRemoveAll,
  totalCards,
}: {
  title: string;
  entries: DeckCardEntry[];
  onAdd: (card: Card) => void;
  onRemove: (cardId: number) => void;
  onRemoveAll: (cardId: number) => void;
  totalCards: number;
}) {
  return (
    <div className="mb-3">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
        {title}
      </p>
      {entries.map((entry) => (
        <div
          key={entry.card.id}
          className="flex items-center gap-1 py-1 group"
        >
          <span className="text-sm text-gray-900 flex-1 truncate">
            <span className="font-medium text-gray-600">{entry.quantity}x</span>{" "}
            {entry.card.name_pt || entry.card.name_en}
          </span>
          <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => onRemove(entry.card.id)}
              className="w-5 h-5 flex items-center justify-center text-xs bg-gray-200 text-gray-600 rounded hover:bg-red-200 hover:text-red-700 transition-colors"
              title="Remover uma copia"
            >
              -
            </button>
            <button
              onClick={() => onAdd(entry.card)}
              disabled={entry.quantity >= MAX_CARD_COPIES || totalCards >= MAX_DECK_SIZE}
              className="w-5 h-5 flex items-center justify-center text-xs bg-gray-200 text-gray-600 rounded hover:bg-green-200 hover:text-green-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              title="Adicionar uma copia"
            >
              +
            </button>
            <button
              onClick={() => onRemoveAll(entry.card.id)}
              className="w-5 h-5 flex items-center justify-center text-xs bg-gray-200 text-gray-600 rounded hover:bg-red-200 hover:text-red-700 transition-colors ml-0.5"
              title="Remover todas as copias"
            >
              x
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
