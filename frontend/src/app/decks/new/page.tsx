'use client';

import { useState, useMemo } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getCards, createDeck, searchCards } from '@/lib/api';
import { Card as CardType, DeckFormat } from '@/types';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  MinusIcon,
  TrashIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Image from 'next/image';

interface DeckCardEntry {
  card: CardType;
  quantity: number;
}

export default function NewDeckPage() {
  const router = useRouter();
  const [deckName, setDeckName] = useState('');
  const [deckFormat, setDeckFormat] = useState<DeckFormat>('standard');
  const [archetype, setArchetype] = useState('');
  const [description, setDescription] = useState('');
  const [deckCards, setDeckCards] = useState<DeckCardEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [subtypeFilter, setSubtypeFilter] = useState('');
  const [energyFilter, setEnergyFilter] = useState('');
  const [cardPage, setCardPage] = useState(1);

  // Fetch available cards
  const { data: cardsData, isLoading: loadingCards } = useQuery({
    queryKey: ['cards-for-deck', cardPage, searchQuery, typeFilter, subtypeFilter, energyFilter],
    queryFn: () =>
      getCards({
        page: cardPage,
        page_size: 18,
        name: searchQuery || undefined,
        card_type: typeFilter || undefined,
        subtype: subtypeFilter || undefined,
        energy_type: energyFilter || undefined,
        standard_only: deckFormat === 'standard',
      }),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createDeck({
        name: deckName,
        format: deckFormat,
        description: description || undefined,
        archetype: archetype || undefined,
        cards: deckCards.map((dc) => ({ card_id: dc.card.id, quantity: dc.quantity })),
      }),
    onSuccess: () => {
      toast.success('Deck created successfully!');
      router.push('/decks');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to create deck');
    },
  });

  const availableCards: CardType[] = cardsData?.data?.cards || [];
  const totalCards = cardsData?.data?.total || 0;

  // Calculate deck stats
  const deckStats = useMemo(() => {
    let pokemon = 0;
    let trainer = 0;
    let energy = 0;
    let total = 0;

    deckCards.forEach((dc) => {
      total += dc.quantity;
      if (dc.card.card_type === 'pokemon') pokemon += dc.quantity;
      else if (dc.card.card_type === 'trainer') trainer += dc.quantity;
      else if (dc.card.card_type === 'energy') energy += dc.quantity;
    });

    return { pokemon, trainer, energy, total };
  }, [deckCards]);

  const addCard = (card: CardType) => {
    setDeckCards((prev) => {
      const existing = prev.find((dc) => dc.card.id === card.id);
      if (existing) {
        // Check 4-card limit (except basic energy)
        const isBasicEnergy = card.subtype === 'basic_energy';
        if (!isBasicEnergy && existing.quantity >= 4) {
          toast.error('Maximum 4 copies allowed (except basic energy)');
          return prev;
        }
        return prev.map((dc) =>
          dc.card.id === card.id ? { ...dc, quantity: dc.quantity + 1 } : dc
        );
      }
      return [...prev, { card, quantity: 1 }];
    });
  };

  const removeCard = (cardId: number) => {
    setDeckCards((prev) => {
      const existing = prev.find((dc) => dc.card.id === cardId);
      if (existing && existing.quantity > 1) {
        return prev.map((dc) =>
          dc.card.id === cardId ? { ...dc, quantity: dc.quantity - 1 } : dc
        );
      }
      return prev.filter((dc) => dc.card.id !== cardId);
    });
  };

  const deleteCard = (cardId: number) => {
    setDeckCards((prev) => prev.filter((dc) => dc.card.id !== cardId));
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      pokemon: 'bg-red-500',
      trainer: 'bg-blue-500',
      energy: 'bg-yellow-500',
    };
    return colors[type] || 'bg-gray-500';
  };

  const canSave = deckName.trim().length > 0 && deckCards.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeftIcon className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Build New Deck</h1>
          <p className="text-gray-600">Select cards to build your deck</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card Browser - Left Side */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search and Filters */}
          <Card padding="sm">
            <div className="flex flex-wrap gap-3">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search cards..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCardPage(1);
                    }}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                  />
                </div>
              </div>
              <select
                value={typeFilter}
                onChange={(e) => {
                  setTypeFilter(e.target.value);
                  setCardPage(1);
                }}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Types</option>
                <option value="pokemon">Pokemon</option>
                <option value="trainer">Trainer</option>
                <option value="energy">Energy</option>
              </select>
              <select
                value={subtypeFilter}
                onChange={(e) => {
                  setSubtypeFilter(e.target.value);
                  setCardPage(1);
                }}
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
              </select>
              <select
                value={energyFilter}
                onChange={(e) => {
                  setEnergyFilter(e.target.value);
                  setCardPage(1);
                }}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Energy</option>
                <option value="fire">Fire</option>
                <option value="water">Water</option>
                <option value="grass">Grass</option>
                <option value="lightning">Lightning</option>
                <option value="psychic">Psychic</option>
                <option value="fighting">Fighting</option>
                <option value="darkness">Darkness</option>
                <option value="metal">Metal</option>
                <option value="colorless">Colorless</option>
              </select>
            </div>
          </Card>

          {/* Card Grid */}
          {loadingCards ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
            </div>
          ) : availableCards.length === 0 ? (
            <Card className="text-center py-12">
              <p className="text-gray-600">No cards found. Import cards first!</p>
            </Card>
          ) : (
            <>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                {availableCards.map((card) => {
                  const inDeck = deckCards.find((dc) => dc.card.id === card.id);
                  return (
                    <div
                      key={card.id}
                      onClick={() => addCard(card)}
                      className={`relative bg-white rounded-lg border-2 overflow-hidden cursor-pointer transition-all hover:scale-105 ${
                        inDeck ? 'border-pokemon-blue ring-2 ring-pokemon-blue/30' : 'border-gray-200'
                      }`}
                    >
                      {card.image_small ? (
                        <div className="aspect-[2.5/3.5] relative">
                          <Image
                            src={card.image_small}
                            alt={card.name}
                            fill
                            className="object-contain"
                            sizes="100px"
                          />
                        </div>
                      ) : (
                        <div className="aspect-[2.5/3.5] bg-gray-100 flex items-center justify-center p-1">
                          <span className="text-xs text-gray-500 text-center">{card.name}</span>
                        </div>
                      )}
                      {inDeck && (
                        <div className="absolute top-1 right-1 bg-pokemon-blue text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                          {inDeck.quantity}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Pagination */}
              <div className="flex justify-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setCardPage((p) => Math.max(1, p - 1))}
                  disabled={cardPage === 1}
                >
                  Previous
                </Button>
                <span className="px-3 py-1 text-sm text-gray-600">
                  Page {cardPage} of {Math.ceil(totalCards / 18)}
                </span>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setCardPage((p) => p + 1)}
                  disabled={cardPage * 18 >= totalCards}
                >
                  Next
                </Button>
              </div>
            </>
          )}
        </div>

        {/* Deck Builder - Right Side */}
        <div className="space-y-4">
          {/* Deck Info */}
          <Card>
            <CardHeader>
              <CardTitle>Deck Info</CardTitle>
            </CardHeader>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Deck Name *
                </label>
                <input
                  type="text"
                  value={deckName}
                  onChange={(e) => setDeckName(e.target.value)}
                  placeholder="My Awesome Deck"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Format
                </label>
                <select
                  value={deckFormat}
                  onChange={(e) => setDeckFormat(e.target.value as DeckFormat)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                >
                  <option value="standard">Standard</option>
                  <option value="expanded">Expanded</option>
                  <option value="unlimited">Unlimited</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Archetype
                </label>
                <input
                  type="text"
                  value={archetype}
                  onChange={(e) => setArchetype(e.target.value)}
                  placeholder="e.g. Charizard ex"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                />
              </div>
            </div>
          </Card>

          {/* Deck Stats */}
          <Card>
            <div className="flex justify-between items-center mb-3">
              <span className="font-semibold text-gray-900">
                Cards: {deckStats.total}/60
              </span>
              {deckStats.total !== 60 && (
                <span className="text-sm text-orange-600">
                  {deckStats.total < 60 ? `Need ${60 - deckStats.total} more` : `${deckStats.total - 60} over`}
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <div className="flex-1 bg-red-100 rounded p-2 text-center">
                <div className="text-lg font-bold text-red-700">{deckStats.pokemon}</div>
                <div className="text-xs text-red-600">Pokemon</div>
              </div>
              <div className="flex-1 bg-blue-100 rounded p-2 text-center">
                <div className="text-lg font-bold text-blue-700">{deckStats.trainer}</div>
                <div className="text-xs text-blue-600">Trainer</div>
              </div>
              <div className="flex-1 bg-yellow-100 rounded p-2 text-center">
                <div className="text-lg font-bold text-yellow-700">{deckStats.energy}</div>
                <div className="text-xs text-yellow-600">Energy</div>
              </div>
            </div>
          </Card>

          {/* Deck Cards List */}
          <Card className="max-h-[400px] overflow-y-auto">
            <CardHeader>
              <CardTitle>Deck List</CardTitle>
            </CardHeader>
            {deckCards.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                Click cards to add them to your deck
              </p>
            ) : (
              <div className="space-y-2">
                {deckCards.map((dc) => (
                  <div
                    key={dc.card.id}
                    className="flex items-center gap-2 p-2 bg-gray-50 rounded"
                  >
                    <div
                      className={`w-2 h-8 rounded ${getTypeColor(dc.card.card_type)}`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {dc.card.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {dc.card.set?.code} {dc.card.set_number}
                      </p>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => removeCard(dc.card.id)}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        <MinusIcon className="h-4 w-4 text-gray-600" />
                      </button>
                      <span className="w-6 text-center font-medium">{dc.quantity}</span>
                      <button
                        onClick={() => addCard(dc.card)}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        <PlusIcon className="h-4 w-4 text-gray-600" />
                      </button>
                      <button
                        onClick={() => deleteCard(dc.card.id)}
                        className="p-1 hover:bg-red-100 rounded ml-1"
                      >
                        <TrashIcon className="h-4 w-4 text-red-500" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Save Button */}
          <Button
            onClick={() => createMutation.mutate()}
            disabled={!canSave}
            loading={createMutation.isPending}
            className="w-full"
          >
            Create Deck
          </Button>
        </div>
      </div>
    </div>
  );
}
