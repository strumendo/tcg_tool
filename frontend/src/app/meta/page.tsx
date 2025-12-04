'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import {
  getTop10Decks,
  getDecks,
  compareDeckToMeta,
  importMetaFromFile,
  getMetaSnapshots,
} from '@/lib/api';
import { MetaDeck, Deck, DeckComparisonResult, MetaSnapshot } from '@/types';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusIcon,
  SparklesIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  TrophyIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

type ViewMode = 'tier' | 'list' | 'matchups';

export default function MetaPage() {
  const [showImport, setShowImport] = useState(false);
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);
  const [selectedSnapshotId, setSelectedSnapshotId] = useState<number | null>(null);
  const [comparisonResult, setComparisonResult] = useState<DeckComparisonResult | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('tier');
  const [expandedMatchups, setExpandedMatchups] = useState<Set<string>>(new Set());
  const queryClient = useQueryClient();

  const { data: metaData, isLoading: loadingMeta } = useQuery({
    queryKey: ['top10', selectedSnapshotId],
    queryFn: () => getTop10Decks(selectedSnapshotId || undefined),
  });

  const { data: snapshotsData } = useQuery({
    queryKey: ['snapshots'],
    queryFn: () => getMetaSnapshots(),
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
      queryClient.invalidateQueries({ queryKey: ['snapshots'] });
      setShowImport(false);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to import meta data');
    },
  });

  const compareMutation = useMutation({
    mutationFn: (deckId: number) => compareDeckToMeta(deckId, selectedSnapshotId || undefined),
    onSuccess: (res) => {
      setComparisonResult(res.data);
    },
    onError: () => {
      toast.error('Failed to compare deck');
    },
  });

  const topDecks: MetaDeck[] = metaData?.data?.top_decks || [];
  const snapshotName = metaData?.data?.snapshot_name;
  const snapshotDate = metaData?.data?.snapshot_date;
  const userDecks: Deck[] = decksData?.data?.decks || [];
  const snapshots: MetaSnapshot[] = snapshotsData?.data?.snapshots || [];

  // Group decks into tiers
  const getTier = (rank: number, metaShare: number): { tier: string; color: string; bg: string } => {
    if (rank <= 3 || metaShare >= 10) return { tier: 'S', color: 'text-red-600', bg: 'bg-red-50 border-red-200' };
    if (rank <= 5 || metaShare >= 7) return { tier: 'A', color: 'text-orange-600', bg: 'bg-orange-50 border-orange-200' };
    if (rank <= 8 || metaShare >= 4) return { tier: 'B', color: 'text-yellow-600', bg: 'bg-yellow-50 border-yellow-200' };
    return { tier: 'C', color: 'text-gray-600', bg: 'bg-gray-50 border-gray-200' };
  };

  const getWinRateColor = (wr: number) => {
    if (wr >= 55) return 'text-green-600';
    if (wr >= 50) return 'text-blue-600';
    if (wr >= 45) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getWinRateBg = (wr: number) => {
    if (wr >= 55) return 'bg-green-100';
    if (wr >= 50) return 'bg-blue-50';
    if (wr >= 45) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const toggleMatchup = (archetype: string) => {
    setExpandedMatchups((prev) => {
      const next = new Set(prev);
      if (next.has(archetype)) {
        next.delete(archetype);
      } else {
        next.add(archetype);
      }
      return next;
    });
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Group decks by tier for tier view
  const decksByTier = topDecks.reduce(
    (acc, deck, index) => {
      const { tier } = getTier(index + 1, deck.meta_share);
      if (!acc[tier]) acc[tier] = [];
      acc[tier].push({ ...deck, displayRank: index + 1 });
      return acc;
    },
    {} as Record<string, (MetaDeck & { displayRank: number })[]>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meta Analysis</h1>
          <p className="text-gray-600 mt-1">
            {snapshotName
              ? `${snapshotName} (${snapshotDate ? formatDate(snapshotDate) : ''})`
              : 'Compare your decks against the meta'}
          </p>
        </div>
        <div className="flex gap-2">
          {snapshots.length > 0 && (
            <select
              value={selectedSnapshotId || ''}
              onChange={(e) => setSelectedSnapshotId(e.target.value ? Number(e.target.value) : null)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue text-sm"
            >
              <option value="">Latest Snapshot</option>
              {snapshots.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          )}
          <Button onClick={() => setShowImport(!showImport)}>Import Meta Data</Button>
        </div>
      </div>

      {/* Import Card */}
      {showImport && (
        <Card>
          <CardHeader>
            <CardTitle>Import Meta Data</CardTitle>
          </CardHeader>
          <p className="text-sm text-gray-600 mb-4">
            Import meta data from LimitlessTCG, Play Pokemon, or other sources. Supports JSON and CSV formats.
          </p>
          <FileUpload
            onUpload={(files) => importMutation.mutate(files[0])}
            accept={{
              'application/json': ['.json'],
              'text/csv': ['.csv'],
            }}
            label="Upload meta data"
            hint="JSON or CSV with deck archetypes, meta share, and win rates"
          />
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 font-medium mb-2">Expected JSON format:</p>
            <pre className="text-xs text-gray-600 overflow-x-auto">
{`{
  "name": "Tournament Name",
  "snapshot_date": "2024-12-01",
  "decks": [
    {"archetype": "Charizard ex", "rank": 1, "meta_share": 15.2, "win_rate": 52.1}
  ]
}`}
            </pre>
          </div>
        </Card>
      )}

      {/* View Mode Toggle */}
      <div className="flex gap-2 border-b border-gray-200 pb-4">
        <button
          onClick={() => setViewMode('tier')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            viewMode === 'tier'
              ? 'bg-pokemon-blue text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <TrophyIcon className="h-4 w-4 inline mr-1" />
          Tier List
        </button>
        <button
          onClick={() => setViewMode('list')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            viewMode === 'list'
              ? 'bg-pokemon-blue text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <ChartBarIcon className="h-4 w-4 inline mr-1" />
          Rankings
        </button>
        <button
          onClick={() => setViewMode('matchups')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            viewMode === 'matchups'
              ? 'bg-pokemon-blue text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <SparklesIcon className="h-4 w-4 inline mr-1" />
          Matchups
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Area */}
        <div className="lg:col-span-2">
          {loadingMeta ? (
            <Card className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
            </Card>
          ) : topDecks.length === 0 ? (
            <Card className="text-center py-12">
              <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">No meta data available</p>
              <p className="text-sm text-gray-500">Import meta data to see tier rankings and matchups</p>
            </Card>
          ) : viewMode === 'tier' ? (
            /* Tier List View */
            <div className="space-y-4">
              {['S', 'A', 'B', 'C'].map((tier) => {
                const tierDecks = decksByTier[tier] || [];
                if (tierDecks.length === 0) return null;

                const tierInfo = getTier(tier === 'S' ? 1 : tier === 'A' ? 4 : tier === 'B' ? 6 : 9, 0);
                return (
                  <Card key={tier} className={`border ${tierInfo.bg}`}>
                    <div className="flex items-center gap-4 mb-4">
                      <span className={`text-3xl font-bold ${tierInfo.color}`}>{tier}</span>
                      <div className="h-px flex-1 bg-gray-200" />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {tierDecks.map((deck) => (
                        <div
                          key={deck.archetype}
                          className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-lg font-bold text-gray-300 w-6">
                              {deck.displayRank}
                            </span>
                            <div>
                              <p className="font-semibold text-gray-900">{deck.archetype}</p>
                              <p className="text-xs text-gray-500">{deck.meta_share.toFixed(1)}% meta</p>
                            </div>
                          </div>
                          {deck.win_rate && (
                            <span className={`text-sm font-medium ${getWinRateColor(deck.win_rate)}`}>
                              {deck.win_rate.toFixed(1)}%
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </Card>
                );
              })}
            </div>
          ) : viewMode === 'list' ? (
            /* Rankings View */
            <Card>
              <CardHeader>
                <CardTitle>Meta Rankings</CardTitle>
              </CardHeader>
              <div className="space-y-2">
                {topDecks.map((deck, index) => {
                  const { color, bg } = getTier(index + 1, deck.meta_share);
                  return (
                    <div
                      key={deck.archetype}
                      className={`flex items-center justify-between p-4 rounded-lg border ${bg}`}
                    >
                      <div className="flex items-center gap-4">
                        <span className={`text-2xl font-bold ${color} w-8`}>{index + 1}</span>
                        <div>
                          <p className="font-semibold text-gray-900">{deck.archetype}</p>
                          <div className="flex gap-4 text-sm text-gray-600">
                            <span>{deck.meta_share.toFixed(1)}% meta share</span>
                            {deck.top8_count && <span>{deck.top8_count} Top 8</span>}
                            {deck.day2_conversion && (
                              <span>{deck.day2_conversion.toFixed(0)}% Day 2</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        {deck.win_rate && (
                          <p className={`text-lg font-bold ${getWinRateColor(deck.win_rate)}`}>
                            {deck.win_rate.toFixed(1)}%
                          </p>
                        )}
                        <p className="text-xs text-gray-500">Win Rate</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          ) : (
            /* Matchups View */
            <Card>
              <CardHeader>
                <CardTitle>Matchup Analysis</CardTitle>
              </CardHeader>
              <p className="text-sm text-gray-600 mb-4">
                Click on a deck to see its matchups against other meta decks
              </p>
              <div className="space-y-2">
                {topDecks.map((deck, index) => (
                  <div key={deck.archetype} className="border rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleMatchup(deck.archetype)}
                      className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-gray-400">{index + 1}</span>
                        <span className="font-semibold">{deck.archetype}</span>
                      </div>
                      {expandedMatchups.has(deck.archetype) ? (
                        <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                    {expandedMatchups.has(deck.archetype) && deck.matchups && (
                      <div className="p-4 border-t bg-white">
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                          {Object.entries(deck.matchups).map(([opponent, winRate]) => {
                            const wr = winRate as number;
                            return (
                              <div
                                key={opponent}
                                className={`p-2 rounded text-center ${getWinRateBg(wr)}`}
                              >
                                <p className="text-xs text-gray-600 truncate">{opponent}</p>
                                <p className={`font-bold ${getWinRateColor(wr)}`}>
                                  {wr >= 50 ? (
                                    <ArrowTrendingUpIcon className="h-3 w-3 inline mr-1" />
                                  ) : wr < 50 ? (
                                    <ArrowTrendingDownIcon className="h-3 w-3 inline mr-1" />
                                  ) : (
                                    <MinusIcon className="h-3 w-3 inline mr-1" />
                                  )}
                                  {wr.toFixed(0)}%
                                </p>
                              </div>
                            );
                          })}
                        </div>
                        {Object.keys(deck.matchups).length === 0 && (
                          <p className="text-center text-gray-500 text-sm">No matchup data available</p>
                        )}
                      </div>
                    )}
                    {expandedMatchups.has(deck.archetype) && !deck.matchups && (
                      <div className="p-4 border-t bg-white">
                        <p className="text-center text-gray-500 text-sm">No matchup data available</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Sidebar - Deck Comparison */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <SparklesIcon className="h-5 w-5 mr-2" />
                Compare Your Deck
              </CardTitle>
            </CardHeader>

            <div className="space-y-4">
              <select
                value={selectedDeckId || ''}
                onChange={(e) => {
                  setSelectedDeckId(e.target.value ? Number(e.target.value) : null);
                  setComparisonResult(null);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              >
                <option value="">Select a deck...</option>
                {userDecks.map((deck) => (
                  <option key={deck.id} value={deck.id}>
                    {deck.name} {deck.archetype && `(${deck.archetype})`}
                  </option>
                ))}
              </select>

              <Button
                onClick={() => selectedDeckId && compareMutation.mutate(selectedDeckId)}
                disabled={!selectedDeckId || topDecks.length === 0}
                loading={compareMutation.isPending}
                className="w-full"
              >
                <SparklesIcon className="h-4 w-4 mr-2" />
                Analyze vs Meta
              </Button>

              {userDecks.length === 0 && (
                <p className="text-xs text-gray-500 text-center">
                  Create a deck first to compare against meta
                </p>
              )}
            </div>
          </Card>

          {/* Comparison Results */}
          {comparisonResult && (
            <Card>
              <CardHeader>
                <CardTitle>{comparisonResult.deck_archetype}</CardTitle>
              </CardHeader>

              <div className="space-y-4">
                {/* Overall Score */}
                <div className="text-center p-4 bg-gradient-to-br from-pokemon-blue/10 to-pokemon-yellow/10 rounded-lg">
                  <p
                    className={`text-4xl font-bold ${getWinRateColor(comparisonResult.overall_meta_score)}`}
                  >
                    {comparisonResult.overall_meta_score.toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-600">Expected Win Rate vs Meta</p>
                </div>

                {/* Meta Position Badge */}
                {comparisonResult.meta_position && (
                  <div className="text-center">
                    <span
                      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                        getTier(comparisonResult.meta_position, 0).bg
                      } ${getTier(comparisonResult.meta_position, 0).color}`}
                    >
                      <TrophyIcon className="h-4 w-4 mr-1" />
                      #{comparisonResult.meta_position} in Meta
                    </span>
                  </div>
                )}

                {/* Matchup Breakdown */}
                {Object.keys(comparisonResult.matchup_analysis).length > 0 && (
                  <div>
                    <p className="font-medium text-gray-700 mb-2">Matchup Breakdown</p>
                    <div className="space-y-1 max-h-48 overflow-y-auto">
                      {Object.entries(comparisonResult.matchup_analysis)
                        .sort((a, b) => (b[1] as any).win_rate - (a[1] as any).win_rate)
                        .map(([opponent, data]) => {
                          const wr = (data as any).win_rate;
                          return (
                            <div
                              key={opponent}
                              className="flex justify-between items-center text-sm py-1"
                            >
                              <span className="text-gray-600 truncate flex-1">{opponent}</span>
                              <span className={`font-medium ml-2 ${getWinRateColor(wr)}`}>
                                {wr.toFixed(0)}%
                              </span>
                            </div>
                          );
                        })}
                    </div>
                  </div>
                )}

                {/* Strengths */}
                {comparisonResult.strengths.length > 0 && (
                  <div>
                    <p className="font-medium text-green-700 mb-2 flex items-center">
                      <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                      Strengths
                    </p>
                    <ul className="space-y-1">
                      {comparisonResult.strengths.map((s, i) => (
                        <li key={i} className="text-sm text-gray-600 flex items-start">
                          <span className="text-green-500 mr-2">+</span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Weaknesses */}
                {comparisonResult.weaknesses.length > 0 && (
                  <div>
                    <p className="font-medium text-red-700 mb-2 flex items-center">
                      <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                      Weaknesses
                    </p>
                    <ul className="space-y-1">
                      {comparisonResult.weaknesses.map((w, i) => (
                        <li key={i} className="text-sm text-gray-600 flex items-start">
                          <span className="text-red-500 mr-2">-</span>
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Suggestions */}
                {comparisonResult.suggestions.length > 0 && (
                  <div>
                    <p className="font-medium text-pokemon-blue mb-2 flex items-center">
                      <SparklesIcon className="h-4 w-4 mr-1" />
                      Suggestions
                    </p>
                    <ul className="space-y-1">
                      {comparisonResult.suggestions.map((s, i) => (
                        <li key={i} className="text-sm text-gray-600 flex items-start">
                          <span className="text-pokemon-blue mr-2">{i + 1}.</span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Quick Stats */}
          {topDecks.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
              </CardHeader>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-500">Top 3 Meta Share</dt>
                  <dd className="font-medium text-gray-900">
                    {topDecks
                      .slice(0, 3)
                      .reduce((sum, d) => sum + d.meta_share, 0)
                      .toFixed(1)}
                    %
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Highest Win Rate</dt>
                  <dd className="font-medium text-green-600">
                    {Math.max(...topDecks.filter((d) => d.win_rate).map((d) => d.win_rate || 0)).toFixed(
                      1
                    )}
                    %
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Most Played</dt>
                  <dd className="font-medium text-gray-900 truncate max-w-[150px]">
                    {topDecks[0]?.archetype}
                  </dd>
                </div>
              </dl>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
