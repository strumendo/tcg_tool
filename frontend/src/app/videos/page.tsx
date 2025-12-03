'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import { getVideos, uploadVideo, analyzeVideo, deleteVideo } from '@/lib/api';
import { Video } from '@/types';
import { PlayIcon, SparklesIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export default function VideosPage() {
  const [showUpload, setShowUpload] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['videos'],
    queryFn: () => getVideos(),
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile || !uploadTitle) throw new Error('Missing file or title');
      return uploadVideo(selectedFile, uploadTitle);
    },
    onSuccess: () => {
      toast.success('Video uploaded successfully!');
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      setShowUpload(false);
      setSelectedFile(null);
      setUploadTitle('');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to upload video');
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: (id: number) => analyzeVideo(id, 'full'),
    onSuccess: () => {
      toast.success('Video analysis started!');
      queryClient.invalidateQueries({ queryKey: ['videos'] });
    },
    onError: () => {
      toast.error('Failed to start analysis');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteVideo(id),
    onSuccess: () => {
      toast.success('Video deleted');
      queryClient.invalidateQueries({ queryKey: ['videos'] });
    },
  });

  const videos: Video[] = data?.data?.videos || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'analyzing': return 'bg-blue-100 text-blue-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '-- MB';
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Match Videos</h1>
          <p className="text-gray-600 mt-1">Upload and analyze your Pokemon TCG matches</p>
        </div>
        <Button onClick={() => setShowUpload(!showUpload)}>
          Upload Video
        </Button>
      </div>

      {showUpload && (
        <Card>
          <CardHeader>
            <CardTitle>Upload Match Video</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Video Title
              </label>
              <input
                type="text"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                placeholder="e.g., Charizard ex vs Lugia VSTAR"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
              />
            </div>
            <FileUpload
              onUpload={(files) => setSelectedFile(files[0])}
              accept={{
                'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
              }}
              maxSize={500 * 1024 * 1024}
              label={selectedFile ? selectedFile.name : 'Select video file'}
              hint="Max 500MB - MP4, MOV, AVI, MKV, WebM"
            />
            <div className="flex gap-2 justify-end">
              <Button variant="secondary" onClick={() => setShowUpload(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => uploadMutation.mutate()}
                loading={uploadMutation.isPending}
                disabled={!selectedFile || !uploadTitle}
              >
                Upload
              </Button>
            </div>
          </div>
        </Card>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : videos.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-gray-600">No videos yet. Upload your first match video!</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {videos.map((video) => (
            <Card key={video.id} padding="none" className="overflow-hidden">
              {/* Thumbnail */}
              <div className="aspect-video bg-gray-900 relative">
                {video.thumbnail_path ? (
                  <img
                    src={`/api/v1/videos/${video.id}/thumbnail`}
                    alt={video.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <PlayIcon className="h-16 w-16 text-gray-600" />
                  </div>
                )}
                <div className="absolute bottom-2 right-2 bg-black/75 text-white text-xs px-2 py-1 rounded">
                  {formatDuration(video.duration_seconds)}
                </div>
              </div>

              {/* Info */}
              <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900 line-clamp-1">{video.title}</h3>
                  <span className={`px-2 py-0.5 rounded text-xs ${getStatusColor(video.status)}`}>
                    {video.status}
                  </span>
                </div>

                <div className="text-sm text-gray-500 mb-4">
                  <span>{formatFileSize(video.file_size)}</span>
                  {video.resolution && <span className="ml-2">{video.resolution}</span>}
                </div>

                {video.analysis_result && (
                  <div className="mb-4 p-2 bg-green-50 rounded text-sm text-green-800">
                    AI Analysis available
                  </div>
                )}

                <div className="flex gap-2">
                  {video.status === 'ready' && !video.analysis_result && (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => analyzeMutation.mutate(video.id)}
                      loading={analyzeMutation.isPending}
                    >
                      <SparklesIcon className="h-4 w-4 mr-1" />
                      Analyze
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteMutation.mutate(video.id)}
                  >
                    <TrashIcon className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
