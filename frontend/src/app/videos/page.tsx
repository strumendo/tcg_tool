'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import { getVideos, uploadVideoWithProgress, analyzeVideo, deleteVideo, getVideoThumbnailUrl } from '@/lib/api';
import { Video } from '@/types';
import { PlayIcon, SparklesIcon, TrashIcon, EyeIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export default function VideosPage() {
  const router = useRouter();
  const [showUpload, setShowUpload] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['videos'],
    queryFn: () => getVideos(),
  });

  const handleUpload = async () => {
    if (!selectedFile || !uploadTitle) {
      toast.error('Please provide a title and select a file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      await uploadVideoWithProgress(
        selectedFile,
        uploadTitle,
        (progress) => setUploadProgress(progress),
        uploadDescription || undefined
      );
      toast.success('Video uploaded successfully!');
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      setShowUpload(false);
      setSelectedFile(null);
      setUploadTitle('');
      setUploadDescription('');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to upload video');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const analyzeMutation = useMutation({
    mutationFn: (id: number) => analyzeVideo(id, 'full'),
    onSuccess: () => {
      toast.success('Video analysis started!');
      queryClient.invalidateQueries({ queryKey: ['videos'] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to start analysis');
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
                Video Title *
              </label>
              <input
                type="text"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                placeholder="e.g., Charizard ex vs Lugia VSTAR"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                disabled={isUploading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description (optional)
              </label>
              <textarea
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
                placeholder="Notes about the match..."
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue resize-none"
                disabled={isUploading}
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
              disabled={isUploading}
            />

            {/* Upload Progress Bar */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-pokemon-blue h-full rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                {uploadProgress === 100 && (
                  <p className="text-sm text-gray-600">Processing video...</p>
                )}
              </div>
            )}

            <div className="flex gap-2 justify-end">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowUpload(false);
                  setSelectedFile(null);
                  setUploadTitle('');
                  setUploadDescription('');
                }}
                disabled={isUploading}
              >
                Cancel
              </Button>
              <Button
                onClick={handleUpload}
                loading={isUploading}
                disabled={!selectedFile || !uploadTitle || isUploading}
              >
                {isUploading ? `Uploading ${uploadProgress}%` : 'Upload'}
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
          <PlayIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">No videos yet</p>
          <p className="text-sm text-gray-500">Upload your first match video to get AI-powered analysis!</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {videos.map((video) => (
            <Card key={video.id} padding="none" className="overflow-hidden group">
              {/* Thumbnail */}
              <div
                className="aspect-video bg-gray-900 relative cursor-pointer"
                onClick={() => router.push(`/videos/${video.id}`)}
              >
                {video.thumbnail_path ? (
                  <img
                    src={getVideoThumbnailUrl(video.id)}
                    alt={video.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <PlayIcon className="h-16 w-16 text-gray-600" />
                  </div>
                )}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center">
                  <EyeIcon className="h-10 w-10 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <div className="absolute bottom-2 right-2 bg-black/75 text-white text-xs px-2 py-1 rounded">
                  {formatDuration(video.duration_seconds)}
                </div>
              </div>

              {/* Info */}
              <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3
                    className="font-semibold text-gray-900 line-clamp-1 cursor-pointer hover:text-pokemon-blue"
                    onClick={() => router.push(`/videos/${video.id}`)}
                  >
                    {video.title}
                  </h3>
                  <span className={`px-2 py-0.5 rounded text-xs flex-shrink-0 ml-2 ${getStatusColor(video.status)}`}>
                    {video.status}
                  </span>
                </div>

                <div className="text-sm text-gray-500 mb-4">
                  <span>{formatFileSize(video.file_size)}</span>
                  {video.resolution && <span className="ml-2">{video.resolution}</span>}
                </div>

                {video.analysis_result && (
                  <div
                    className="mb-4 p-2 bg-green-50 rounded text-sm text-green-800 cursor-pointer hover:bg-green-100"
                    onClick={() => router.push(`/videos/${video.id}`)}
                  >
                    <SparklesIcon className="h-4 w-4 inline mr-1" />
                    AI Analysis available - Click to view
                  </div>
                )}

                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => router.push(`/videos/${video.id}`)}
                  >
                    <EyeIcon className="h-4 w-4 mr-1" />
                    View
                  </Button>
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
                    onClick={() => {
                      if (confirm('Are you sure you want to delete this video?')) {
                        deleteMutation.mutate(video.id);
                      }
                    }}
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
