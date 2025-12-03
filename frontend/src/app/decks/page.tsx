'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/ui/FileUpload';
import { getDecks, importDeckFromFile, deleteDeck } from '@/lib/api';
import { Deck } from '@/types';
import { PlusIcon, TrashIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function DecksPage() {
  const [showImport, setShowImport] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['decks'],
    queryFn: () => getDecks(),
  });

  const importMutation = useMutation({
    mutationFn: (file: File) => importDeckFromFile(file),
    onSuccess: () => {
      toast.success('Deck imported successfully!');
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      setShowImport(false);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to import deck');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteDeck(id),
    onSuccess: () => {
      toast.success('Deck deleted');
      queryClient.invalidateQueries({ queryKey: ['decks'] });
    },
    onError: () => {
      toast.error('Failed to delete deck');
    },
  });

  const decks: Deck[] = data?.data?.decks || [];

  const getFormatColor = (format: string) => {
    switch (format) {
      case 'standard': return 'bg-green-100 text-green-800';
      case 'expanded': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Decks</h1>
          <p className="text-gray-600 mt-1">Manage your Pokemon TCG decks</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setShowImport(!showImport)}>
            Import Deck
          </Button>
          <Link href="/decks/new">
            <Button>
              <PlusIcon className="h-4 w-4 mr-2" />
              New Deck
            </Button>
          </Link>
        </div>
      </div>

      {showImport && (
        <Card>
          <CardHeader>
            <CardTitle>Import Deck</CardTitle>
          </CardHeader>
          <FileUpload
            onUpload={(files) => importMutation.mutate(files[0])}
            accept={{ 'text/plain': ['.txt'], 'application/json': ['.json'] }}
            label="Upload deck list"
            hint="Supports PTCGO format (.txt) or JSON"
          />
        </Card>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading decks...</p>
        </div>
      ) : error ? (
        <Card className="text-center py-12">
          <p className="text-red-600">Failed to load decks. Is the backend running?</p>
        </Card>
      ) : decks.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-gray-600">No decks yet. Create or import your first deck!</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {decks.map((deck) => (
            <Card key={deck.id} className="hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">{deck.name}</h3>
                  {deck.archetype && (
                    <p className="text-sm text-gray-600">{deck.archetype}</p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getFormatColor(deck.format)}`}>
                  {deck.format}
                </span>
              </div>

              <div className="flex gap-4 text-sm text-gray-600 mb-4">
                <span>Pokemon: {deck.pokemon_count}</span>
                <span>Trainers: {deck.trainer_count}</span>
                <span>Energy: {deck.energy_count}</span>
              </div>

              <div className="flex gap-2">
                <Link href={`/decks/${deck.id}`} className="flex-1">
                  <Button variant="secondary" className="w-full">View</Button>
                </Link>
                <Link href={`/meta?deck=${deck.id}`}>
                  <Button variant="ghost" title="Analyze vs Meta">
                    <ChartBarIcon className="h-4 w-4" />
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  onClick={() => deleteMutation.mutate(deck.id)}
                  title="Delete"
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
