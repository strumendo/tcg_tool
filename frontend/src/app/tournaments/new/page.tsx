'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { createTournament, getDecks } from '@/lib/api';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Link from 'next/link';

const FORMATS = [
  { value: 'standard', label: 'Standard' },
  { value: 'expanded', label: 'Expanded' },
  { value: 'unlimited', label: 'Unlimited' },
  { value: 'glc', label: 'Gym Leader Challenge' },
  { value: 'other', label: 'Other' },
];

const TOURNAMENT_TYPES = [
  { value: 'local', label: 'Local Event' },
  { value: 'league_cup', label: 'League Cup' },
  { value: 'league_challenge', label: 'League Challenge' },
  { value: 'regional', label: 'Regional Championship' },
  { value: 'international', label: 'International Championship' },
  { value: 'world', label: 'World Championship' },
  { value: 'online', label: 'Online Tournament' },
  { value: 'casual', label: 'Casual/Friendly' },
];

interface Deck {
  id: number;
  name: string;
  archetype?: string;
}

export default function NewTournamentPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [decks, setDecks] = useState<Deck[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    format: 'standard',
    tournament_type: 'local',
    event_date: new Date().toISOString().split('T')[0],
    location: '',
    organizer: '',
    total_rounds: 0,
    total_players: undefined as number | undefined,
    entry_fee: undefined as number | undefined,
    deck_id: undefined as number | undefined,
    deck_archetype: '',
    notes: '',
  });

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadDecks();
    }
  }, [isAuthenticated]);

  const loadDecks = async () => {
    try {
      const res = await getDecks({ page_size: 100 });
      setDecks(res.data.decks || res.data);
    } catch {
      // Ignore error if decks endpoint not available
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast.error('Tournament name is required');
      return;
    }

    setIsSaving(true);
    try {
      const res = await createTournament({
        ...formData,
        total_players: formData.total_players || undefined,
        entry_fee: formData.entry_fee || undefined,
        deck_id: formData.deck_id || undefined,
      });
      toast.success('Tournament created!');
      router.push(`/tournaments/${res.data.id}`);
    } catch (err) {
      toast.error('Failed to create tournament');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeckChange = (deckId: number | undefined) => {
    setFormData((prev) => ({
      ...prev,
      deck_id: deckId,
      deck_archetype: deckId
        ? decks.find((d) => d.id === deckId)?.archetype || ''
        : prev.deck_archetype,
    }));
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/tournaments">
          <Button variant="ghost" size="sm">
            <ArrowLeftIcon className="h-5 w-5" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">New Tournament</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Tournament Details</CardTitle>
          </CardHeader>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tournament Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                placeholder="e.g., League Cup at Local Game Store"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Format</label>
                <select
                  value={formData.format}
                  onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                >
                  {FORMATS.map((f) => (
                    <option key={f.value} value={f.value}>
                      {f.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tournament Type
                </label>
                <select
                  value={formData.tournament_type}
                  onChange={(e) => setFormData({ ...formData, tournament_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                >
                  {TOURNAMENT_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Event Date *
                </label>
                <input
                  type="date"
                  value={formData.event_date}
                  onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                  placeholder="City or venue name"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Organizer</label>
              <input
                type="text"
                value={formData.organizer}
                onChange={(e) => setFormData({ ...formData, organizer: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                placeholder="Tournament organizer or store name"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected Rounds
                </label>
                <input
                  type="number"
                  value={formData.total_rounds || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, total_rounds: Number(e.target.value) || 0 })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                  min="0"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Players</label>
                <input
                  type="number"
                  value={formData.total_players || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      total_players: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                  min="0"
                  placeholder="?"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Entry Fee</label>
                <input
                  type="number"
                  value={formData.entry_fee || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      entry_fee: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                  min="0"
                  step="0.01"
                  placeholder="$"
                />
              </div>
            </div>

            <div className="border-t pt-4 mt-4">
              <h3 className="font-medium text-gray-900 mb-3">Deck Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select Deck
                  </label>
                  <select
                    value={formData.deck_id || ''}
                    onChange={(e) =>
                      handleDeckChange(e.target.value ? Number(e.target.value) : undefined)
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
                    Deck Archetype
                  </label>
                  <input
                    type="text"
                    value={formData.deck_archetype}
                    onChange={(e) => setFormData({ ...formData, deck_archetype: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                    placeholder="e.g., Charizard ex"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue resize-none"
                placeholder="Any additional notes about the tournament..."
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Link href="/tournaments">
                <Button variant="secondary" type="button">
                  Cancel
                </Button>
              </Link>
              <Button type="submit" loading={isSaving}>
                Create Tournament
              </Button>
            </div>
          </div>
        </Card>
      </form>
    </div>
  );
}
