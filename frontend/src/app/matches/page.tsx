'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import { getMatches, importMatchFromScreenshot, deleteMatch } from '@/lib/api';
import { Match } from '@/types';
import { TrashIcon, TrophyIcon, XCircleIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export default function MatchesPage() {
  const [showImport, setShowImport] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['matches'],
    queryFn: () => getMatches(),
  });

  const importMutation = useMutation({
    mutationFn: (file: File) => importMatchFromScreenshot(file),
    onSuccess: () => {
      toast.success('Match imported successfully!');
      queryClient.invalidateQueries({ queryKey: ['matches'] });
      setShowImport(false);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to import match');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteMatch(id),
    onSuccess: () => {
      toast.success('Match deleted');
      queryClient.invalidateQueries({ queryKey: ['matches'] });
    },
  });

  const matches: Match[] = data?.data?.matches || [];

  const getResultIcon = (result?: string) => {
    switch (result) {
      case 'win':
        return <TrophyIcon className="h-5 w-5 text-green-500" />;
      case 'loss':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getResultColor = (result?: string) => {
    switch (result) {
      case 'win': return 'bg-green-100 text-green-800';
      case 'loss': return 'bg-red-100 text-red-800';
      case 'draw': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Match History</h1>
          <p className="text-gray-600 mt-1">Import matches from Pokemon TCG Live</p>
        </div>
        <Button onClick={() => setShowImport(!showImport)}>
          Import Match
        </Button>
      </div>

      {showImport && (
        <Card>
          <CardHeader>
            <CardTitle>Import from Screenshot</CardTitle>
          </CardHeader>
          <p className="text-sm text-gray-600 mb-4">
            Take a screenshot of your match summary in Pokemon TCG Live and upload it here.
            Our OCR will extract the match details automatically.
          </p>
          <FileUpload
            onUpload={(files) => importMutation.mutate(files[0])}
            accept={{
              'image/*': ['.png', '.jpg', '.jpeg'],
            }}
            label="Upload screenshot"
            hint="Supports PNG, JPG"
          />
        </Card>
      )}

      {/* Match Stats Summary */}
      {matches.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="text-center">
            <p className="text-3xl font-bold text-gray-900">{matches.length}</p>
            <p className="text-sm text-gray-600">Total Matches</p>
          </Card>
          <Card className="text-center">
            <p className="text-3xl font-bold text-green-600">
              {matches.filter(m => m.result === 'win').length}
            </p>
            <p className="text-sm text-gray-600">Wins</p>
          </Card>
          <Card className="text-center">
            <p className="text-3xl font-bold text-red-600">
              {matches.filter(m => m.result === 'loss').length}
            </p>
            <p className="text-sm text-gray-600">Losses</p>
          </Card>
          <Card className="text-center">
            <p className="text-3xl font-bold text-pokemon-blue">
              {matches.length > 0
                ? ((matches.filter(m => m.result === 'win').length / matches.length) * 100).toFixed(0)
                : 0}%
            </p>
            <p className="text-sm text-gray-600">Win Rate</p>
          </Card>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
        </div>
      ) : matches.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-gray-600">No matches yet. Import your first match from Pokemon TCG Live!</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <Card key={match.id} className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {getResultIcon(match.result)}
                <div>
                  <p className="font-semibold text-gray-900">
                    vs {match.opponent_deck_archetype || 'Unknown'}
                  </p>
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>Prizes: {match.player_prizes_taken} - {match.opponent_prizes_taken}</span>
                    {match.total_turns && <span>{match.total_turns} turns</span>}
                    {match.went_first !== undefined && (
                      <span>{match.went_first ? 'Went first' : 'Went second'}</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <span className={`px-3 py-1 rounded text-sm font-medium ${getResultColor(match.result)}`}>
                  {match.result?.toUpperCase() || 'UNKNOWN'}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteMutation.mutate(match.id)}
                >
                  <TrashIcon className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
