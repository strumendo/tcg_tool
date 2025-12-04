'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  getYouTubeChannels,
  addYouTubeChannelFromUrl,
  toggleChannelFavorite,
  deleteYouTubeChannel,
  updateYouTubeChannel,
} from '@/lib/api';
import { YouTubeChannel } from '@/types';
import {
  PlayCircleIcon,
  StarIcon,
  TrashIcon,
  PlusIcon,
  UserGroupIcon,
  FilmIcon,
  LinkIcon,
  PencilIcon,
  XMarkIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'competitive', label: 'Competitive' },
  { value: 'casual', label: 'Casual' },
  { value: 'news', label: 'News & Updates' },
  { value: 'deckbuilding', label: 'Deck Building' },
  { value: 'tutorials', label: 'Tutorials' },
  { value: 'entertainment', label: 'Entertainment' },
];

export default function ChannelsPage() {
  const [showAddForm, setShowAddForm] = useState(false);
  const [channelUrl, setChannelUrl] = useState('');
  const [channelCategory, setChannelCategory] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [editingChannel, setEditingChannel] = useState<YouTubeChannel | null>(null);
  const [editNotes, setEditNotes] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['youtube-channels', filterCategory, showFavoritesOnly],
    queryFn: () =>
      getYouTubeChannels({
        category: filterCategory || undefined,
        favorites_only: showFavoritesOnly,
      }),
  });

  const addMutation = useMutation({
    mutationFn: () => addYouTubeChannelFromUrl(channelUrl, channelCategory || undefined),
    onSuccess: () => {
      toast.success('Channel added successfully!');
      queryClient.invalidateQueries({ queryKey: ['youtube-channels'] });
      setShowAddForm(false);
      setChannelUrl('');
      setChannelCategory('');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to add channel');
    },
  });

  const favoriteMutation = useMutation({
    mutationFn: (channelId: number) => toggleChannelFavorite(channelId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['youtube-channels'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (channelId: number) => deleteYouTubeChannel(channelId),
    onSuccess: () => {
      toast.success('Channel removed');
      queryClient.invalidateQueries({ queryKey: ['youtube-channels'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => updateYouTubeChannel(id, data),
    onSuccess: () => {
      toast.success('Channel updated');
      queryClient.invalidateQueries({ queryKey: ['youtube-channels'] });
      setEditingChannel(null);
    },
    onError: () => {
      toast.error('Failed to update channel');
    },
  });

  const channels: YouTubeChannel[] = data?.data?.channels || [];

  const formatSubscribers = (count?: number) => {
    if (!count) return '--';
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  const getCategoryColor = (category?: string) => {
    switch (category) {
      case 'competitive':
        return 'bg-red-100 text-red-800';
      case 'casual':
        return 'bg-green-100 text-green-800';
      case 'news':
        return 'bg-blue-100 text-blue-800';
      case 'deckbuilding':
        return 'bg-purple-100 text-purple-800';
      case 'tutorials':
        return 'bg-yellow-100 text-yellow-800';
      case 'entertainment':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const startEditing = (channel: YouTubeChannel) => {
    setEditingChannel(channel);
    setEditNotes(channel.notes || '');
    setEditCategory(channel.category || '');
  };

  const saveEdit = () => {
    if (editingChannel) {
      updateMutation.mutate({
        id: editingChannel.id,
        data: {
          notes: editNotes,
          category: editCategory || null,
        },
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">YouTube Channels</h1>
          <p className="text-gray-600 mt-1">Track your favorite Pokemon TCG content creators</p>
        </div>
        <Button onClick={() => setShowAddForm(!showAddForm)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Channel
        </Button>
      </div>

      {/* Add Channel Form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>Add YouTube Channel</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Channel URL</label>
              <input
                type="text"
                value={channelUrl}
                onChange={(e) => setChannelUrl(e.target.value)}
                placeholder="https://youtube.com/@channelname"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              />
              <p className="text-xs text-gray-500 mt-1">
                Supports youtube.com/@username, youtube.com/c/name, or youtube.com/channel/ID
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category (optional)</label>
              <select
                value={channelCategory}
                onChange={(e) => setChannelCategory(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              >
                <option value="">Select category...</option>
                {CATEGORIES.slice(1).map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 justify-end">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowAddForm(false);
                  setChannelUrl('');
                  setChannelCategory('');
                }}
              >
                Cancel
              </Button>
              <Button onClick={() => addMutation.mutate()} loading={addMutation.isPending} disabled={!channelUrl}>
                Add Channel
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue text-sm"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            showFavoritesOnly
              ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
              : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
          }`}
        >
          {showFavoritesOnly ? (
            <StarSolidIcon className="h-4 w-4 text-yellow-500" />
          ) : (
            <StarIcon className="h-4 w-4" />
          )}
          Favorites Only
        </button>
        <span className="text-sm text-gray-500 ml-auto">{channels.length} channels</span>
      </div>

      {/* Channel Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : channels.length === 0 ? (
        <Card className="text-center py-12">
          <PlayCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">No channels yet</p>
          <p className="text-sm text-gray-500">
            Add your favorite Pokemon TCG YouTube channels to keep track of new content
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {channels.map((channel) => (
            <Card key={channel.id} padding="none" className="overflow-hidden group">
              {/* Channel Header */}
              <div className="p-4">
                <div className="flex gap-4">
                  {/* Thumbnail */}
                  <div className="flex-shrink-0">
                    {channel.thumbnail_url ? (
                      <img
                        src={channel.thumbnail_url}
                        alt={channel.name}
                        className="w-16 h-16 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                        <PlayCircleIcon className="h-8 w-8 text-gray-400" />
                      </div>
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <h3 className="font-semibold text-gray-900 truncate pr-2">{channel.name}</h3>
                      <button
                        onClick={() => favoriteMutation.mutate(channel.id)}
                        className="flex-shrink-0"
                      >
                        {channel.is_favorite ? (
                          <StarSolidIcon className="h-5 w-5 text-yellow-400" />
                        ) : (
                          <StarIcon className="h-5 w-5 text-gray-300 hover:text-yellow-400" />
                        )}
                      </button>
                    </div>

                    {channel.category && (
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-xs mt-1 ${getCategoryColor(
                          channel.category
                        )}`}
                      >
                        {channel.category}
                      </span>
                    )}

                    <div className="flex gap-4 mt-2 text-sm text-gray-500">
                      {channel.subscriber_count && (
                        <span className="flex items-center">
                          <UserGroupIcon className="h-4 w-4 mr-1" />
                          {formatSubscribers(channel.subscriber_count)}
                        </span>
                      )}
                      {channel.video_count && (
                        <span className="flex items-center">
                          <FilmIcon className="h-4 w-4 mr-1" />
                          {channel.video_count} videos
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Description */}
                {channel.description && (
                  <p className="text-sm text-gray-600 mt-3 line-clamp-2">{channel.description}</p>
                )}

                {/* Notes */}
                {channel.notes && (
                  <div className="mt-3 p-2 bg-yellow-50 rounded text-sm text-yellow-800">
                    <strong>Notes:</strong> {channel.notes}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="border-t bg-gray-50 px-4 py-3 flex justify-between items-center">
                <a
                  href={channel.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-pokemon-blue hover:text-blue-700 text-sm font-medium flex items-center"
                >
                  <LinkIcon className="h-4 w-4 mr-1" />
                  Visit Channel
                </a>
                <div className="flex gap-2">
                  <button
                    onClick={() => startEditing(channel)}
                    className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Remove this channel?')) {
                        deleteMutation.mutate(channel.id);
                      }
                    }}
                    className="p-1.5 text-gray-400 hover:text-red-500 rounded"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingChannel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Edit Channel</CardTitle>
                <button onClick={() => setEditingChannel(null)}>
                  <XMarkIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                </button>
              </div>
            </CardHeader>
            <div className="space-y-4">
              <div>
                <p className="font-medium text-gray-900">{editingChannel.name}</p>
                <p className="text-sm text-gray-500">{editingChannel.url}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                >
                  <option value="">No category</option>
                  {CATEGORIES.slice(1).map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  rows={3}
                  placeholder="Add personal notes about this channel..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue resize-none"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button variant="secondary" onClick={() => setEditingChannel(null)}>
                  Cancel
                </Button>
                <Button onClick={saveEdit} loading={updateMutation.isPending}>
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
