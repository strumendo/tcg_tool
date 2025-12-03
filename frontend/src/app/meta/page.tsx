'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import { getTop10Decks, getDecks, compareDeckToMeta, importMetaFromFile, getLatestSnapshot } from '@/lib/api';
import { MetaDeck, Deck, DeckComparisonResult } from '@/types';
import toast from 'react-hot-toast';

export default function MetaPage() {
  const [showImport, setShowImport] = useState(false);
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);
  const [comparisonResult, setComparisonResult] = useState<DeckComparisonResult | null>(null);
  const queryClient = useQueryClient();

  const { data: metaData, isLoading: loadingMeta } = useQuery({
    queryKey: ['top10'],
    queryFn: () => getTop10Decks(),
  });

  const { data: decksData } = useQuery({
    queryKey: ['decks'],
    queryFn: () => getDecks(),
  });

  const importMutation = useMutation({
    mutationFn: (file: File) => importMetaFromFile(file),
    onSuccess: () => {
      toast.success('Meta data imported!');
      queryClient.invalidateQueries({ queryKey: ['top10'] });
      setShowImport(false);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to import meta data');
    },
  });

  const compareMutation = useMutation({
    mutationFn: (deckId: number) => compareDeckToMeta(deckId),
    onSuccess: (res) => {
      setComparisonResult(res.data);
    },
    onError: () => {
      toast.error('Failed to compare deck');
    },
  });

  const topDecks: MetaDeck[] = metaData?.data?.top_decks || [];
  const snapshotName = metaData?.data?.snapshot_name;
  const userDecks: Deck[] = decksData?.data?.decks || [];

  const getWinRateColor = (wr: number) => {
    if (wr >= 55) return 'text-green-600';
    if (wr >= 45) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meta Analysis</h1>
          <p className="text-gray-600 mt-1">
            {snapshotName ? `Current: ${snapshotName}` : 'Compare your decks against the meta'}
          </p>
        </div>
        <Button onClick={() => setShowImport(!showImport)}>
          Import Meta Data
        </Button>
      </div>

      {showImport && (
        <Card>
          <CardHeader>
            <CardTitle>Import Meta Data</CardTitle>
          </CardHeader>
          <p className="text-sm text-gray-600 mb-4">
            Import meta data from LimitlessTCG or other sources. Supports JSON and CSV formats.
          </p>
          <FileUpload
            onUpload={(files) => importMutation.mutate(files[0])}
            accept={{
              'application/json': ['.json'],
              'text/csv': ['.csv'],
            }}
            label="Upload meta data"
            hint="JSON or CSV with deck archetypes and win rates"
          />
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top 10 Decks */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Top 10 Meta Decks</CardTitle>
            </CardHeader>

            {loadingMeta ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
              </div>
            ) : topDecks.length === 0 ? (
              <div className="text-center py-8 text-gray-600">
                No meta data available. Import meta data to get started.
              </div>
            ) : (
              <div className="space-y-3">
                {topDecks.map((deck, index) => (
                  <div
                    key={deck.archetype}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <span className="text-2xl font-bold text-gray-300 w-8">
                        {index + 1}
                      </span>
                      <div>
                        <p className="font-semibold text-gray-900">{deck.archetype}</p>
                        <p className="text-sm text-gray-600">
                          {deck.meta_share.toFixed(1)}% of meta
                        </p>
                      </div>
                    </div>
                    {deck.win_rate && (
                      <span className={`font-semibold ${getWinRateColor(deck.win_rate)}`}>
                        {deck.win_rate.toFixed(1)}% WR
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Deck Comparison */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Compare Your Deck</CardTitle>
            </CardHeader>

            <div className="space-y-4">
              <select
                value={selectedDeckId || ''}
                onChange={(e) => setSelectedDeckId(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              >
                <option value="">Select a deck...</option>
                {userDecks.map((deck) => (
                  <option key={deck.id} value={deck.id}>
                    {deck.name} ({deck.archetype || 'Unknown'})
                  </option>
                ))}
              </select>

              <Button
                onClick={() => selectedDeckId && compareMutation.mutate(selectedDeckId)}
                disabled={!selectedDeckId || topDecks.length === 0}
                loading={compareMutation.isPending}
                className="w-full"
              >
                Analyze vs Meta
              </Button>
            </div>
          </Card>

          {/* Comparison Results */}
          {comparisonResult && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>{comparisonResult.deck_archetype}</CardTitle>
              </CardHeader>

              <div className="space-y-4">
                {/* Overall Score */}
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-pokemon-blue">
                    {comparisonResult.overall_meta_score.toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-600">Expected Win Rate vs Meta</p>
                </div>

                {/* Meta Position */}
                {comparisonResult.meta_position && (
                  <p className="text-center text-gray-600">
                    Currently #{comparisonResult.meta_position} in meta
                  </p>
                )}

                {/* Strengths */}
                {comparisonResult.strengths.length > 0 && (
                  <div>
                    <p className="font-semibold text-green-700 mb-2">Strengths</p>
                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                      {comparisonResult.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Weaknesses */}
                {comparisonResult.weaknesses.length > 0 && (
                  <div>
                    <p className="font-semibold text-red-700 mb-2">Weaknesses</p>
                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                      {comparisonResult.weaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Suggestions */}
                {comparisonResult.suggestions.length > 0 && (
                  <div>
                    <p className="font-semibold text-pokemon-blue mb-2">Suggestions</p>
                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                      {comparisonResult.suggestions.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
