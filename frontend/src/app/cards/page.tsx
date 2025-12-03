'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import { getCards, importCards, getCardSets } from '@/lib/api';
import { Card as CardType, CardSet } from '@/types';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Image from 'next/image';

export default function CardsPage() {
  const [showImport, setShowImport] = useState(false);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [page, setPage] = useState(1);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['cards', page, search, typeFilter],
    queryFn: () => getCards({ page, page_size: 24, name: search || undefined, card_type: typeFilter || undefined }),
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
        <div className="flex flex-wrap gap-4">
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
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
          >
            <option value="">All Types</option>
            <option value="pokemon">Pokemon</option>
            <option value="trainer">Trainer</option>
            <option value="energy">Energy</option>
          </select>
        </div>
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
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
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
    </div>
  );
}
