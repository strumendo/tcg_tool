'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getDeck, deleteDeck, compareDeckToMeta } from '@/lib/api';
import { Deck, DeckCard, DeckComparisonResult } from '@/types';
import {
  ArrowLeftIcon,
  TrashIcon,
  ChartBarIcon,
  PencilIcon,
  DocumentDuplicateIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Image from 'next/image';
import Link from 'next/link';
import { useState, useMemo } from 'react';

export default function DeckDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const deckId = Number(params.id);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<DeckComparisonResult | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['deck', deckId],
    queryFn: () => getDeck(deckId),
    enabled: !isNaN(deckId),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteDeck(deckId),
    onSuccess: () => {
      toast.success('Deck deleted');
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      router.push('/decks');
    },
    onError: () => {
      toast.error('Failed to delete deck');
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: () => compareDeckToMeta(deckId),
    onSuccess: (res) => {
      setAnalysisResult(res.data);
      setShowAnalysis(true);
    },
    onError: () => {
      toast.error('Failed to analyze deck');
    },
  });

  const deck: Deck | undefined = data?.data;

  // Group cards by type
  const groupedCards = useMemo(() => {
    if (!deck?.cards) return { pokemon: [], trainer: [], energy: [] };

    const groups: Record<string, DeckCard[]> = {
      pokemon: [],
      trainer: [],
      energy: [],
    };

    deck.cards.forEach((dc) => {
      const type = dc.card?.card_type || 'trainer';
      if (groups[type]) {
        groups[type].push(dc);
      }
    });

    // Sort by name within each group
    Object.keys(groups).forEach((key) => {
      groups[key].sort((a, b) => (a.card?.name || '').localeCompare(b.card?.name || ''));
    });

    return groups;
  }, [deck]);

  const exportDeckList = () => {
    if (!deck) return;

    let text = `Pokemon: ${deck.pokemon_count}\n`;
    groupedCards.pokemon.forEach((dc) => {
      text += `${dc.quantity} ${dc.card?.name} ${dc.card?.set?.code || ''} ${dc.card?.set_number || ''}\n`;
    });

    text += `\nTrainer: ${deck.trainer_count}\n`;
    groupedCards.trainer.forEach((dc) => {
      text += `${dc.quantity} ${dc.card?.name} ${dc.card?.set?.code || ''} ${dc.card?.set_number || ''}\n`;
    });

    text += `\nEnergy: ${deck.energy_count}\n`;
    groupedCards.energy.forEach((dc) => {
      text += `${dc.quantity} ${dc.card?.name}\n`;
    });

    navigator.clipboard.writeText(text);
    toast.success('Deck list copied to clipboard!');
  };

  const getFormatColor = (format: string) => {
    switch (format) {
      case 'standard':
        return 'bg-green-100 text-green-800';
      case 'expanded':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading deck...</p>
      </div>
    );
  }

  if (error || !deck) {
    return (
      <Card className="text-center py-12">
        <p className="text-red-600">Failed to load deck</p>
        <Button variant="secondary" onClick={() => router.push('/decks')} className="mt-4">
          Back to Decks
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push('/decks')}>
            <ArrowLeftIcon className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{deck.name}</h1>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getFormatColor(deck.format)}`}>
                {deck.format}
              </span>
            </div>
            {deck.archetype && <p className="text-gray-600">{deck.archetype}</p>}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={exportDeckList}>
            <DocumentDuplicateIcon className="h-4 w-4 mr-2" />
            Copy List
          </Button>
          <Button variant="secondary" onClick={() => analyzeMutation.mutate()} loading={analyzeMutation.isPending}>
            <ChartBarIcon className="h-4 w-4 mr-2" />
            Analyze
          </Button>
          <Button
            variant="ghost"
            onClick={() => {
              if (confirm('Delete this deck?')) deleteMutation.mutate();
            }}
          >
            <TrashIcon className="h-5 w-5 text-red-500" />
          </Button>
        </div>
      </div>

      {/* Meta Analysis Results */}
      {showAnalysis && analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle>Meta Analysis</CardTitle>
          </CardHeader>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-pokemon-blue">
                {analysisResult.overall_meta_score.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Expected Win Rate</p>
            </div>
            {analysisResult.meta_position && (
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-3xl font-bold text-gray-900">#{analysisResult.meta_position}</p>
                <p className="text-sm text-gray-600">Meta Position</p>
              </div>
            )}
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-gray-900">
                {Object.keys(analysisResult.matchup_analysis).length}
              </p>
              <p className="text-sm text-gray-600">Matchups Analyzed</p>
            </div>
          </div>

          {/* Matchups */}
          {Object.keys(analysisResult.matchup_analysis).length > 0 && (
            <div className="mt-4">
              <p className="font-semibold mb-2">Key Matchups</p>
              <div className="space-y-2">
                {Object.entries(analysisResult.matchup_analysis)
                  .slice(0, 5)
                  .map(([deck, data]) => (
                    <div key={deck} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="text-sm">{deck}</span>
                      <span
                        className={`font-semibold ${
                          data.win_rate >= 55
                            ? 'text-green-600'
                            : data.win_rate >= 45
                            ? 'text-yellow-600'
                            : 'text-red-600'
                        }`}
                      >
                        {data.win_rate}%
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          <Button variant="secondary" onClick={() => setShowAnalysis(false)} className="mt-4">
            Close Analysis
          </Button>
        </Card>
      )}

      {/* Deck Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <p className="text-2xl font-bold text-gray-900">{deck.total_cards}</p>
          <p className="text-sm text-gray-600">Total Cards</p>
        </Card>
        <Card className="text-center p-4">
          <p className="text-2xl font-bold text-red-600">{deck.pokemon_count}</p>
          <p className="text-sm text-gray-600">Pokemon</p>
        </Card>
        <Card className="text-center p-4">
          <p className="text-2xl font-bold text-blue-600">{deck.trainer_count}</p>
          <p className="text-sm text-gray-600">Trainers</p>
        </Card>
        <Card className="text-center p-4">
          <p className="text-2xl font-bold text-yellow-600">{deck.energy_count}</p>
          <p className="text-sm text-gray-600">Energy</p>
        </Card>
      </div>

      {/* Card Lists */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Pokemon */}
        <Card>
          <CardHeader>
            <CardTitle className="text-red-600">Pokemon ({deck.pokemon_count})</CardTitle>
          </CardHeader>
          <div className="space-y-2">
            {groupedCards.pokemon.length === 0 ? (
              <p className="text-sm text-gray-500">No Pokemon</p>
            ) : (
              groupedCards.pokemon.map((dc) => (
                <div key={dc.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                  {dc.card?.image_small && (
                    <div className="w-8 h-11 relative flex-shrink-0">
                      <Image
                        src={dc.card.image_small}
                        alt={dc.card.name || ''}
                        fill
                        className="object-contain rounded"
                        sizes="32px"
                      />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{dc.card?.name}</p>
                    <p className="text-xs text-gray-500">
                      {dc.card?.set?.code} {dc.card?.set_number}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-gray-700">x{dc.quantity}</span>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Trainers */}
        <Card>
          <CardHeader>
            <CardTitle className="text-blue-600">Trainers ({deck.trainer_count})</CardTitle>
          </CardHeader>
          <div className="space-y-2">
            {groupedCards.trainer.length === 0 ? (
              <p className="text-sm text-gray-500">No Trainers</p>
            ) : (
              groupedCards.trainer.map((dc) => (
                <div key={dc.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                  {dc.card?.image_small && (
                    <div className="w-8 h-11 relative flex-shrink-0">
                      <Image
                        src={dc.card.image_small}
                        alt={dc.card.name || ''}
                        fill
                        className="object-contain rounded"
                        sizes="32px"
                      />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{dc.card?.name}</p>
                    <p className="text-xs text-gray-500">
                      {dc.card?.set?.code} {dc.card?.set_number}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-gray-700">x{dc.quantity}</span>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Energy */}
        <Card>
          <CardHeader>
            <CardTitle className="text-yellow-600">Energy ({deck.energy_count})</CardTitle>
          </CardHeader>
          <div className="space-y-2">
            {groupedCards.energy.length === 0 ? (
              <p className="text-sm text-gray-500">No Energy</p>
            ) : (
              groupedCards.energy.map((dc) => (
                <div key={dc.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{dc.card?.name}</p>
                  </div>
                  <span className="text-sm font-bold text-gray-700">x{dc.quantity}</span>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Description */}
      {deck.description && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <p className="text-gray-600">{deck.description}</p>
        </Card>
      )}
    </div>
  );
}
