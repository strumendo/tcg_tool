// TypeScript interfaces matching backend Pydantic schemas

export type CardType = "pokemon" | "trainer" | "energy";
export type TrainerSubtype = "supporter" | "item" | "stadium" | "tool";
export type CardFunction =
  | "draw"
  | "search"
  | "recovery"
  | "removal"
  | "switching"
  | "energy_accel"
  | "damage"
  | "healing"
  | "disruption"
  | "setup"
  | "protection"
  | "other";

export type Severity = "NONE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
export type BattleResult = "win" | "loss" | "draw";
export type Language = "en" | "pt";

// Card models
export interface CardSet {
  id: number;
  code: string;
  tcgdex_id: string | null;
  name_en: string;
  name_pt: string | null;
  regulation_mark: string | null;
  release_date: string | null;
  total_cards: number | null;
  is_legal: boolean;
}

export interface CardAbility {
  id: number;
  name_en: string;
  name_pt: string | null;
  effect_en: string | null;
  effect_pt: string | null;
  category: string | null;
}

export interface CardAttack {
  id: number;
  name_en: string;
  name_pt: string | null;
  damage: string | null;
  energy_cost: string[];
  effect_en: string | null;
  effect_pt: string | null;
}

export interface Card {
  id: number;
  name_en: string;
  name_pt: string | null;
  card_type: CardType;
  trainer_subtype: TrainerSubtype | null;
  set_id: number;
  set_number: string;
  regulation_mark: string | null;
  hp: number | null;
  energy_type: string | null;
  stage: string | null;
  is_ex: boolean;
  image_url: string | null;
  image_url_hires: string | null;
  abilities: CardAbility[];
  attacks: CardAttack[];
  functions: CardFunction[];
  set?: CardSet;
}

// Deck models
export interface DeckCard {
  id: number;
  card_id: number;
  quantity: number;
  card: Card;
  is_owned?: boolean;
}

export interface Deck {
  id: number;
  user_id: number;
  name: string;
  archetype: string | null;
  notes: string | null;
  is_active: boolean;
  is_valid: boolean;
  total_cards: number;
  cards: DeckCard[];
  created_at: string;
  updated_at: string;
}

export interface DeckCreate {
  name: string;
  archetype?: string;
  notes?: string;
  cards: { card_id: number; quantity: number }[];
}

export interface DeckImport {
  text: string;
  name?: string;
}

// Meta models
export interface MetaDeck {
  id: string;
  name_en: string;
  name_pt: string | null;
  tier: number;
  description_en: string | null;
  description_pt: string | null;
  strategy_en: string | null;
  strategy_pt: string | null;
  difficulty: string | null;
  meta_share: number;
  key_pokemon: string[];
  energy_types: string[];
  strengths_en: string[];
  strengths_pt: string[];
  weaknesses_en: string[];
  weaknesses_pt: string[];
  cards: DeckCard[];
  matchups: MetaMatchup[];
}

export interface MetaMatchup {
  deck_a_id: string;
  deck_b_id: string;
  win_rate_a: number;
  notes_en: string | null;
  notes_pt: string | null;
}

// Analysis models
export interface RotationBreakdown {
  rotating: number;
  illegal: number;
  safe: number;
}

export interface RotationReport {
  total_cards: number;
  rotating_cards: number;
  illegal_cards: number;
  safe_cards: number;
  rotation_percentage: number;
  problem_percentage: number;
  severity: Severity;
  breakdown: {
    pokemon: RotationBreakdown;
    trainers: RotationBreakdown;
    energy: RotationBreakdown;
  };
}

export interface DeckComparison {
  shared_cards: { card_a: Card; card_b: Card }[];
  unique_to_a: Card[];
  unique_to_b: Card[];
  similarity_percentage: number;
}

export interface MatchupAnalysis {
  a_advantages: string[];
  b_advantages: string[];
  key_differences: string[];
  speed_score_a: number;
  speed_score_b: number;
  consistency_score_a: number;
  consistency_score_b: number;
  power_score_a: number;
  power_score_b: number;
  matchup_favor: string;
}

export interface SubstitutionSuggestion {
  original_card: Card;
  suggested_card: Card;
  match_score: number;
  reasons: string[];
}

// Battle models
export interface BattleAction {
  turn: number;
  player: string;
  action_type: string;
  card_name: string | null;
  details: string | null;
}

export interface Battle {
  id: number;
  user_id: number;
  deck_id: number | null;
  opponent_deck_name: string | null;
  opponent_meta_deck_id: string | null;
  result: BattleResult;
  total_turns: number | null;
  went_first: boolean | null;
  notes: string | null;
  source: string;
  source_url: string | null;
  actions: BattleAction[];
  played_at: string;
  created_at: string;
}

export interface BattleCreate {
  deck_id: number;
  opponent_deck_name?: string;
  opponent_meta_deck_id?: string;
  result: BattleResult;
  total_turns?: number;
  went_first?: boolean;
  notes?: string;
  source?: string;
  actions?: Omit<BattleAction, "id">[];
}

// Chat models
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  deck_id?: number;
  context?: string;
}

// Stats models
export interface CardUsageStats {
  card_id: number;
  card_name: string;
  usage_percentage: number;
  avg_copies: number;
  sample_size: number;
}

export interface DeckUsageStats {
  archetype: string;
  meta_share: number;
  avg_placement: number;
  sample_size: number;
}

export interface UserStats {
  total_battles: number;
  win_rate: number;
  total_decks: number;
  most_played_deck: string | null;
  best_matchup: string | null;
  worst_matchup: string | null;
}

// Collection models
export interface CollectionEntry {
  id?: number;
  user_id?: number;
  card_id: number;
  card: Card;
  quantity_owned: number;
}

export interface MissingCard {
  card_id: number;
  card_name: string | null;
  quantity_needed: number;
  quantity_owned: number;
  quantity_missing: number;
}

// Tournament models
export interface Tournament {
  id: string;
  name: string;
  date: string | null;
  end_date: string | null;
  location: string | null;
  country: string | null;
  format: string;
  event_type: string | null;
  url: string | null;
}

export interface NewsArticle {
  id: string;
  title: string;
  summary: string | null;
  url: string | null;
  image_url: string | null;
  source: string;
  published_at: string | null;
}

// Simulation models
export interface PlaySequence {
  turn: number;
  action: string;
  card_name: string | null;
  reasoning: string;
}

export interface SimulationResult {
  deck_name: string;
  opponent_name: string;
  turns: PlaySequence[];
  win_probability: number;
  key_insights: string[];
}

// API response wrappers
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
