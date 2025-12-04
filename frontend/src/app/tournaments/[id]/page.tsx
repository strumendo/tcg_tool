'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  getTournament,
  updateTournament,
  deleteTournament,
  addTournamentRound,
  deleteTournamentRound,
  completeTournament,
} from '@/lib/api';
import {
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon,
  CheckCircleIcon,
  PencilIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface Round {
  id: number;
  round_number: number;
  is_top_cut: boolean;
  top_cut_round?: string;
  opponent_name?: string;
  opponent_deck?: string;
  opponent_archetype?: string;
  result: string;
  games_won: number;
  games_lost: number;
  notes?: string;
}

interface Tournament {
  id: number;
  name: string;
  format: string;
  tournament_type: string;
  event_date: string;
  location?: string;
  organizer?: string;
  status: string;
  total_rounds: number;
  total_players?: number;
  entry_fee?: number;
  final_standing?: number;
  final_record?: string;
  championship_points: number;
  deck_archetype?: string;
  notes?: string;
  rounds: Round[];
  wins: number;
  losses: number;
  ties: number;
}

const RESULT_OPTIONS = [
  { value: 'win', label: 'Win', color: 'bg-green-100 text-green-800' },
  { value: 'loss', label: 'Loss', color: 'bg-red-100 text-red-800' },
  { value: 'tie', label: 'Tie', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'bye', label: 'Bye', color: 'bg-blue-100 text-blue-800' },
  { value: 'id', label: 'ID', color: 'bg-purple-100 text-purple-800' },
];

const RESULT_COLORS: Record<string, string> = {
  win: 'bg-green-100 text-green-800 border-green-200',
  loss: 'bg-red-100 text-red-800 border-red-200',
  tie: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  bye: 'bg-blue-100 text-blue-800 border-blue-200',
  id: 'bg-purple-100 text-purple-800 border-purple-200',
};

export default function TournamentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddRound, setShowAddRound] = useState(false);
  const [showComplete, setShowComplete] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [newRound, setNewRound] = useState({
    round_number: 1,
    is_top_cut: false,
    top_cut_round: '',
    opponent_name: '',
    opponent_deck: '',
    opponent_archetype: '',
    result: 'win' as 'win' | 'loss' | 'tie' | 'bye' | 'id',
    games_won: 2,
    games_lost: 0,
    notes: '',
  });

  const [completeData, setCompleteData] = useState({
    final_standing: undefined as number | undefined,
    championship_points: 0,
  });

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated && params.id) {
      loadTournament();
    }
  }, [isAuthenticated, params.id]);

  const loadTournament = async () => {
    setIsLoading(true);
    try {
      const res = await getTournament(Number(params.id));
      setTournament(res.data);
      // Set next round number
      const maxRound = Math.max(0, ...res.data.rounds.map((r: Round) => r.round_number));
      setNewRound((prev) => ({ ...prev, round_number: maxRound + 1 }));
    } catch (err) {
      toast.error('Tournament not found');
      router.push('/tournaments');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddRound = async () => {
    if (!tournament) return;

    setIsSaving(true);
    try {
      await addTournamentRound(tournament.id, newRound);
      toast.success('Round added!');
      setShowAddRound(false);
      setNewRound({
        round_number: newRound.round_number + 1,
        is_top_cut: false,
        top_cut_round: '',
        opponent_name: '',
        opponent_deck: '',
        opponent_archetype: '',
        result: 'win',
        games_won: 2,
        games_lost: 0,
        notes: '',
      });
      loadTournament();
    } catch (err) {
      toast.error('Failed to add round');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteRound = async (roundId: number) => {
    if (!tournament || !confirm('Delete this round?')) return;

    try {
      await deleteTournamentRound(tournament.id, roundId);
      toast.success('Round deleted');
      loadTournament();
    } catch (err) {
      toast.error('Failed to delete round');
    }
  };

  const handleComplete = async () => {
    if (!tournament) return;

    setIsSaving(true);
    try {
      await completeTournament(
        tournament.id,
        completeData.final_standing,
        completeData.championship_points
      );
      toast.success('Tournament marked as completed!');
      setShowComplete(false);
      loadTournament();
    } catch (err) {
      toast.error('Failed to complete tournament');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!tournament || !confirm('Delete this tournament? This cannot be undone.')) return;

    try {
      await deleteTournament(tournament.id);
      toast.success('Tournament deleted');
      router.push('/tournaments');
    } catch (err) {
      toast.error('Failed to delete tournament');
    }
  };

  if (authLoading || isLoading || !tournament) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/tournaments">
            <Button variant="ghost" size="sm">
              <ArrowLeftIcon className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{tournament.name}</h1>
            <p className="text-gray-500">
              {new Date(tournament.event_date).toLocaleDateString()} -{' '}
              {tournament.location || 'Location TBD'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {tournament.status !== 'completed' && (
            <Button variant="secondary" onClick={() => setShowComplete(true)}>
              <CheckCircleIcon className="h-5 w-5 mr-1" />
              Complete
            </Button>
          )}
          <Button variant="ghost" onClick={handleDelete}>
            <TrashIcon className="h-5 w-5 text-red-500" />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <p className="text-2xl font-bold text-gray-900">
            {tournament.wins}-{tournament.losses}-{tournament.ties}
          </p>
          <p className="text-sm text-gray-500">Record</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-2xl font-bold text-pokemon-blue">
            {tournament.final_standing ? `#${tournament.final_standing}` : '-'}
          </p>
          <p className="text-sm text-gray-500">Final Standing</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-2xl font-bold text-yellow-600">{tournament.championship_points}</p>
          <p className="text-sm text-gray-500">CP Earned</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-2xl font-bold text-gray-900">{tournament.total_players || '?'}</p>
          <p className="text-sm text-gray-500">Players</p>
        </Card>
      </div>

      {/* Tournament Info */}
      <Card className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Format</p>
            <p className="font-medium capitalize">{tournament.format}</p>
          </div>
          <div>
            <p className="text-gray-500">Type</p>
            <p className="font-medium capitalize">{tournament.tournament_type.replace('_', ' ')}</p>
          </div>
          <div>
            <p className="text-gray-500">Deck</p>
            <p className="font-medium">{tournament.deck_archetype || 'Not specified'}</p>
          </div>
          <div>
            <p className="text-gray-500">Status</p>
            <p className="font-medium capitalize">{tournament.status.replace('_', ' ')}</p>
          </div>
        </div>
      </Card>

      {/* Rounds */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Rounds</CardTitle>
          {tournament.status !== 'completed' && (
            <Button size="sm" onClick={() => setShowAddRound(true)}>
              <PlusIcon className="h-4 w-4 mr-1" />
              Add Round
            </Button>
          )}
        </CardHeader>

        {tournament.rounds.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No rounds recorded yet.</p>
            {tournament.status !== 'completed' && (
              <Button className="mt-4" onClick={() => setShowAddRound(true)}>
                Add First Round
              </Button>
            )}
          </div>
        ) : (
          <div className="divide-y">
            {tournament.rounds.map((round) => (
              <div
                key={round.id}
                className={`p-4 flex items-center justify-between ${RESULT_COLORS[round.result]} border-l-4`}
              >
                <div className="flex items-center gap-4">
                  <div className="text-center min-w-[60px]">
                    <p className="text-xs text-gray-500">
                      {round.is_top_cut ? round.top_cut_round || 'Top Cut' : 'Swiss'}
                    </p>
                    <p className="text-lg font-bold">R{round.round_number}</p>
                  </div>
                  <div>
                    <p className="font-medium">
                      vs {round.opponent_name || 'Unknown'}{' '}
                      {round.opponent_archetype && (
                        <span className="text-gray-600">({round.opponent_archetype})</span>
                      )}
                    </p>
                    <p className="text-sm text-gray-600">
                      {round.result.toUpperCase()} ({round.games_won}-{round.games_lost})
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {round.notes && (
                    <span
                      className="text-xs text-gray-500 max-w-[200px] truncate"
                      title={round.notes}
                    >
                      {round.notes}
                    </span>
                  )}
                  {tournament.status !== 'completed' && (
                    <button
                      onClick={() => handleDeleteRound(round.id)}
                      className="p-1 hover:bg-white/50 rounded"
                    >
                      <TrashIcon className="h-4 w-4 text-gray-400 hover:text-red-500" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Notes */}
      {tournament.notes && (
        <Card className="p-4">
          <h3 className="font-medium text-gray-900 mb-2">Notes</h3>
          <p className="text-gray-600 whitespace-pre-wrap">{tournament.notes}</p>
        </Card>
      )}

      {/* Add Round Modal */}
      {showAddRound && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>Add Round {newRound.round_number}</CardTitle>
            </CardHeader>

            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={newRound.is_top_cut}
                    onChange={(e) => setNewRound({ ...newRound, is_top_cut: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Top Cut Round</span>
                </label>
                {newRound.is_top_cut && (
                  <input
                    type="text"
                    value={newRound.top_cut_round}
                    onChange={(e) => setNewRound({ ...newRound, top_cut_round: e.target.value })}
                    placeholder="e.g., Top 8, Finals"
                    className="px-3 py-1 border rounded text-sm"
                  />
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Opponent Name
                  </label>
                  <input
                    type="text"
                    value={newRound.opponent_name}
                    onChange={(e) => setNewRound({ ...newRound, opponent_name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="Player name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Opponent Archetype
                  </label>
                  <input
                    type="text"
                    value={newRound.opponent_archetype}
                    onChange={(e) =>
                      setNewRound({ ...newRound, opponent_archetype: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="e.g., Lugia VSTAR"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Result</label>
                <div className="flex gap-2">
                  {RESULT_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() =>
                        setNewRound({
                          ...newRound,
                          result: opt.value as any,
                          games_won: opt.value === 'win' ? 2 : opt.value === 'loss' ? 0 : 1,
                          games_lost: opt.value === 'loss' ? 2 : opt.value === 'win' ? 0 : 1,
                        })
                      }
                      className={`px-3 py-2 rounded-lg font-medium ${
                        newRound.result === opt.value
                          ? opt.color + ' ring-2 ring-offset-1 ring-gray-400'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Games Won</label>
                  <input
                    type="number"
                    value={newRound.games_won}
                    onChange={(e) => setNewRound({ ...newRound, games_won: Number(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-lg"
                    min="0"
                    max="3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Games Lost</label>
                  <input
                    type="number"
                    value={newRound.games_lost}
                    onChange={(e) =>
                      setNewRound({ ...newRound, games_lost: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                    min="0"
                    max="3"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={newRound.notes}
                  onChange={(e) => setNewRound({ ...newRound, notes: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border rounded-lg resize-none"
                  placeholder="Key plays, misplays, observations..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={() => setShowAddRound(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddRound} loading={isSaving}>
                  Add Round
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Complete Tournament Modal */}
      {showComplete && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Complete Tournament</CardTitle>
            </CardHeader>

            <div className="space-y-4">
              <p className="text-gray-600">
                Mark this tournament as completed and record your final results.
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Final Standing
                </label>
                <input
                  type="number"
                  value={completeData.final_standing || ''}
                  onChange={(e) =>
                    setCompleteData({
                      ...completeData,
                      final_standing: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg"
                  min="1"
                  placeholder="e.g., 1, 2, 5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Championship Points Earned
                </label>
                <input
                  type="number"
                  value={completeData.championship_points}
                  onChange={(e) =>
                    setCompleteData({
                      ...completeData,
                      championship_points: Number(e.target.value) || 0,
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg"
                  min="0"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={() => setShowComplete(false)}>
                  Cancel
                </Button>
                <Button onClick={handleComplete} loading={isSaving}>
                  Complete Tournament
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
