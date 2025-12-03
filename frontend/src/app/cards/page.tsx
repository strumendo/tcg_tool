'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import { getCards, importCards, getCardSets } from '@/lib/api';
import { Card as CardType, CardSet } from '@/types';
import { MagnifyingGlassIcon, XMarkIcon, FunnelIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Image from 'next/image';

export default function CardsPage() {
  const [showImport, setShowImport] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [subtypeFilter, setSubtypeFilter] = useState('');
  const [energyFilter, setEnergyFilter] = useState('');
  const [standardOnly, setStandardOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'hp' | 'created_at'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(1);
  const [selectedCard, setSelectedCard] = useState<CardType | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['cards', page, search, typeFilter, subtypeFilter, energyFilter, standardOnly, sortBy, sortOrder],
    queryFn: () => getCards({
      page,
      page_size: 24,
      name: search || undefined,
      card_type: typeFilter || undefined,
      subtype: subtypeFilter || undefined,
      energy_type: energyFilter || undefined,
      standard_only: standardOnly || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    }),
  });

  const { data: setsData } = useQuery({
    queryKey: ['card-sets'],
    queryFn: () => getCardSets(),
  });

  const importMutation = useMutation({
    mutationFn: (file: File) => importCards(file),
    onSuccess: (res) => {
      const result = res.data;
      toast.success(`Imported ${result.imported} cards (${result.skipped} skipped)`);
      queryClient.invalidateQueries({ queryKey: ['cards'] });
      setShowImport(false);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to import cards');
    },
  });

  const cards: CardType[] = data?.data?.cards || [];
  const total = data?.data?.total || 0;
  const sets: CardSet[] = setsData?.data || [];

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      pokemon: 'bg-pokemon-red text-white',
      trainer: 'bg-pokemon-blue text-white',
      energy: 'bg-pokemon-gold text-black',
    };
    return colors[type] || 'bg-gray-200';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Card Collection</h1>
          <p className="text-gray-600 mt-1">
            {total > 0 ? `${total} cards in database` : 'Import cards to get started'}
          </p>
        </div>
        <Button onClick={() => setShowImport(!showImport)}>
          Import Cards
        </Button>
      </div>

      {showImport && (
        <Card>
          <CardHeader>
            <CardTitle>Import Cards</CardTitle>
          </CardHeader>
          <p className="text-sm text-gray-600 mb-4">
            Import cards from JSON or CSV file. You can export card data from LimitlessTCG or Pokemon TCG API.
          </p>
          <FileUpload
            onUpload={(files) => importMutation.mutate(files[0])}
            accept={{
              'application/json': ['.json'],
              'text/csv': ['.csv'],
            }}
            label="Upload card data"
            hint="Supports JSON or CSV format"
          />
        </Card>
      )}

      {/* Search and Filters */}
      <Card padding="sm">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search cards..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={typeFilter}
            onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue text-sm"
          >
            <option value="">All Types</option>
            <option value="pokemon">Pokemon</option>
            <option value="trainer">Trainer</option>
            <option value="energy">Energy</option>
          </select>
          <Button variant="secondary" onClick={() => setShowFilters(!showFilters)}>
            <FunnelIcon className="h-4 w-4 mr-1" />
            Filters
          </Button>
        </div>

        {/* Extended Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex flex-wrap gap-3">
              <select
                value={subtypeFilter}
                onChange={(e) => { setSubtypeFilter(e.target.value); setPage(1); }}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Subtypes</option>
                <option value="basic">Basic</option>
                <option value="stage1">Stage 1</option>
                <option value="stage2">Stage 2</option>
                <option value="ex">ex</option>
                <option value="v">V</option>
                <option value="vmax">VMAX</option>
                <option value="vstar">VSTAR</option>
                <option value="item">Item</option>
                <option value="supporter">Supporter</option>
                <option value="stadium">Stadium</option>
                <option value="tool">Tool</option>
              </select>
              <select
                value={energyFilter}
                onChange={(e) => { setEnergyFilter(e.target.value); setPage(1); }}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Energy Types</option>
                <option value="fire">Fire</option>
                <option value="water">Water</option>
                <option value="grass">Grass</option>
                <option value="lightning">Lightning</option>
                <option value="psychic">Psychic</option>
                <option value="fighting">Fighting</option>
                <option value="darkness">Darkness</option>
                <option value="metal">Metal</option>
                <option value="dragon">Dragon</option>
                <option value="colorless">Colorless</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => { setSortBy(e.target.value as any); setPage(1); }}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="name">Sort by Name</option>
                <option value="hp">Sort by HP</option>
                <option value="created_at">Sort by Date Added</option>
              </select>
              <select
                value={sortOrder}
                onChange={(e) => { setSortOrder(e.target.value as any); setPage(1); }}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
              <label className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg cursor-pointer">
                <input
                  type="checkbox"
                  checked={standardOnly}
                  onChange={(e) => { setStandardOnly(e.target.checked); setPage(1); }}
                  className="rounded text-pokemon-blue"
                />
                <span className="text-sm">Standard Legal Only</span>
              </label>
            </div>
          </div>
        )}
      </Card>

      {/* Sets Summary */}
      {sets.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {sets.slice(0, 10).map((set) => (
            <span key={set.id} className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">
              {set.name}
            </span>
          ))}
          {sets.length > 10 && (
            <span className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">
              +{sets.length - 10} more
            </span>
          )}
        </div>
      )}

      {/* Cards Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : cards.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-gray-600">
            {search || typeFilter ? 'No cards match your search' : 'No cards in database. Import some cards to get started!'}
          </p>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {cards.map((card) => (
              <div
                key={card.id}
                onClick={() => setSelectedCard(card)}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer hover:scale-105"
              >
                {card.image_small ? (
                  <div className="aspect-[2.5/3.5] relative bg-gray-100">
                    <Image
                      src={card.image_small}
                      alt={card.name}
                      fill
                      className="object-contain"
                      sizes="(max-width: 768px) 50vw, (max-width: 1200px) 25vw, 16vw"
                    />
                  </div>
                ) : (
                  <div className="aspect-[2.5/3.5] bg-gray-100 flex items-center justify-center">
                    <span className="text-gray-400 text-sm">{card.name}</span>
                  </div>
                )}
                <div className="p-2">
                  <p className="text-sm font-medium text-gray-900 truncate">{card.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-1.5 py-0.5 rounded text-xs ${getTypeColor(card.card_type)}`}>
                      {card.card_type}
                    </span>
                    {card.set && (
                      <span className="text-xs text-gray-500">{card.set.code}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-center gap-2">
            <Button
              variant="secondary"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="px-4 py-2 text-gray-600">
              Page {page} of {Math.ceil(total / 24)}
            </span>
            <Button
              variant="secondary"
              onClick={() => setPage(p => p + 1)}
              disabled={page * 24 >= total}
            >
              Next
            </Button>
          </div>
        </>
      )}

      {/* Card Detail Modal */}
      {selectedCard && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedCard(null)}
        >
          <div
            className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start p-4 border-b">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{selectedCard.name}</h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-0.5 rounded text-xs ${getTypeColor(selectedCard.card_type)}`}>
                    {selectedCard.card_type}
                  </span>
                  {selectedCard.subtype && (
                    <span className="text-xs text-gray-600">{selectedCard.subtype}</span>
                  )}
                  {selectedCard.set && (
                    <span className="text-xs text-gray-500">
                      {selectedCard.set.name} ({selectedCard.set.code})
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => setSelectedCard(null)}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Card Image */}
              <div className="flex justify-center">
                {selectedCard.image_large || selectedCard.image_small ? (
                  <div className="w-64 aspect-[2.5/3.5] relative">
                    <Image
                      src={selectedCard.image_large || selectedCard.image_small || ''}
                      alt={selectedCard.name}
                      fill
                      className="object-contain rounded-lg"
                      sizes="256px"
                    />
                  </div>
                ) : (
                  <div className="w-64 aspect-[2.5/3.5] bg-gray-100 rounded-lg flex items-center justify-center">
                    <span className="text-gray-400">No Image</span>
                  </div>
                )}
              </div>

              {/* Card Details */}
              <div className="space-y-4">
                {selectedCard.hp && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">HP</span>
                    <span className="font-semibold">{selectedCard.hp}</span>
                  </div>
                )}
                {selectedCard.energy_type && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Energy Type</span>
                    <span className="font-semibold capitalize">{selectedCard.energy_type}</span>
                  </div>
                )}
                {selectedCard.weakness && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Weakness</span>
                    <span className="font-semibold">{selectedCard.weakness}</span>
                  </div>
                )}
                {selectedCard.resistance && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resistance</span>
                    <span className="font-semibold">{selectedCard.resistance}</span>
                  </div>
                )}
                {selectedCard.retreat_cost !== undefined && selectedCard.retreat_cost !== null && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Retreat Cost</span>
                    <span className="font-semibold">{selectedCard.retreat_cost}</span>
                  </div>
                )}
                {selectedCard.rarity && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Rarity</span>
                    <span className="font-semibold">{selectedCard.rarity}</span>
                  </div>
                )}
                {selectedCard.regulation_mark && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Regulation Mark</span>
                    <span className="font-semibold">{selectedCard.regulation_mark}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">Standard Legal</span>
                  <span className={`font-semibold ${selectedCard.is_standard_legal ? 'text-green-600' : 'text-red-600'}`}>
                    {selectedCard.is_standard_legal ? 'Yes' : 'No'}
                  </span>
                </div>

                {/* Abilities */}
                {selectedCard.abilities && selectedCard.abilities.length > 0 && (
                  <div className="pt-2 border-t">
                    <p className="font-semibold text-gray-900 mb-2">Abilities</p>
                    {selectedCard.abilities.map((ability: any, idx: number) => (
                      <div key={idx} className="bg-purple-50 p-2 rounded mb-2">
                        <p className="font-medium text-purple-700">{ability.name}</p>
                        <p className="text-sm text-gray-600">{ability.text}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Attacks */}
                {selectedCard.attacks && selectedCard.attacks.length > 0 && (
                  <div className="pt-2 border-t">
                    <p className="font-semibold text-gray-900 mb-2">Attacks</p>
                    {selectedCard.attacks.map((attack: any, idx: number) => (
                      <div key={idx} className="bg-gray-50 p-2 rounded mb-2">
                        <div className="flex justify-between">
                          <p className="font-medium">{attack.name}</p>
                          {attack.damage && <span className="font-bold text-red-600">{attack.damage}</span>}
                        </div>
                        {attack.cost && (
                          <p className="text-xs text-gray-500">Cost: {attack.cost.join(', ')}</p>
                        )}
                        {attack.text && <p className="text-sm text-gray-600 mt-1">{attack.text}</p>}
                      </div>
                    ))}
                  </div>
                )}

                {/* Rules */}
                {selectedCard.rules && (
                  <div className="pt-2 border-t">
                    <p className="font-semibold text-gray-900 mb-2">Rules</p>
                    <p className="text-sm text-gray-600">{selectedCard.rules}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
