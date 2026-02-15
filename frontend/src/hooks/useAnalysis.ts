import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";

// Backend response types matching the actual Pydantic schemas

export interface RotationCardOut {
  name: string;
  set_code: string;
  set_number: string;
  quantity: number;
  regulation_mark: string;
  card_type: string;
}

export interface RotationBreakdownOut {
  pokemon: { rotating: number; illegal: number; safe: number };
  trainers: { rotating: number; illegal: number; safe: number };
  energy: { rotating: number; illegal: number; safe: number };
}

export interface RotationReportOut {
  total_cards: number;
  rotating_cards: number;
  illegal_cards: number;
  safe_cards: number;
  rotation_percentage: number;
  problem_percentage: number;
  severity: string;
  breakdown: RotationBreakdownOut;
  rotating_card_list: RotationCardOut[];
  safe_card_list: RotationCardOut[];
}

export interface SharedCardOut {
  name: string;
  quantity_a: number;
  quantity_b: number;
}

export interface UniqueCardOut {
  name: string;
  quantity: number;
  card_type: string;
}

export interface DeckComparisonOut {
  deck_a_name: string;
  deck_b_name: string;
  shared_count: number;
  similarity_percentage: number;
  shared_cards: SharedCardOut[];
  unique_to_a: UniqueCardOut[];
  unique_to_b: UniqueCardOut[];
}

export interface MatchupAnalysisOut {
  deck_a_name: string;
  deck_b_name: string;
  matchup_favor: string;
  a_advantages: string[];
  b_advantages: string[];
  key_differences: string[];
  speed_score_a: number;
  speed_score_b: number;
  consistency_score_a: number;
  consistency_score_b: number;
  power_score_a: number;
  power_score_b: number;
}

export interface SubstitutionSuggestionOut {
  original_name: string;
  original_set_code: string;
  original_set_number: string;
  suggested_name: string;
  suggested_set_code: string;
  suggested_set_number: string;
  match_score: number;
  reasons: string[];
}

export function useRotationAnalysis(deckId: number) {
  return useQuery<RotationReportOut>({
    queryKey: ["analysis", deckId, "rotation"],
    queryFn: async () => {
      const { data } = await api.post("/analysis/rotation", { deck_id: deckId });
      return data;
    },
    enabled: !!deckId,
  });
}

export function useDeckComparison() {
  return useMutation<
    DeckComparisonOut,
    Error,
    { deck_a_id: number; deck_b_id: number; deck_a_name?: string; deck_b_name?: string }
  >({
    mutationFn: async (params) => {
      const { data } = await api.post("/analysis/compare", params);
      return data;
    },
  });
}

export function useMatchupAnalysis() {
  return useMutation<
    MatchupAnalysisOut,
    Error,
    { deck_a_id: number; deck_b_id: number; deck_a_name?: string; deck_b_name?: string }
  >({
    mutationFn: async (params) => {
      const { data } = await api.post("/analysis/matchup", params);
      return data;
    },
  });
}

export function useDeckStrength(deckId: number) {
  return useQuery({
    queryKey: ["analysis", deckId, "strength"],
    queryFn: async () => {
      const { data } = await api.get(`/analysis/${deckId}/strength`);
      return data;
    },
    enabled: !!deckId,
  });
}

export function useSubstitutions(deckId: number) {
  return useQuery<SubstitutionSuggestionOut[]>({
    queryKey: ["analysis", deckId, "substitutions"],
    queryFn: async () => {
      const { data } = await api.post("/analysis/substitutions", { deck_id: deckId });
      return data;
    },
    enabled: !!deckId,
  });
}

export function useAiSuggestions(deckId: number) {
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post(`/analysis/${deckId}/ai-suggestions`);
      return data;
    },
  });
}
