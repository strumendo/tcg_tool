"use client";

import { useState } from "react";
import { useCardSearch } from "@/hooks/useCards";
import { useUpdateCollection } from "@/hooks/useCollection";
import { CardImage } from "@/components/deck/CardImage";
import type { Card } from "@/lib/types";

interface AddToCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AddToCollectionModal({
  isOpen,
  onClose,
}: AddToCollectionModalProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [quantity, setQuantity] = useState(1);

  const { data: searchResults, isLoading: searching } =
    useCardSearch(searchQuery);
  const updateCollection = useUpdateCollection();

  const handleAdd = () => {
    if (!selectedCard) return;
    updateCollection.mutate(
      { cardId: selectedCard.id, quantity },
      {
        onSuccess: () => {
          setSelectedCard(null);
          setQuantity(1);
          setSearchQuery("");
          onClose();
        },
      }
    );
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">
            Adicionar Cartas a Colecao
          </h2>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Search input */}
        <div className="p-5 border-b border-gray-100">
          <div className="relative">
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
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setSelectedCard(null);
              }}
              placeholder="Buscar carta por nome (minimo 2 caracteres)..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {/* Selected card detail */}
          {selectedCard && (
            <div className="mb-5 p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex items-center gap-4">
                <CardImage card={selectedCard} width={80} height={112} />
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">
                    {selectedCard.name_en}
                  </p>
                  {selectedCard.name_pt && (
                    <p className="text-sm text-gray-500">
                      {selectedCard.name_pt}
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {selectedCard.card_type}
                    {selectedCard.set && ` - ${selectedCard.set.code}`}
                    {selectedCard.regulation_mark &&
                      ` - Marca ${selectedCard.regulation_mark}`}
                  </p>

                  <div className="flex items-center gap-3 mt-3">
                    <label className="text-sm text-gray-700 font-medium">
                      Quantidade:
                    </label>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setQuantity(Math.max(1, quantity - 1))}
                        className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center text-gray-700 hover:bg-gray-300 transition-colors"
                      >
                        -
                      </button>
                      <span className="w-8 text-center font-bold text-gray-900">
                        {quantity}
                      </span>
                      <button
                        onClick={() => setQuantity(Math.min(99, quantity + 1))}
                        className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center text-gray-700 hover:bg-gray-300 transition-colors"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Search results grid */}
          {searching && (
            <div className="flex items-center justify-center py-8">
              <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
              <span className="ml-3 text-gray-500">Buscando cartas...</span>
            </div>
          )}

          {!searching &&
            searchQuery.length >= 2 &&
            searchResults &&
            searchResults.length === 0 && (
              <p className="text-center text-gray-500 py-8">
                Nenhuma carta encontrada para &quot;{searchQuery}&quot;
              </p>
            )}

          {!searching && searchResults && searchResults.length > 0 && (
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
              {searchResults.map((card) => (
                <div
                  key={card.id}
                  className={`cursor-pointer rounded-lg transition-all ${
                    selectedCard?.id === card.id
                      ? "ring-2 ring-blue-500 scale-105"
                      : "hover:scale-105"
                  }`}
                  onClick={() => {
                    setSelectedCard(card);
                    setQuantity(1);
                  }}
                >
                  <CardImage card={card} width={100} height={140} />
                  <p className="mt-1 text-xs text-gray-600 text-center truncate px-1">
                    {card.name_en}
                  </p>
                </div>
              ))}
            </div>
          )}

          {searchQuery.length < 2 && !selectedCard && (
            <div className="text-center py-8">
              <svg
                className="w-12 h-12 text-gray-300 mx-auto mb-3"
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
              <p className="text-gray-400 text-sm">
                Digite o nome da carta para buscar
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-5 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 font-medium transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleAdd}
            disabled={!selectedCard || updateCollection.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updateCollection.isPending ? "Adicionando..." : "Adicionar"}
          </button>
        </div>
      </div>
    </div>
  );
}
