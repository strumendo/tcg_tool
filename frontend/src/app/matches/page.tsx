'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import {
  getMatches,
  getDecks,
  createMatch,
  deleteMatch,
  importMatchFromScreenshot,
  importMatchFromText,
  getMatchStats,
} from '@/lib/api';
import { Match, Deck } from '@/types';
import {
  TrophyIcon,
  XCircleIcon,
  MinusCircleIcon,
  PlusIcon,
  TrashIcon,
  DocumentArrowUpIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClockIcon,
  UserIcon,
  ArrowPathIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const RESULT_OPTIONS = [
  { value: '', label: 'All Results' },
  { value: 'win', label: 'Wins' },
  { value: 'loss', label: 'Losses' },
  { value: 'draw', label: 'Draws' },
];

const COMMON_ARCHETYPES = [
  'Charizard ex',
  'Lugia VSTAR',
  'Gardevoir ex',
  'Miraidon ex',
  'Chien-Pao ex',
  'Lost Zone Box',
  'Giratina VSTAR',
  'Snorlax Stall',
  'Roaring Moon ex',
  'Gholdengo ex',
  'Raging Bolt ex',
  'Dragapult ex',
  'Other',
];

export default function MatchesPage() {
  const [showAddForm, setShowAddForm] = useState(false);
  const [showImportForm, setShowImportForm] = useState(false);
  const [importMode, setImportMode] = useState<'screenshot' | 'text'>('screenshot');
  const [filterResult, setFilterResult] = useState('');
  const [filterDeckId, setFilterDeckId] = useState<number | null>(null);

  // Form state for manual match creation
  const [newMatch, setNewMatch] = useState({
    opponent_deck_archetype: '',
    result: 'win' as 'win' | 'loss' | 'draw',
    player_prizes_taken: 6,
    opponent_prizes_taken: 0,
    went_first: true,
    deck_id: null as number | null,
  });

  // Import state
  const [importText, setImportText] = useState('');
  const [importDeckId, setImportDeckId] = useState<number | null>(null);

  const queryClient = useQueryClient();

  // Fetch matches
  const { data: matchesData, isLoading: matchesLoading } = useQuery({
    queryKey: ['matches', filterResult, filterDeckId],
    queryFn: () =>
      getMatches({
        result: filterResult || undefined,
        deck_id: filterDeckId || undefined,
      }),
  });

  // Fetch decks for dropdown
  const { data: decksData } = useQuery({
    queryKey: ['decks'],
    queryFn: () => getDecks(),
  });

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ['match-stats', filterDeckId],
    queryFn: () => getMatchStats(filterDeckId || undefined),
  });

  const matches: Match[] = matchesData?.data?.matches || [];
  const decks: Deck[] = decksData?.data?.decks || [];
  const stats = statsData?.data || null;

  // Create match mutation
  const createMutation = useMutation({
    mutationFn: () => createMatch(newMatch),
    onSuccess: () => {
      toast.success('Match recorded!');
      queryClient.invalidateQueries({ queryKey: ['matches'] });
      queryClient.invalidateQueries({ queryKey: ['match-stats'] });
      setShowAddForm(false);
      setNewMatch({
        opponent_deck_archetype: '',
        result: 'win',
        player_prizes_taken: 6,
        opponent_prizes_taken: 0,
        went_first: true,
        deck_id: null,
      });
    },
    onError: () => toast.error('Failed to create match'),
  });

  // Delete match mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteMatch(id),
    onSuccess: () => {
      toast.success('Match deleted');
      queryClient.invalidateQueries({ queryKey: ['matches'] });
      queryClient.invalidateQueries({ queryKey: ['match-stats'] });
    },
  });

  // Import from screenshot mutation
  const importScreenshotMutation = useMutation({
    mutationFn: (file: File) => importMatchFromScreenshot(file, importDeckId || undefined),
    onSuccess: () => {
      toast.success('Match imported from screenshot!');
      queryClient.invalidateQueries({ queryKey: ['matches'] });
      queryClient.invalidateQueries({ queryKey: ['match-stats'] });
      setShowImportForm(false);
      setImportDeckId(null);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to import match');
    },
  });

  // Import from text mutation
  const importTextMutation = useMutation({
    mutationFn: () => {
      if (!importText.trim()) throw new Error('No text provided');
      return importMatchFromText(importText, importDeckId || undefined);
    },
    onSuccess: () => {
      toast.success('Match imported from text!');
      queryClient.invalidateQueries({ queryKey: ['matches'] });
      queryClient.invalidateQueries({ queryKey: ['match-stats'] });
      setShowImportForm(false);
      setImportText('');
      setImportDeckId(null);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to import match');
    },
  });

  const getResultIcon = (result?: string) => {
    switch (result) {
      case 'win':
        return <TrophyIcon className="h-5 w-5 text-green-500" />;
      case 'loss':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'draw':
        return <MinusCircleIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <MinusCircleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getResultColor = (result?: string) => {
    switch (result) {
      case 'win':
        return 'bg-green-50 border-green-200 text-green-700';
      case 'loss':
        return 'bg-red-50 border-red-200 text-red-700';
      case 'draw':
        return 'bg-yellow-50 border-yellow-200 text-yellow-700';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700';
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '--';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Match History</h1>
          <p className="text-gray-600 mt-1">
            Track and analyze your Pokemon TCG Live matches
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setShowImportForm(!showImportForm)}>
            <DocumentArrowUpIcon className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button onClick={() => setShowAddForm(!showAddForm)}>
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Match
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card className="text-center">
            <div className="text-3xl font-bold text-gray-900">{stats.total_matches}</div>
            <div className="text-sm text-gray-500">Total Matches</div>
          </Card>
          <Card className="text-center">
            <div className="text-3xl font-bold text-green-600">{stats.wins}</div>
            <div className="text-sm text-gray-500">Wins</div>
          </Card>
          <Card className="text-center">
            <div className="text-3xl font-bold text-red-600">{stats.losses}</div>
            <div className="text-sm text-gray-500">Losses</div>
          </Card>
          <Card className="text-center">
            <div className="text-3xl font-bold text-yellow-600">{stats.draws}</div>
            <div className="text-sm text-gray-500">Draws</div>
          </Card>
          <Card className="text-center">
            <div className="text-3xl font-bold text-pokemon-blue">{stats.win_rate}%</div>
            <div className="text-sm text-gray-500">Win Rate</div>
          </Card>
        </div>
      )}

      {/* Import Form */}
      {showImportForm && (
        <Card>
          <CardHeader>
            <CardTitle>Import Match</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            {/* Import Mode Tabs */}
            <div className="flex gap-2 border-b pb-4">
              <button
                onClick={() => setImportMode('screenshot')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  importMode === 'screenshot'
                    ? 'bg-pokemon-blue text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <DocumentArrowUpIcon className="h-4 w-4 inline mr-2" />
                From Screenshot
              </button>
              <button
                onClick={() => setImportMode('text')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  importMode === 'text'
                    ? 'bg-pokemon-blue text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <DocumentTextIcon className="h-4 w-4 inline mr-2" />
                From Text
              </button>
            </div>

            {/* Deck Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Link to Deck (optional)
              </label>
              <select
                value={importDeckId || ''}
                onChange={(e) => setImportDeckId(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              >
                <option value="">No deck selected</option>
                {decks.map((deck) => (
                  <option key={deck.id} value={deck.id}>
                    {deck.name}
                  </option>
                ))}
              </select>
            </div>

            {importMode === 'screenshot' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Screenshot File
                </label>
                <FileUpload
                  onUpload={(files) => importScreenshotMutation.mutate(files[0])}
                  accept={{
                    'image/*': ['.png', '.jpg', '.jpeg'],
                  }}
                  label="Upload screenshot"
                  hint="Take a screenshot of your match summary in Pokemon TCG Live"
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Match Log Text
                </label>
                <textarea
                  value={importText}
                  onChange={(e) => setImportText(e.target.value)}
                  rows={6}
                  placeholder="Paste match log or game history text here..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue resize-none font-mono text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Paste the match log from Pokemon TCG Live
                </p>
                <div className="flex gap-2 justify-end mt-4">
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setShowImportForm(false);
                      setImportText('');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => importTextMutation.mutate()}
                    loading={importTextMutation.isPending}
                    disabled={!importText.trim()}
                  >
                    Import Match
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Add Match Form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>Record Match</CardTitle>
          </CardHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Opponent Deck
              </label>
              <select
                value={newMatch.opponent_deck_archetype}
                onChange={(e) =>
                  setNewMatch({ ...newMatch, opponent_deck_archetype: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              >
                <option value="">Select archetype...</option>
                {COMMON_ARCHETYPES.map((arch) => (
                  <option key={arch} value={arch}>
                    {arch}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Result</label>
              <div className="flex gap-2">
                {(['win', 'loss', 'draw'] as const).map((r) => (
                  <button
                    key={r}
                    onClick={() => setNewMatch({ ...newMatch, result: r })}
                    className={`flex-1 py-2 px-4 rounded-lg border-2 font-medium transition-colors ${
                      newMatch.result === r
                        ? r === 'win'
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : r === 'loss'
                          ? 'border-red-500 bg-red-50 text-red-700'
                          : 'border-yellow-500 bg-yellow-50 text-yellow-700'
                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    {r.charAt(0).toUpperCase() + r.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Prizes Taken
              </label>
              <input
                type="number"
                min="0"
                max="6"
                value={newMatch.player_prizes_taken}
                onChange={(e) =>
                  setNewMatch({ ...newMatch, player_prizes_taken: Number(e.target.value) })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Opponent Prizes Taken
              </label>
              <input
                type="number"
                min="0"
                max="6"
                value={newMatch.opponent_prizes_taken}
                onChange={(e) =>
                  setNewMatch({ ...newMatch, opponent_prizes_taken: Number(e.target.value) })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Your Deck</label>
              <select
                value={newMatch.deck_id || ''}
                onChange={(e) =>
                  setNewMatch({
                    ...newMatch,
                    deck_id: e.target.value ? Number(e.target.value) : null,
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              >
                <option value="">No deck selected</option>
                {decks.map((deck) => (
                  <option key={deck.id} value={deck.id}>
                    {deck.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Who went first?
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setNewMatch({ ...newMatch, went_first: true })}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 font-medium transition-colors ${
                    newMatch.went_first
                      ? 'border-pokemon-blue bg-blue-50 text-pokemon-blue'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                  }`}
                >
                  Me
                </button>
                <button
                  onClick={() => setNewMatch({ ...newMatch, went_first: false })}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 font-medium transition-colors ${
                    !newMatch.went_first
                      ? 'border-pokemon-blue bg-blue-50 text-pokemon-blue'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                  }`}
                >
                  Opponent
                </button>
              </div>
            </div>
          </div>

          <div className="flex gap-2 justify-end mt-6">
            <Button
              variant="secondary"
              onClick={() => {
                setShowAddForm(false);
                setNewMatch({
                  opponent_deck_archetype: '',
                  result: 'win',
                  player_prizes_taken: 6,
                  opponent_prizes_taken: 0,
                  went_first: true,
                  deck_id: null,
                });
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={() => createMutation.mutate()}
              loading={createMutation.isPending}
              disabled={!newMatch.opponent_deck_archetype}
            >
              Save Match
            </Button>
          </div>
        </Card>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <select
            value={filterResult}
            onChange={(e) => setFilterResult(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue text-sm"
          >
            {RESULT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        <select
          value={filterDeckId || ''}
          onChange={(e) => setFilterDeckId(e.target.value ? Number(e.target.value) : null)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue text-sm"
        >
          <option value="">All Decks</option>
          {decks.map((deck) => (
            <option key={deck.id} value={deck.id}>
              {deck.name}
            </option>
          ))}
        </select>
        <span className="text-sm text-gray-500 ml-auto">{matches.length} matches</span>
      </div>

      {/* Archetype Breakdown */}
      {stats && stats.archetype_breakdown && Object.keys(stats.archetype_breakdown).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ChartBarIcon className="h-5 w-5" />
              Matchup Breakdown
            </CardTitle>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 border-b">
                  <th className="pb-2 font-medium">Archetype</th>
                  <th className="pb-2 font-medium text-center">Games</th>
                  <th className="pb-2 font-medium text-center">Wins</th>
                  <th className="pb-2 font-medium text-center">Losses</th>
                  <th className="pb-2 font-medium text-center">Win Rate</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats.archetype_breakdown)
                  .sort(([, a]: any, [, b]: any) => b.total - a.total)
                  .map(([archetype, data]: [string, any]) => (
                    <tr key={archetype} className="border-b border-gray-100">
                      <td className="py-3 font-medium">{archetype}</td>
                      <td className="py-3 text-center text-gray-600">{data.total}</td>
                      <td className="py-3 text-center text-green-600">{data.wins}</td>
                      <td className="py-3 text-center text-red-600">{data.losses}</td>
                      <td className="py-3 text-center">
                        <span
                          className={`px-2 py-1 rounded text-sm font-medium ${
                            data.total > 0 && data.wins / data.total >= 0.5
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {data.total > 0 ? Math.round((data.wins / data.total) * 100) : 0}%
                        </span>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Match List */}
      {matchesLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : matches.length === 0 ? (
        <Card className="text-center py-12">
          <TrophyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">No matches recorded yet</p>
          <p className="text-sm text-gray-500">
            Start tracking your matches to see stats and improve your game
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {matches.map((match) => (
            <Card
              key={match.id}
              padding="none"
              className={`overflow-hidden border-l-4 ${
                match.result === 'win'
                  ? 'border-l-green-500'
                  : match.result === 'loss'
                  ? 'border-l-red-500'
                  : 'border-l-yellow-500'
              }`}
            >
              <div className="p-4 flex items-center gap-4">
                {/* Result Icon */}
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center ${getResultColor(
                    match.result
                  )}`}
                >
                  {getResultIcon(match.result)}
                </div>

                {/* Match Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900">
                      vs {match.opponent_deck_archetype || 'Unknown'}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${getResultColor(
                        match.result
                      )}`}
                    >
                      {match.result || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-sm text-gray-500">
                    <span className="flex items-center">
                      <TrophyIcon className="h-4 w-4 mr-1" />
                      Prizes: {match.player_prizes_taken} - {match.opponent_prizes_taken}
                    </span>
                    {match.total_turns && (
                      <span className="flex items-center">
                        <ArrowPathIcon className="h-4 w-4 mr-1" />
                        {match.total_turns} turns
                      </span>
                    )}
                    {match.went_first !== null && match.went_first !== undefined && (
                      <span className="flex items-center">
                        <UserIcon className="h-4 w-4 mr-1" />
                        {match.went_first ? 'Went first' : 'Went second'}
                      </span>
                    )}
                    <span className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {formatDate(match.match_date || match.created_at)}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <button
                  onClick={() => {
                    if (confirm('Delete this match?')) {
                      deleteMutation.mutate(match.id);
                    }
                  }}
                  className="p-2 text-gray-400 hover:text-red-500 rounded"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
