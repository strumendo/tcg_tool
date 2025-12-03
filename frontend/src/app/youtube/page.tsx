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
} from '@/lib/api';
import { YouTubeChannel } from '@/types';
import { StarIcon, TrashIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';

export default function YouTubePage() {
  const [showAdd, setShowAdd] = useState(false);
  const [channelUrl, setChannelUrl] = useState('');
  const [category, setCategory] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['youtube-channels'],
    queryFn: () => getYouTubeChannels(),
  });

  const addMutation = useMutation({
    mutationFn: () => addYouTubeChannelFromUrl(channelUrl, category || undefined),
    onSuccess: () => {
      toast.success('Channel added!');
      queryClient.invalidateQueries({ queryKey: ['youtube-channels'] });
      setShowAdd(false);
      setChannelUrl('');
      setCategory('');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to add channel');
    },
  });

  const favoriteMutation = useMutation({
    mutationFn: (id: number) => toggleChannelFavorite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['youtube-channels'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteYouTubeChannel(id),
    onSuccess: () => {
      toast.success('Channel removed');
      queryClient.invalidateQueries({ queryKey: ['youtube-channels'] });
    },
  });

  const channels: YouTubeChannel[] = data?.data?.channels || [];

  const formatSubscribers = (count?: number) => {
    if (!count) return '--';
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  const categories = ['competitive', 'casual', 'news', 'deck-tech', 'pulls'];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">YouTube Channels</h1>
          <p className="text-gray-600 mt-1">Your favorite Pokemon TCG content creators</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)}>
          Add Channel
        </Button>
      </div>

      {showAdd && (
        <Card>
          <CardHeader>
            <CardTitle>Add YouTube Channel</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Channel URL
              </label>
              <input
                type="text"
                value={channelUrl}
                onChange={(e) => setChannelUrl(e.target.value)}
                placeholder="https://www.youtube.com/@channel or /channel/UC..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category (optional)
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              >
                <option value="">Select category...</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="secondary" onClick={() => setShowAdd(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => addMutation.mutate()}
                loading={addMutation.isPending}
                disabled={!channelUrl}
              >
                Add Channel
              </Button>
            </div>
          </div>
        </Card>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : channels.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-gray-600">No channels yet. Add your favorite Pokemon TCG YouTubers!</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {channels.map((channel) => (
            <Card key={channel.id} className="flex flex-col">
              <div className="flex items-start gap-4 mb-4">
                {channel.thumbnail_url ? (
                  <img
                    src={channel.thumbnail_url}
                    alt={channel.name}
                    className="w-16 h-16 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-2xl text-gray-400">
                      {channel.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">{channel.name}</h3>
                  {channel.category && (
                    <span className="inline-block px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600 mt-1">
                      {channel.category}
                    </span>
                  )}
                  <p className="text-sm text-gray-500 mt-1">
                    {formatSubscribers(channel.subscriber_count)} subscribers
                  </p>
                </div>
              </div>

              {channel.description && (
                <p className="text-sm text-gray-600 line-clamp-2 mb-4 flex-1">
                  {channel.description}
                </p>
              )}

              <div className="flex gap-2 mt-auto">
                <a
                  href={channel.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1"
                >
                  <Button variant="secondary" className="w-full">
                    <ArrowTopRightOnSquareIcon className="h-4 w-4 mr-2" />
                    Visit
                  </Button>
                </a>
                <Button
                  variant="ghost"
                  onClick={() => favoriteMutation.mutate(channel.id)}
                  title={channel.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                >
                  {channel.is_favorite ? (
                    <StarSolidIcon className="h-5 w-5 text-yellow-500" />
                  ) : (
                    <StarIcon className="h-5 w-5 text-gray-400" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => deleteMutation.mutate(channel.id)}
                  title="Remove channel"
                >
                  <TrashIcon className="h-5 w-5 text-red-500" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
