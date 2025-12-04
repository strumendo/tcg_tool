'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  getDecks,
  getTournaments,
  getDeckForClipboard,
  getTournamentSummary,
  exportStats,
  getStatsShareData,
} from '@/lib/api';
import {
  ArrowDownTrayIcon,
  DocumentDuplicateIcon,
  ShareIcon,
  ChartBarIcon,
  TrophyIcon,
  RectangleStackIcon,
  ClipboardDocumentIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface Deck {
  id: number;
  name: string;
  archetype?: string;
}

interface Tournament {
  id: number;
  name: string;
  event_date: string;
  status: string;
}

const DECK_FORMATS = [
  { value: 'text', label: 'Plain Text', description: 'Simple text list' },
  { value: 'ptcgo', label: 'PTCGO', description: 'Pokemon TCG Online format' },
  { value: 'limitless', label: 'Limitless', description: 'Limitless TCG format' },
  { value: 'json', label: 'JSON', description: 'Structured data format' },
];

export default function ExportPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [decks, setDecks] = useState<Deck[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [selectedFormat, setSelectedFormat] = useState('text');
  const [deckContent, setDeckContent] = useState<string>('');
  const [copied, setCopied] = useState(false);

  const [selectedTournament, setSelectedTournament] = useState<number | null>(null);
  const [tournamentSummary, setTournamentSummary] = useState<string>('');

  const [statsShare, setStatsShare] = useState<any>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [decksRes, tournamentsRes, statsRes] = await Promise.all([
        getDecks({ page_size: 100 }),
        getTournaments({ page_size: 100 }),
        getStatsShareData(),
      ]);

      setDecks(decksRes.data.decks || decksRes.data || []);
      setTournaments(tournamentsRes.data.tournaments || []);
      setStatsShare(statsRes.data);
    } catch (err) {
      toast.error('Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeckExport = async () => {
    if (!selectedDeck) {
      toast.error('Please select a deck');
      return;
    }

    try {
      const res = await getDeckForClipboard(selectedDeck, selectedFormat as any);
      setDeckContent(res.data.content);
    } catch (err) {
      toast.error('Failed to export deck');
    }
  };

  const handleCopyDeck = async () => {
    if (!deckContent) return;

    try {
      await navigator.clipboard.writeText(deckContent);
      setCopied(true);
      toast.success('Copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleDownloadDeck = () => {
    if (!deckContent || !selectedDeck) return;

    const blob = new Blob([deckContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `deck_${selectedDeck}_${selectedFormat}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleTournamentSummary = async () => {
    if (!selectedTournament) {
      toast.error('Please select a tournament');
      return;
    }

    try {
      const res = await getTournamentSummary(selectedTournament);
      setTournamentSummary(res.data.summary);
    } catch (err) {
      toast.error('Failed to get tournament summary');
    }
  };

  const handleCopyTournament = async () => {
    if (!tournamentSummary) return;

    try {
      await navigator.clipboard.writeText(tournamentSummary);
      toast.success('Copied to clipboard!');
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleCopyStats = async () => {
    if (!statsShare?.share_text) return;

    try {
      await navigator.clipboard.writeText(statsShare.share_text);
      toast.success('Copied to clipboard!');
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleShareTwitter = (text: string, hashtags: string[]) => {
    const encodedText = encodeURIComponent(text);
    const encodedHashtags = encodeURIComponent(hashtags.join(','));
    window.open(
      `https://twitter.com/intent/tweet?text=${encodedText}&hashtags=${encodedHashtags}`,
      '_blank'
    );
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ShareIcon className="h-8 w-8 text-pokemon-blue" />
        <h1 className="text-2xl font-bold text-gray-900">Export & Share</h1>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Deck Export */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RectangleStackIcon className="h-5 w-5" />
                Export Deck
              </CardTitle>
            </CardHeader>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Deck
                </label>
                <select
                  value={selectedDeck || ''}
                  onChange={(e) => {
                    setSelectedDeck(e.target.value ? Number(e.target.value) : null);
                    setDeckContent('');
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                >
                  <option value="">Choose a deck...</option>
                  {decks.map((deck) => (
                    <option key={deck.id} value={deck.id}>
                      {deck.name} {deck.archetype && `(${deck.archetype})`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Export Format
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {DECK_FORMATS.map((format) => (
                    <button
                      key={format.value}
                      onClick={() => {
                        setSelectedFormat(format.value);
                        setDeckContent('');
                      }}
                      className={`p-3 text-left rounded-lg border transition-colors ${
                        selectedFormat === format.value
                          ? 'border-pokemon-blue bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <p className="font-medium text-sm">{format.label}</p>
                      <p className="text-xs text-gray-500">{format.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              <Button onClick={handleDeckExport} disabled={!selectedDeck} className="w-full">
                Generate Export
              </Button>

              {deckContent && (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      onClick={handleCopyDeck}
                      className="flex-1"
                    >
                      {copied ? (
                        <CheckIcon className="h-4 w-4 mr-1" />
                      ) : (
                        <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                      )}
                      {copied ? 'Copied!' : 'Copy'}
                    </Button>
                    <Button variant="secondary" onClick={handleDownloadDeck}>
                      <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                  <pre className="p-3 bg-gray-50 rounded-lg text-xs overflow-auto max-h-64 whitespace-pre-wrap">
                    {deckContent}
                  </pre>
                </div>
              )}
            </div>
          </Card>

          {/* Tournament Export */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrophyIcon className="h-5 w-5" />
                Share Tournament
              </CardTitle>
            </CardHeader>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Tournament
                </label>
                <select
                  value={selectedTournament || ''}
                  onChange={(e) => {
                    setSelectedTournament(e.target.value ? Number(e.target.value) : null);
                    setTournamentSummary('');
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                >
                  <option value="">Choose a tournament...</option>
                  {tournaments.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} ({new Date(t.event_date).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>

              <Button
                onClick={handleTournamentSummary}
                disabled={!selectedTournament}
                className="w-full"
              >
                Generate Summary
              </Button>

              {tournamentSummary && (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      onClick={handleCopyTournament}
                      className="flex-1"
                    >
                      <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                      Copy
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() =>
                        handleShareTwitter(tournamentSummary, ['PokemonTCG', 'Tournament'])
                      }
                    >
                      Share on X
                    </Button>
                  </div>
                  <pre className="p-3 bg-gray-50 rounded-lg text-sm whitespace-pre-wrap">
                    {tournamentSummary}
                  </pre>
                </div>
              )}
            </div>
          </Card>

          {/* Stats Share */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChartBarIcon className="h-5 w-5" />
                Share Your Stats
              </CardTitle>
            </CardHeader>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Stats Preview */}
              {statsShare && (
                <>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg text-white">
                        <p className="text-3xl font-bold">{statsShare.stats?.matches?.win_rate}%</p>
                        <p className="text-sm opacity-80">Win Rate</p>
                      </div>
                      <div className="p-4 bg-gradient-to-br from-green-500 to-green-600 rounded-lg text-white">
                        <p className="text-3xl font-bold">{statsShare.stats?.matches?.total}</p>
                        <p className="text-sm opacity-80">Matches</p>
                      </div>
                      <div className="p-4 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg text-white">
                        <p className="text-3xl font-bold">{statsShare.stats?.tournaments?.total}</p>
                        <p className="text-sm opacity-80">Tournaments</p>
                      </div>
                      <div className="p-4 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg text-white">
                        <p className="text-3xl font-bold">
                          {statsShare.stats?.tournaments?.championship_points || 0}
                        </p>
                        <p className="text-sm opacity-80">Championship Pts</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <pre className="p-4 bg-gray-50 rounded-lg text-sm whitespace-pre-wrap">
                      {statsShare.share_text}
                    </pre>
                    <div className="flex gap-2">
                      <Button variant="secondary" onClick={handleCopyStats} className="flex-1">
                        <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                        Copy
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={() =>
                          handleShareTwitter(statsShare.share_text, statsShare.hashtags)
                        }
                      >
                        Share on X
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </Card>

          {/* Quick Export Links */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ArrowDownTrayIcon className="h-5 w-5" />
                Bulk Downloads
              </CardTitle>
            </CardHeader>

            <div className="grid md:grid-cols-3 gap-4">
              <a
                href="/api/v1/export/matches?format=csv"
                download
                className="p-4 border rounded-lg hover:border-pokemon-blue hover:bg-blue-50 transition-colors"
              >
                <p className="font-medium">Match History (CSV)</p>
                <p className="text-sm text-gray-500">Download all matches as spreadsheet</p>
              </a>
              <a
                href="/api/v1/export/matches?format=json"
                download
                className="p-4 border rounded-lg hover:border-pokemon-blue hover:bg-blue-50 transition-colors"
              >
                <p className="font-medium">Match History (JSON)</p>
                <p className="text-sm text-gray-500">Download all matches as JSON</p>
              </a>
              <a
                href="/api/v1/export/stats"
                download
                className="p-4 border rounded-lg hover:border-pokemon-blue hover:bg-blue-50 transition-colors"
              >
                <p className="font-medium">Complete Stats</p>
                <p className="text-sm text-gray-500">Full statistics summary</p>
              </a>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
