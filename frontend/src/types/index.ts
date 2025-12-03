// Card Types
export type CardType = 'pokemon' | 'trainer' | 'energy';

export type CardSubtype =
  | 'basic' | 'stage1' | 'stage2'
  | 'vstar' | 'vmax' | 'v' | 'ex' | 'gx' | 'radiant'
  | 'item' | 'supporter' | 'stadium' | 'tool'
  | 'basic_energy' | 'special_energy';

export type EnergyType =
  | 'grass' | 'fire' | 'water' | 'lightning'
  | 'psychic' | 'fighting' | 'darkness' | 'metal'
  | 'dragon' | 'colorless' | 'fairy';

export interface CardSet {
  id: number;
  code: string;
  name: string;
  series?: string;
  release_date?: string;
  total_cards?: number;
  logo_url?: string;
  symbol_url?: string;
}

export interface Card {
  id: number;
  limitless_id?: string;
  ptcgo_code?: string;
  name: string;
  card_type: CardType;
  subtype?: CardSubtype;
  set_id?: number;
  set?: CardSet;
  set_number?: string;
  hp?: number;
  energy_type?: EnergyType;
  weakness?: string;
  resistance?: string;
  retreat_cost?: number;
  abilities?: any[];
  attacks?: any[];
  rules?: string;
  image_small?: string;
  image_large?: string;
  rarity?: string;
  artist?: string;
  regulation_mark?: string;
  is_standard_legal: boolean;
  is_expanded_legal: boolean;
}

// Deck Types
export type DeckFormat = 'standard' | 'expanded' | 'unlimited';

export interface DeckCard {
  id: number;
  card_id: number;
  quantity: number;
  card?: Card;
}

export interface Deck {
  id: number;
  name: string;
  description?: string;
  format: DeckFormat;
  archetype?: string;
  is_active: boolean;
  is_public: boolean;
  total_cards: number;
  pokemon_count: number;
  trainer_count: number;
  energy_count: number;
  cards: DeckCard[];
  created_at: string;
  updated_at: string;
}

// Match Types
export type MatchResult = 'win' | 'loss' | 'draw' | 'concede';

export type ActionType =
  | 'draw' | 'play_pokemon' | 'evolve' | 'attach_energy'
  | 'play_trainer' | 'attack' | 'ability' | 'retreat'
  | 'knock_out' | 'prize_take' | 'turn_start' | 'turn_end' | 'other';

export interface MatchAction {
  id: number;
  turn_number: number;
  action_order: number;
  is_player_action: boolean;
  action_type: ActionType;
  card_name?: string;
  target_card?: string;
  description?: string;
  damage_dealt?: number;
}

export interface Match {
  id: number;
  deck_id?: number;
  opponent_deck_archetype?: string;
  result?: MatchResult;
  player_prizes_taken: number;
  opponent_prizes_taken: number;
  total_turns?: number;
  went_first?: boolean;
  match_date?: string;
  import_source?: string;
  actions: MatchAction[];
  created_at: string;
}

// Video Types
export type VideoStatus = 'uploading' | 'processing' | 'analyzing' | 'ready' | 'error';

export interface Video {
  id: number;
  title: string;
  description?: string;
  filename: string;
  file_path: string;
  file_size?: number;
  duration_seconds?: number;
  format?: string;
  resolution?: string;
  status: VideoStatus;
  thumbnail_path?: string;
  error_message?: string;
  analysis_result?: string;
  analyzed_at?: string;
  deck_id?: number;
  match_id?: number;
  created_at: string;
}

// YouTube Channel Types
export interface YouTubeChannel {
  id: number;
  channel_id: string;
  name: string;
  description?: string;
  url: string;
  thumbnail_url?: string;
  subscriber_count?: number;
  video_count?: number;
  category?: string;
  tags?: string;
  is_active: boolean;
  is_favorite: boolean;
  notes?: string;
  created_at: string;
}

// Meta Types
export interface MetaDeck {
  id: number;
  archetype: string;
  rank: number;
  meta_share: number;
  play_rate?: number;
  win_rate?: number;
  matchups?: Record<string, number>;
  core_cards?: string[];
  day2_conversion?: number;
  top8_count?: number;
  top16_count?: number;
}

export interface MetaSnapshot {
  id: number;
  name: string;
  description?: string;
  snapshot_date: string;
  source?: string;
  tournament_name?: string;
  total_players?: number;
  meta_decks: MetaDeck[];
  created_at: string;
}

export interface DeckComparisonResult {
  deck_archetype: string;
  meta_position?: number;
  matchup_analysis: Record<string, { win_rate: number; notes: string }>;
  overall_meta_score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

// Paginated Response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
