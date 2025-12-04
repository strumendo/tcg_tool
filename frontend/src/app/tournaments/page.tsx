'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getTournaments, getTournamentStats } from '@/lib/api';
import {
  TrophyIcon,
  CalendarIcon,
  MapPinIcon,
  PlusIcon,
  ChartBarIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface Tournament {
  id: number;
  name: string;
  format: string;
  tournament_type: string;
  event_date: string;
  location?: string;
  status: string;
  final_standing?: number;
  final_record?: string;
  championship_points: number;
  deck_archetype?: string;
  wins: number;
  losses: number;
  ties: number;
}

interface TournamentStats {
  total_tournaments: number;
  total_championship_points: number;
  best_finish?: number;
  total_wins: number;
  total_losses: number;
  total_ties: number;
  win_rate: number;
}

const TOURNAMENT_TYPES: Record<string, string> = {
  local: 'Local',
  league_cup: 'League Cup',
  league_challenge: 'League Challenge',
  regional: 'Regional',
  international: 'International',
  world: 'Worlds',
  online: 'Online',
  casual: 'Casual',
};

const STATUS_COLORS: Record<string, string> = {
  upcoming: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

export default function TournamentsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [stats, setStats] = useState<TournamentStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState<number | undefined>();
  const [selectedType, setSelectedType] = useState<string>('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated, selectedYear, selectedType]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const params: any = { page: 1, page_size: 50 };
      if (selectedYear) params.year = selectedYear;
      if (selectedType) params.tournament_type = selectedType;

      const [tournamentsRes, statsRes] = await Promise.all([
        getTournaments(params),
        getTournamentStats({ year: selectedYear }),
      ]);

      setTournaments(tournamentsRes.data.tournaments);
      setStats(statsRes.data);
    } catch (err) {
      toast.error('Failed to load tournaments');
    } finally {
      setIsLoading(false);
    }
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  if (authLoading || !isAuthenticated) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Tournament Tracker</h1>
        <Link href="/tournaments/new">
          <Button>
            <PlusIcon className="h-5 w-5 mr-2" />
            New Tournament
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <TrophyIcon className="h-8 w-8 text-yellow-500" />
              <div>
                <p className="text-sm text-gray-500">Tournaments</p>
                <p className="text-xl font-bold">{stats.total_tournaments}</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <ChartBarIcon className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-sm text-gray-500">Win Rate</p>
                <p className="text-xl font-bold">{stats.win_rate}%</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-pokemon-blue flex items-center justify-center text-white font-bold">
                CP
              </div>
              <div>
                <p className="text-sm text-gray-500">Championship Pts</p>
                <p className="text-xl font-bold">{stats.total_championship_points}</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="text-2xl">🏆</div>
              <div>
                <p className="text-sm text-gray-500">Best Finish</p>
                <p className="text-xl font-bold">
                  {stats.best_finish ? `#${stats.best_finish}` : '-'}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <select
            value={selectedYear || ''}
            onChange={(e) => setSelectedYear(e.target.value ? Number(e.target.value) : undefined)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
          >
            <option value="">All Years</option>
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
          >
            <option value="">All Types</option>
            {Object.entries(TOURNAMENT_TYPES).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {/* Tournament List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : tournaments.length === 0 ? (
        <Card className="p-12 text-center">
          <TrophyIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Tournaments Yet</h3>
          <p className="text-gray-500 mb-4">Start tracking your tournament journey!</p>
          <Link href="/tournaments/new">
            <Button>Add Your First Tournament</Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-4">
          {tournaments.map((tournament) => (
            <Link key={tournament.id} href={`/tournaments/${tournament.id}`}>
              <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer">
                <div className="flex justify-between items-start">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-lg">{tournament.name}</h3>
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          STATUS_COLORS[tournament.status] || 'bg-gray-100'
                        }`}
                      >
                        {tournament.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <CalendarIcon className="h-4 w-4" />
                        {new Date(tournament.event_date).toLocaleDateString()}
                      </span>
                      {tournament.location && (
                        <span className="flex items-center gap-1">
                          <MapPinIcon className="h-4 w-4" />
                          {tournament.location}
                        </span>
                      )}
                      <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">
                        {TOURNAMENT_TYPES[tournament.tournament_type] || tournament.tournament_type}
                      </span>
                    </div>
                    {tournament.deck_archetype && (
                      <p className="text-sm text-pokemon-blue">
                        Playing: {tournament.deck_archetype}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    {tournament.status === 'completed' ? (
                      <>
                        {tournament.final_standing && (
                          <p className="text-2xl font-bold text-pokemon-blue">
                            #{tournament.final_standing}
                          </p>
                        )}
                        <p className="text-sm text-gray-600">
                          {tournament.final_record || `${tournament.wins}-${tournament.losses}-${tournament.ties}`}
                        </p>
                        {tournament.championship_points > 0 && (
                          <p className="text-xs text-yellow-600">
                            +{tournament.championship_points} CP
                          </p>
                        )}
                      </>
                    ) : (
                      <p className="text-sm text-gray-500">
                        {tournament.wins}-{tournament.losses}-{tournament.ties}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
