'use client';

import { useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getVideo, analyzeVideo, deleteVideo, createMatchFromVideo, getVideoStreamUrl, getVideoThumbnailUrl } from '@/lib/api';
import { Video } from '@/types';
import {
  ArrowLeftIcon,
  SparklesIcon,
  TrashIcon,
  ClockIcon,
  FilmIcon,
  CalendarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  StarIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  PlusCircleIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface VideoAnalysis {
  match_overview?: string;
  decks_identified?: { player: string; opponent: string };
  key_plays?: Array<{ timestamp: number; description: string; assessment: string }>;
  strategic_insights?: string[];
  strengths?: string[];
  areas_for_improvement?: string[];
  overall_rating?: number;
  summary?: string;
  result?: string;
  player_deck?: string;
  opponent_deck?: string;
  turning_point?: string;
  key_moments?: Array<{
    timestamp: number;
    description: string;
    decision_made: string;
    optimal_play: string;
    impact: string;
  }>;
  raw_analysis?: string;
}

export default function VideoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const videoId = parseInt(params.id as string);
  const videoRef = useRef<HTMLVideoElement>(null);

  const [analysisType, setAnalysisType] = useState<'full' | 'summary' | 'key_moments'>('full');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview', 'insights']));

  const { data, isLoading, error } = useQuery({
    queryKey: ['video', videoId],
    queryFn: () => getVideo(videoId),
    enabled: !isNaN(videoId),
  });

  const analyzeMutation = useMutation({
    mutationFn: () => analyzeVideo(videoId, analysisType),
    onSuccess: () => {
      toast.success('Video analysis completed!');
      queryClient.invalidateQueries({ queryKey: ['video', videoId] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to analyze video');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteVideo(videoId),
    onSuccess: () => {
      toast.success('Video deleted');
      router.push('/videos');
    },
  });

  const createMatchMutation = useMutation({
    mutationFn: () => createMatchFromVideo(videoId),
    onSuccess: (response) => {
      toast.success('Match created from video analysis!');
      router.push(`/matches/${response.data.id}`);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to create match');
    },
  });

  const video: Video | undefined = data?.data;
  const analysis: VideoAnalysis | null = video?.analysis_result
    ? JSON.parse(video.analysis_result)
    : null;

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
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

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '--';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const seekToTime = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'analyzing':
        return 'bg-blue-100 text-blue-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const renderRating = (rating?: number) => {
    if (!rating) return null;
    return (
      <div className="flex items-center gap-1">
        {[...Array(10)].map((_, i) => (
          <StarIcon
            key={i}
            className={`h-4 w-4 ${i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
          />
        ))}
        <span className="ml-2 text-sm font-medium">{rating}/10</span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue"></div>
      </div>
    );
  }

  if (error || !video) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Video not found</p>
        <Button className="mt-4" onClick={() => router.push('/videos')}>
          Back to Videos
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push('/videos')}>
            <ArrowLeftIcon className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{video.title}</h1>
            <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
              <span className={`px-2 py-0.5 rounded ${getStatusColor(video.status)}`}>
                {video.status}
              </span>
              <span className="flex items-center">
                <ClockIcon className="h-4 w-4 mr-1" />
                {formatDuration(video.duration_seconds)}
              </span>
              <span className="flex items-center">
                <FilmIcon className="h-4 w-4 mr-1" />
                {formatFileSize(video.file_size)}
              </span>
              <span className="flex items-center">
                <CalendarIcon className="h-4 w-4 mr-1" />
                {formatDate(video.created_at)}
              </span>
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          onClick={() => {
            if (confirm('Are you sure you want to delete this video?')) {
              deleteMutation.mutate();
            }
          }}
        >
          <TrashIcon className="h-5 w-5 text-red-500" />
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video Player Column */}
        <div className="lg:col-span-2 space-y-4">
          {/* Video Player */}
          <Card padding="none" className="overflow-hidden">
            <div className="aspect-video bg-black">
              {video.status === 'ready' ? (
                <video
                  ref={videoRef}
                  className="w-full h-full"
                  controls
                  poster={video.thumbnail_path ? getVideoThumbnailUrl(video.id) : undefined}
                >
                  <source src={getVideoStreamUrl(video.id)} type={`video/${video.format || 'mp4'}`} />
                  Your browser does not support the video tag.
                </video>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center text-white">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                    <p>Video is {video.status}...</p>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Description */}
          {video.description && (
            <Card>
              <h3 className="font-medium text-gray-900 mb-2">Description</h3>
              <p className="text-gray-600">{video.description}</p>
            </Card>
          )}

          {/* Key Plays Timeline (if analysis available) */}
          {analysis?.key_plays && analysis.key_plays.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ClockIcon className="h-5 w-5 mr-2" />
                  Key Plays Timeline
                </CardTitle>
              </CardHeader>
              <div className="space-y-3">
                {analysis.key_plays.map((play, index) => (
                  <div
                    key={index}
                    className="flex gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                    onClick={() => seekToTime(play.timestamp)}
                  >
                    <div className="flex-shrink-0 w-16 text-pokemon-blue font-mono font-medium">
                      {formatDuration(play.timestamp)}
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-900">{play.description}</p>
                      {play.assessment && (
                        <p className="text-sm text-gray-500 mt-1">{play.assessment}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Key Moments (alternative analysis type) */}
          {analysis?.key_moments && analysis.key_moments.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <LightBulbIcon className="h-5 w-5 mr-2" />
                  Key Decision Points
                </CardTitle>
              </CardHeader>
              <div className="space-y-4">
                {analysis.key_moments.map((moment, index) => (
                  <div
                    key={index}
                    className="p-4 border rounded-lg hover:border-pokemon-blue cursor-pointer"
                    onClick={() => seekToTime(moment.timestamp)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-pokemon-blue font-mono font-medium">
                        {formatDuration(moment.timestamp)}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${
                          moment.impact === 'high'
                            ? 'bg-red-100 text-red-800'
                            : moment.impact === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {moment.impact} impact
                      </span>
                    </div>
                    <p className="text-gray-900 font-medium">{moment.description}</p>
                    <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Decision made:</span>
                        <p className="text-gray-700">{moment.decision_made}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Optimal play:</span>
                        <p className="text-gray-700">{moment.optimal_play}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Analysis Sidebar */}
        <div className="space-y-4">
          {/* Analysis Actions */}
          {video.status === 'ready' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <SparklesIcon className="h-5 w-5 mr-2" />
                  AI Analysis
                </CardTitle>
              </CardHeader>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Analysis Type
                  </label>
                  <select
                    value={analysisType}
                    onChange={(e) => setAnalysisType(e.target.value as typeof analysisType)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                    disabled={analyzeMutation.isPending}
                  >
                    <option value="full">Full Analysis</option>
                    <option value="summary">Quick Summary</option>
                    <option value="key_moments">Key Moments Only</option>
                  </select>
                </div>
                <Button
                  className="w-full"
                  onClick={() => analyzeMutation.mutate()}
                  loading={analyzeMutation.isPending}
                >
                  <SparklesIcon className="h-4 w-4 mr-2" />
                  {analysis ? 'Re-analyze Video' : 'Analyze Video'}
                </Button>
                {!analysis && (
                  <p className="text-xs text-gray-500 text-center">
                    AI will analyze key frames to provide match insights
                  </p>
                )}
              </div>
            </Card>
          )}

          {/* Create Match from Analysis */}
          {analysis && !video.match_id && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <PlusCircleIcon className="h-5 w-5 mr-2" />
                  Track This Match
                </CardTitle>
              </CardHeader>
              <div className="space-y-3">
                <p className="text-sm text-gray-600">
                  Create a match record from the AI analysis to track your performance over time.
                </p>
                <Button
                  className="w-full"
                  onClick={() => createMatchMutation.mutate()}
                  loading={createMatchMutation.isPending}
                >
                  <PlusCircleIcon className="h-4 w-4 mr-2" />
                  Create Match Record
                </Button>
              </div>
            </Card>
          )}

          {video.match_id && (
            <Card className="bg-green-50 border-green-200">
              <div className="flex items-center gap-2 text-green-800">
                <CheckCircleIcon className="h-5 w-5" />
                <span className="font-medium">Match Tracked</span>
              </div>
              <p className="text-sm text-green-700 mt-2">
                This video is linked to a match record.
              </p>
              <Button
                variant="secondary"
                size="sm"
                className="mt-3"
                onClick={() => router.push(`/matches/${video.match_id}`)}
              >
                View Match Details
              </Button>
            </Card>
          )}

          {/* Analysis Results */}
          {analysis && (
            <>
              {/* Match Overview */}
              {(analysis.match_overview || analysis.summary) && (
                <Card>
                  <button
                    className="w-full flex items-center justify-between"
                    onClick={() => toggleSection('overview')}
                  >
                    <CardTitle className="flex items-center">
                      <FilmIcon className="h-5 w-5 mr-2" />
                      Match Overview
                    </CardTitle>
                    {expandedSections.has('overview') ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                  {expandedSections.has('overview') && (
                    <div className="mt-4 space-y-4">
                      {analysis.overall_rating && (
                        <div>
                          <span className="text-sm text-gray-500">Overall Rating</span>
                          {renderRating(analysis.overall_rating)}
                        </div>
                      )}
                      <p className="text-gray-700">
                        {analysis.match_overview || analysis.summary}
                      </p>
                      {analysis.decks_identified && (
                        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
                          <div>
                            <span className="text-xs text-gray-500">Your Deck</span>
                            <p className="font-medium text-gray-900">
                              {analysis.decks_identified.player || analysis.player_deck}
                            </p>
                          </div>
                          <div>
                            <span className="text-xs text-gray-500">Opponent</span>
                            <p className="font-medium text-gray-900">
                              {analysis.decks_identified.opponent || analysis.opponent_deck}
                            </p>
                          </div>
                        </div>
                      )}
                      {analysis.result && (
                        <div className="pt-2 border-t">
                          <span className="text-xs text-gray-500">Result</span>
                          <p
                            className={`font-medium ${
                              analysis.result === 'win' ? 'text-green-600' : 'text-red-600'
                            }`}
                          >
                            {analysis.result.toUpperCase()}
                          </p>
                        </div>
                      )}
                      {analysis.turning_point && (
                        <div className="pt-2 border-t">
                          <span className="text-xs text-gray-500">Turning Point</span>
                          <p className="text-gray-700">{analysis.turning_point}</p>
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              )}

              {/* Strengths & Improvements */}
              {(analysis.strengths || analysis.areas_for_improvement) && (
                <Card>
                  <button
                    className="w-full flex items-center justify-between"
                    onClick={() => toggleSection('insights')}
                  >
                    <CardTitle className="flex items-center">
                      <LightBulbIcon className="h-5 w-5 mr-2" />
                      Insights
                    </CardTitle>
                    {expandedSections.has('insights') ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                  {expandedSections.has('insights') && (
                    <div className="mt-4 space-y-4">
                      {analysis.strengths && analysis.strengths.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-green-700 mb-2 flex items-center">
                            <CheckCircleIcon className="h-4 w-4 mr-1" />
                            Strengths
                          </h4>
                          <ul className="space-y-1">
                            {analysis.strengths.map((strength, i) => (
                              <li key={i} className="text-sm text-gray-700 flex items-start">
                                <span className="text-green-500 mr-2">+</span>
                                {strength}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {analysis.areas_for_improvement &&
                        analysis.areas_for_improvement.length > 0 && (
                          <div>
                            <h4 className="text-sm font-medium text-yellow-700 mb-2 flex items-center">
                              <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                              Areas for Improvement
                            </h4>
                            <ul className="space-y-1">
                              {analysis.areas_for_improvement.map((area, i) => (
                                <li key={i} className="text-sm text-gray-700 flex items-start">
                                  <span className="text-yellow-500 mr-2">!</span>
                                  {area}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                    </div>
                  )}
                </Card>
              )}

              {/* Strategic Insights */}
              {analysis.strategic_insights && analysis.strategic_insights.length > 0 && (
                <Card>
                  <button
                    className="w-full flex items-center justify-between"
                    onClick={() => toggleSection('strategic')}
                  >
                    <CardTitle className="flex items-center">
                      <StarIcon className="h-5 w-5 mr-2" />
                      Strategic Insights
                    </CardTitle>
                    {expandedSections.has('strategic') ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                  {expandedSections.has('strategic') && (
                    <ul className="mt-4 space-y-2">
                      {analysis.strategic_insights.map((insight, i) => (
                        <li key={i} className="text-sm text-gray-700 flex items-start">
                          <span className="text-pokemon-blue mr-2 font-bold">{i + 1}.</span>
                          {insight}
                        </li>
                      ))}
                    </ul>
                  )}
                </Card>
              )}

              {/* Raw Analysis (fallback) */}
              {analysis.raw_analysis && !analysis.match_overview && (
                <Card>
                  <CardHeader>
                    <CardTitle>Analysis Results</CardTitle>
                  </CardHeader>
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
                      {analysis.raw_analysis}
                    </pre>
                  </div>
                </Card>
              )}
            </>
          )}

          {/* Video Info */}
          <Card>
            <CardHeader>
              <CardTitle>Video Details</CardTitle>
            </CardHeader>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Filename</dt>
                <dd className="text-gray-900 font-mono text-xs truncate max-w-[200px]">
                  {video.filename}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Resolution</dt>
                <dd className="text-gray-900">{video.resolution || '--'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Format</dt>
                <dd className="text-gray-900">{video.format?.toUpperCase() || '--'}</dd>
              </div>
              {video.analyzed_at && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Analyzed</dt>
                  <dd className="text-gray-900">{formatDate(video.analyzed_at)}</dd>
                </div>
              )}
            </dl>
          </Card>
        </div>
      </div>
    </div>
  );
}
