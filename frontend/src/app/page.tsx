'use client';

import Link from 'next/link';
import {
  RectangleStackIcon,
  VideoCameraIcon,
  ChartBarIcon,
  FolderArrowDownIcon,
  PlayCircleIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    name: 'Deck Builder',
    description: 'Create and manage your Pokemon TCG decks with our intuitive builder.',
    href: '/decks',
    icon: RectangleStackIcon,
    color: 'bg-blue-500',
  },
  {
    name: 'Card Collection',
    description: 'Browse the complete Pokemon TCG card database and build your collection.',
    href: '/cards',
    icon: SparklesIcon,
    color: 'bg-yellow-500',
  },
  {
    name: 'Video Upload',
    description: 'Upload match videos from your phone and get AI-powered analysis.',
    href: '/videos',
    icon: VideoCameraIcon,
    color: 'bg-red-500',
  },
  {
    name: 'Meta Analysis',
    description: 'Compare your decks against the top 10 meta decks with win rate predictions.',
    href: '/meta',
    icon: ChartBarIcon,
    color: 'bg-purple-500',
  },
  {
    name: 'Match Import',
    description: 'Import match replays from Pokemon TCG Live for step-by-step analysis.',
    href: '/matches',
    icon: FolderArrowDownIcon,
    color: 'bg-green-500',
  },
  {
    name: 'YouTube Channels',
    description: 'Curate your favorite Pokemon TCG content creators.',
    href: '/youtube',
    icon: PlayCircleIcon,
    color: 'bg-pink-500',
  },
];

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          Pokemon TCG
          <span className="text-pokemon-red"> Analysis Platform</span>
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600 max-w-2xl mx-auto">
          Build decks, analyze matches, track the meta, and improve your game with AI-powered insights.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => (
          <Link
            key={feature.name}
            href={feature.href}
            className="group relative bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow"
          >
            <div className={`inline-flex p-3 rounded-lg ${feature.color}`}>
              <feature.icon className="h-6 w-6 text-white" aria-hidden="true" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-gray-900 group-hover:text-pokemon-blue">
              {feature.name}
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              {feature.description}
            </p>
          </Link>
        ))}
      </div>

      {/* Quick Stats */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Start</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-pokemon-blue">1</p>
            <p className="text-sm text-gray-600 mt-2">Import your card collection</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-pokemon-red">2</p>
            <p className="text-sm text-gray-600 mt-2">Build or import a deck</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-pokemon-gold">3</p>
            <p className="text-sm text-gray-600 mt-2">Analyze against the meta</p>
          </div>
        </div>
      </div>
    </div>
  );
}
