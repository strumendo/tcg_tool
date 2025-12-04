'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  getDecks,
  getImprovementPlan,
  analyzeDeck,
  getMatchupAdvice,
  getQuickTips,
} from '@/lib/api';
import {
  AcademicCapIcon,
  ChartBarIcon,
  LightBulbIcon,
  ArrowTrendingUpIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface Deck {
  id: number;
  name: string;
  archetype?: string;
}

interface ImprovementPlan {
  status: string;
  message?: string;
  overall_stats?: {
    total_matches: number;
    win_rate: number;
    wins: number;
    losses: number;
  };
  problem_matchups?: Array<{ archetype: string; win_rate: number }>;
  strong_matchups?: Array<{ archetype: string; win_rate: number }>;
  focus_areas?: string[];
  weekly_goals?: string[];
  next_steps?: string[];
}

interface DeckAnalysis {
  deck_name: string;
  archetype?: string;
  stats: {
    total_matches: number;
    wins: number;
    losses: number;
    win_rate: number;
  };
  analysis: {
    summary: string;
    strengths: string[];
    weaknesses: string[];
    tips: string[];
    matchup_advice?: Array<{ archetype: string; advice: string }>;
  };
}

export default function CoachingPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [decks, setDecks] = useState<Deck[]>([]);
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [improvementPlan, setImprovementPlan] = useState<ImprovementPlan | null>(null);
  const [deckAnalysis, setDeckAnalysis] = useState<DeckAnalysis | null>(null);
  const [quickTips, setQuickTips] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [decksRes, planRes, tipsRes] = await Promise.all([
        getDecks({ page_size: 100 }),
        getImprovementPlan(),
        getQuickTips(),
      ]);

      setDecks(decksRes.data.decks || decksRes.data || []);
      setImprovementPlan(planRes.data);
      setQuickTips(tipsRes.data);
    } catch (err) {
      toast.error('Failed to load coaching data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeDeck = async () => {
    if (!selectedDeck) {
      toast.error('Please select a deck');
      return;
    }

    setIsAnalyzing(true);
    try {
      const res = await analyzeDeck(selectedDeck);
      setDeckAnalysis(res.data);
    } catch (err) {
      toast.error('Failed to analyze deck');
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <AcademicCapIcon className="h-8 w-8 text-pokemon-blue" />
        <h1 className="text-2xl font-bold text-gray-900">AI Coach</h1>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pokemon-blue mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading coaching insights...</p>
        </div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Improvement Plan */}
            {improvementPlan && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ArrowTrendingUpIcon className="h-5 w-5 text-green-500" />
                    Your Improvement Plan
                  </CardTitle>
                </CardHeader>

                {improvementPlan.status === 'no_data' ? (
                  <div className="text-center py-6">
                    <p className="text-gray-600 mb-4">{improvementPlan.message}</p>
                    <ul className="text-left max-w-md mx-auto space-y-2">
                      {improvementPlan.next_steps?.map((step, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                          <span className="w-6 h-6 rounded-full bg-pokemon-blue text-white flex items-center justify-center text-xs">
                            {i + 1}
                          </span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Stats Overview */}
                    {improvementPlan.overall_stats && (
                      <div className="grid grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-900">
                            {improvementPlan.overall_stats.total_matches}
                          </p>
                          <p className="text-xs text-gray-500">Matches</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">
                            {improvementPlan.overall_stats.wins}
                          </p>
                          <p className="text-xs text-gray-500">Wins</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-red-600">
                            {improvementPlan.overall_stats.losses}
                          </p>
                          <p className="text-xs text-gray-500">Losses</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-pokemon-blue">
                            {improvementPlan.overall_stats.win_rate}%
                          </p>
                          <p className="text-xs text-gray-500">Win Rate</p>
                        </div>
                      </div>
                    )}

                    {/* Matchup Insights */}
                    <div className="grid md:grid-cols-2 gap-4">
                      {/* Problem Matchups */}
                      {improvementPlan.problem_matchups && improvementPlan.problem_matchups.length > 0 && (
                        <div className="p-4 bg-red-50 rounded-lg">
                          <h4 className="font-medium text-red-800 flex items-center gap-2 mb-2">
                            <ExclamationTriangleIcon className="h-4 w-4" />
                            Needs Work
                          </h4>
                          <ul className="space-y-1">
                            {improvementPlan.problem_matchups.map((m) => (
                              <li key={m.archetype} className="text-sm text-red-700">
                                vs {m.archetype}: {m.win_rate}% WR
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Strong Matchups */}
                      {improvementPlan.strong_matchups && improvementPlan.strong_matchups.length > 0 && (
                        <div className="p-4 bg-green-50 rounded-lg">
                          <h4 className="font-medium text-green-800 flex items-center gap-2 mb-2">
                            <CheckCircleIcon className="h-4 w-4" />
                            Strong Against
                          </h4>
                          <ul className="space-y-1">
                            {improvementPlan.strong_matchups.map((m) => (
                              <li key={m.archetype} className="text-sm text-green-700">
                                vs {m.archetype}: {m.win_rate}% WR
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Focus Areas */}
                    {improvementPlan.focus_areas && improvementPlan.focus_areas.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Focus Areas</h4>
                        <ul className="space-y-1">
                          {improvementPlan.focus_areas.map((area, i) => (
                            <li key={i} className="text-sm text-gray-600 flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-pokemon-blue"></span>
                              {area}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Weekly Goals */}
                    {improvementPlan.weekly_goals && improvementPlan.weekly_goals.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Weekly Goals</h4>
                        <ul className="space-y-2">
                          {improvementPlan.weekly_goals.map((goal, i) => (
                            <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                              <input type="checkbox" className="mt-1 rounded" />
                              {goal}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            )}

            {/* Deck Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <SparklesIcon className="h-5 w-5 text-purple-500" />
                  Deck Analysis
                </CardTitle>
              </CardHeader>

              <div className="space-y-4">
                <div className="flex gap-4">
                  <select
                    value={selectedDeck || ''}
                    onChange={(e) => setSelectedDeck(e.target.value ? Number(e.target.value) : null)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pokemon-blue"
                  >
                    <option value="">Select a deck to analyze</option>
                    {decks.map((deck) => (
                      <option key={deck.id} value={deck.id}>
                        {deck.name} {deck.archetype && `(${deck.archetype})`}
                      </option>
                    ))}
                  </select>
                  <Button onClick={handleAnalyzeDeck} loading={isAnalyzing} disabled={!selectedDeck}>
                    Analyze
                  </Button>
                </div>

                {deckAnalysis && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-lg">{deckAnalysis.deck_name}</h3>
                        <p className="text-sm text-gray-500">{deckAnalysis.archetype}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-pokemon-blue">
                          {deckAnalysis.stats.win_rate}%
                        </p>
                        <p className="text-xs text-gray-500">
                          {deckAnalysis.stats.wins}W - {deckAnalysis.stats.losses}L
                        </p>
                      </div>
                    </div>

                    <p className="text-gray-700">{deckAnalysis.analysis.summary}</p>

                    <div className="grid md:grid-cols-2 gap-4">
                      {/* Strengths */}
                      <div className="p-4 bg-green-50 rounded-lg">
                        <h4 className="font-medium text-green-800 mb-2">Strengths</h4>
                        <ul className="space-y-1">
                          {deckAnalysis.analysis.strengths.map((s, i) => (
                            <li key={i} className="text-sm text-green-700 flex items-start gap-2">
                              <CheckCircleIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
                              {s}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Weaknesses */}
                      <div className="p-4 bg-yellow-50 rounded-lg">
                        <h4 className="font-medium text-yellow-800 mb-2">Areas to Improve</h4>
                        <ul className="space-y-1">
                          {deckAnalysis.analysis.weaknesses.map((w, i) => (
                            <li key={i} className="text-sm text-yellow-700 flex items-start gap-2">
                              <ExclamationTriangleIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
                              {w}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Tips */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Coaching Tips</h4>
                      <ul className="space-y-2">
                        {deckAnalysis.analysis.tips.map((tip, i) => (
                          <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                            <LightBulbIcon className="h-4 w-4 mt-0.5 text-yellow-500 flex-shrink-0" />
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Sidebar - Quick Tips */}
          <div className="space-y-6">
            {quickTips && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <LightBulbIcon className="h-5 w-5 text-yellow-500" />
                      General Tips
                    </CardTitle>
                  </CardHeader>
                  <ul className="space-y-2">
                    {quickTips.general_tips?.map((tip: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-pokemon-blue">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Going First</CardTitle>
                  </CardHeader>
                  <ul className="space-y-2">
                    {quickTips.going_first_tips?.map((tip: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-green-500">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Going Second</CardTitle>
                  </CardHeader>
                  <ul className="space-y-2">
                    {quickTips.going_second_tips?.map((tip: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-blue-500">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Late Game</CardTitle>
                  </CardHeader>
                  <ul className="space-y-2">
                    {quickTips.late_game_tips?.map((tip: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-purple-500">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </Card>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
