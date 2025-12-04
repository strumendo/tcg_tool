'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  RectangleStackIcon,
  VideoCameraIcon,
  ChartBarIcon,
  FolderArrowDownIcon,
  PlayCircleIcon,
  SparklesIcon,
  TrophyIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  FireIcon,
} from '@heroicons/react/24/outline';
import {
  getDashboardStats,
  getRecentActivity,
  getMatchupSummary,
  getTopDecks,
} from '@/lib/api';

const quickLinks = [
  { name: 'Decks', href: '/decks', icon: RectangleStackIcon, color: 'bg-blue-500' },
  { name: 'Cards', href: '/cards', icon: SparklesIcon, color: 'bg-yellow-500' },
  { name: 'Videos', href: '/videos', icon: VideoCameraIcon, color: 'bg-red-500' },
  { name: 'Meta', href: '/meta', icon: ChartBarIcon, color: 'bg-purple-500' },
  { name: 'Matches', href: '/matches', icon: FolderArrowDownIcon, color: 'bg-green-500' },
  { name: 'Channels', href: '/channels', icon: PlayCircleIcon, color: 'bg-pink-500' },
];

export default function DashboardPage() {
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => getDashboardStats(),
  });

  const { data: activityData } = useQuery({
    queryKey: ['dashboard-activity'],
    queryFn: () => getRecentActivity(8),
  });

  const { data: matchupData } = useQuery({
    queryKey: ['dashboard-matchups'],
    queryFn: () => getMatchupSummary(undefined, 30),
  });

  const { data: topDecksData } = useQuery({
    queryKey: ['dashboard-top-decks'],
    queryFn: () => getTopDecks(5),
  });

  const stats = statsData?.data || null;
  const activities = activityData?.data?.activities || [];
  const matchups = matchupData?.data?.matchups || [];
  const topDecks = topDecksData?.data?.decks || [];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'match':
        return <TrophyIcon className="h-5 w-5 text-green-500" />;
      case 'deck':
        return <RectangleStackIcon className="h-5 w-5 text-blue-500" />;
      case 'video':
        return <VideoCameraIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome to your Pokemon TCG Analysis Platform</p>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
        {quickLinks.map((link) => (
          <Link
            key={link.name}
            href={link.href}
            className="flex flex-col items-center p-4 bg-white rounded-xl border border-gray-200 hover:shadow-md transition-shadow"
          >
            <div className={`p-2 rounded-lg ${link.color}`}>
              <link.icon className="h-5 w-5 text-white" />
            </div>
            <span className="mt-2 text-sm font-medium text-gray-700">{link.name}</span>
          </Link>
        ))}
      </div>

      {/* Stats Overview */}
      {statsLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <div className="h-16 bg-gray-200 rounded"></div>
            </Card>
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <RectangleStackIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.decks.total}</p>
                <p className="text-sm text-gray-500">Decks ({stats.decks.active} active)</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <TrophyIcon className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.matches.total}</p>
                <p className="text-sm text-gray-500">
                  Matches ({stats.matches.win_rate}% WR)
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-red-100 rounded-lg">
                <VideoCameraIcon className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.videos.total}</p>
                <p className="text-sm text-gray-500">
                  Videos ({stats.videos.analyzed} analyzed)
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <SparklesIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.cards.total}</p>
                <p className="text-sm text-gray-500">Cards ({stats.cards.sets} sets)</p>
              </div>
            </div>
          </Card>
        </div>
      ) : null}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClockIcon className="h-5 w-5" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          {activities.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No recent activity</p>
          ) : (
            <div className="space-y-3">
              {activities.map((activity: any, i: number) => (
                <Link
                  key={i}
                  href={activity.link}
                  className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {getActivityIcon(activity.type)}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{activity.title}</p>
                    <p className="text-sm text-gray-500 truncate">{activity.subtitle}</p>
                  </div>
                  <span className="text-xs text-gray-400 whitespace-nowrap">
                    {formatTimeAgo(activity.timestamp)}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </Card>

        {/* Top Decks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FireIcon className="h-5 w-5" />
              Top Performing Decks
            </CardTitle>
          </CardHeader>
          {topDecks.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No deck data yet</p>
          ) : (
            <div className="space-y-3">
              {topDecks.map((deck: any, i: number) => (
                <Link
                  key={deck.id}
                  href={`/decks/${deck.id}`}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      i === 0
                        ? 'bg-yellow-100 text-yellow-700'
                        : i === 1
                        ? 'bg-gray-100 text-gray-700'
                        : i === 2
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-gray-50 text-gray-500'
                    }`}
                  >
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{deck.name}</p>
                    <p className="text-xs text-gray-500">
                      {deck.matches_played} matches played
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-sm font-medium ${
                      deck.win_rate >= 60
                        ? 'bg-green-100 text-green-700'
                        : deck.win_rate >= 50
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {deck.win_rate}%
                  </span>
                </Link>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Matchup Summary */}
      {matchups.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ArrowTrendingUpIcon className="h-5 w-5" />
              Matchup Summary (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 border-b">
                  <th className="pb-3 font-medium">Opponent Archetype</th>
                  <th className="pb-3 font-medium text-center">Games</th>
                  <th className="pb-3 font-medium text-center">Wins</th>
                  <th className="pb-3 font-medium text-center">Losses</th>
                  <th className="pb-3 font-medium text-center">Win Rate</th>
                </tr>
              </thead>
              <tbody>
                {matchups.slice(0, 8).map((matchup: any) => (
                  <tr key={matchup.archetype} className="border-b border-gray-100">
                    <td className="py-3 font-medium">{matchup.archetype}</td>
                    <td className="py-3 text-center text-gray-600">{matchup.total}</td>
                    <td className="py-3 text-center text-green-600">{matchup.wins}</td>
                    <td className="py-3 text-center text-red-600">{matchup.losses}</td>
                    <td className="py-3 text-center">
                      <span
                        className={`px-2 py-1 rounded text-sm font-medium ${
                          matchup.win_rate >= 50
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {matchup.win_rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {matchups.length > 8 && (
            <div className="mt-4 text-center">
              <Link href="/matches" className="text-pokemon-blue hover:underline text-sm">
                View all matchups →
              </Link>
            </div>
          )}
        </Card>
      )}

      {/* Empty State for New Users */}
      {stats && stats.matches.total === 0 && stats.decks.total === 0 && (
        <Card className="text-center py-12">
          <SparklesIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Get Started</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Create your first deck, import some matches, or browse the card database to get
            started with your Pokemon TCG analysis journey.
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href="/decks"
              className="px-4 py-2 bg-pokemon-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Deck
            </Link>
            <Link
              href="/cards"
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Browse Cards
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
}
