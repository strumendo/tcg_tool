import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Functions

// Health
export const checkHealth = () => api.get('/health');

// Cards
export const getCards = (params?: {
  page?: number;
  page_size?: number;
  name?: string;
  card_type?: string;
  subtype?: string;
  energy_type?: string;
  rarity?: string;
  regulation_mark?: string;
  set_code?: string;
  standard_only?: boolean;
  sort_by?: 'name' | 'hp' | 'set_number' | 'created_at';
  sort_order?: 'asc' | 'desc';
}) => api.get('/cards', { params });

export const searchCards = (q: string, page?: number, pageSize?: number) =>
  api.get('/cards/search', { params: { q, page, page_size: pageSize } });

export const getCard = (id: number) => api.get(`/cards/${id}`);

export const importCards = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/cards/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getCardSets = () => api.get('/cards/sets/');

// Multilingual Card API (TCGdex + Pokemon TCG API fallback)
export const searchCardsApi = (q: string, page?: number, pageSize?: number, lang?: string) =>
  api.get('/cards/api/search', { params: { q, page, page_size: pageSize, lang } });

export const getCardApi = (cardId: string, lang?: string) =>
  api.get(`/cards/api/card/${cardId}`, { params: { lang } });

export const getSetsApi = (lang?: string) =>
  api.get('/cards/api/sets', { params: { lang } });

export const getSetApi = (setId: string, lang?: string) =>
  api.get(`/cards/api/set/${setId}`, { params: { lang } });

export const getSetCardsApi = (setId: string, page?: number, pageSize?: number, lang?: string) =>
  api.get(`/cards/api/set/${setId}/cards`, { params: { page, page_size: pageSize, lang } });

export const getSupportedLanguages = () => api.get('/cards/languages');

// Sync cards from external API
export const syncSets = () => api.post('/cards/sync/sets');
export const syncSetCards = (setCode: string) => api.post(`/cards/sync/set/${setCode}`);
export const syncStandardCards = () => api.post('/cards/sync/standard');

// Decks
export const getDecks = (params?: { page?: number; format?: string; archetype?: string }) =>
  api.get('/decks', { params });

export const getDeck = (id: number) => api.get(`/decks/${id}`);

export const createDeck = (data: {
  name: string;
  format?: string;
  description?: string;
  archetype?: string;
  cards?: { card_id: number; quantity: number }[];
}) => api.post('/decks', data);

export const updateDeck = (id: number, data: Partial<{
  name: string;
  format: string;
  description: string;
  archetype: string;
}>) => api.put(`/decks/${id}`, data);

export const deleteDeck = (id: number) => api.delete(`/decks/${id}`);

export const addCardToDeck = (deckId: number, cardId: number, quantity: number) =>
  api.post(`/decks/${deckId}/cards`, { card_id: cardId, quantity });

export const importDeckFromText = (data: { deck_list: string; name?: string; format?: string }) =>
  api.post('/decks/import', data);

export const importDeckFromFile = (file: File, name?: string, format?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  if (name) formData.append('name', name);
  if (format) formData.append('format', format);
  return api.post('/decks/import/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Matches
export const getMatches = (params?: { page?: number; deck_id?: number; result?: string }) =>
  api.get('/matches', { params });

export const getMatch = (id: number) => api.get(`/matches/${id}`);

export const createMatch = (data: any) => api.post('/matches', data);

export const deleteMatch = (id: number) => api.delete(`/matches/${id}`);

export const importMatchFromScreenshot = (file: File, deckId?: number) => {
  const formData = new FormData();
  formData.append('file', file);
  if (deckId) formData.append('deck_id', deckId.toString());
  return api.post('/matches/import/ocr', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const importMatchFromText = (textData: string, deckId?: number) =>
  api.post('/matches/import/text', { text_data: textData, deck_id: deckId });

export const getMatchStats = (deckId?: number) =>
  api.get('/matches/stats', { params: { deck_id: deckId } });

// Videos
export const getVideos = (params?: { page?: number; status?: string; deck_id?: number }) =>
  api.get('/videos', { params });

export const getVideo = (id: number) => api.get(`/videos/${id}`);

export const uploadVideo = (file: File, title: string, description?: string, deckId?: number) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  if (description) formData.append('description', description);
  if (deckId) formData.append('deck_id', deckId.toString());
  return api.post('/videos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Video upload with progress tracking
export const uploadVideoWithProgress = (
  file: File,
  title: string,
  onProgress: (progress: number) => void,
  description?: string,
  deckId?: number
) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  if (description) formData.append('description', description);
  if (deckId) formData.append('deck_id', deckId.toString());

  return api.post('/videos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
};

export const analyzeVideo = (id: number, analysisType?: string) =>
  api.post(`/videos/${id}/analyze`, null, { params: { analysis_type: analysisType } });

export const deleteVideo = (id: number) => api.delete(`/videos/${id}`);

export const getVideoThumbnailUrl = (id: number) => `${API_BASE_URL}/api/v1/videos/${id}/thumbnail`;

export const getVideoStreamUrl = (id: number) => `${API_BASE_URL}/api/v1/videos/${id}/stream`;

export const createMatchFromVideo = (videoId: number) =>
  api.post(`/videos/${videoId}/create-match`);

// YouTube Channels
export const getYouTubeChannels = (params?: { page?: number; category?: string; favorites_only?: boolean }) =>
  api.get('/youtube-channels', { params });

export const getYouTubeChannel = (id: number) => api.get(`/youtube-channels/${id}`);

export const addYouTubeChannelFromUrl = (url: string, category?: string) =>
  api.post('/youtube-channels/from-url', null, { params: { url, category } });

export const updateYouTubeChannel = (id: number, data: any) =>
  api.put(`/youtube-channels/${id}`, data);

export const deleteYouTubeChannel = (id: number) => api.delete(`/youtube-channels/${id}`);

export const toggleChannelFavorite = (id: number) => api.post(`/youtube-channels/${id}/favorite`);

// Meta
export const getMetaSnapshots = (params?: { page?: number }) => api.get('/meta/snapshots', { params });

export const getLatestSnapshot = () => api.get('/meta/snapshots/latest');

export const getMetaSnapshot = (id: number) => api.get(`/meta/snapshots/${id}`);

export const getTop10Decks = (snapshotId?: number) =>
  api.get('/meta/top10', { params: { snapshot_id: snapshotId } });

export const compareDeckToMeta = (deckId: number, snapshotId?: number) =>
  api.post('/meta/compare', { deck_id: deckId, snapshot_id: snapshotId });

export const importMetaFromFile = (file: File, name?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  if (name) formData.append('name', name);
  return api.post('/meta/import/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats');

export const getRecentActivity = (limit?: number) =>
  api.get('/dashboard/activity', { params: { limit } });

export const getMatchupSummary = (deckId?: number, days?: number) =>
  api.get('/dashboard/matchup-summary', { params: { deck_id: deckId, days } });

export const getWinRateTrend = (deckId?: number, days?: number) =>
  api.get('/dashboard/win-rate-trend', { params: { deck_id: deckId, days } });

export const getTopDecks = (limit?: number) =>
  api.get('/dashboard/top-decks', { params: { limit } });

// Auth
export const register = (data: { email: string; username: string; password: string; display_name?: string }) =>
  api.post('/auth/register', data);

export const login = (data: { email: string; password: string }) =>
  api.post('/auth/login/json', data);

export const getCurrentUser = () => api.get('/auth/me');

export const updateProfile = (data: { display_name?: string; bio?: string; preferred_language?: string }) =>
  api.put('/auth/me', data);

export const changePassword = (currentPassword: string, newPassword: string) =>
  api.post('/auth/change-password', null, { params: { current_password: currentPassword, new_password: newPassword } });

export const checkAuth = () => api.get('/auth/check');

// Helper to set auth token
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// Tournaments
export const getTournaments = (params?: {
  page?: number;
  page_size?: number;
  format?: string;
  tournament_type?: string;
  status?: string;
  year?: number;
  sort_by?: 'event_date' | 'created_at' | 'name';
  sort_order?: 'asc' | 'desc';
}) => api.get('/tournaments', { params });

export const getTournament = (id: number) => api.get(`/tournaments/${id}`);

export const getTournamentStats = (params?: { year?: number; format?: string }) =>
  api.get('/tournaments/stats', { params });

export const createTournament = (data: {
  name: string;
  format?: string;
  tournament_type?: string;
  event_date: string;
  location?: string;
  organizer?: string;
  total_rounds?: number;
  total_players?: number;
  entry_fee?: number;
  deck_id?: number;
  deck_archetype?: string;
  notes?: string;
}) => api.post('/tournaments', data);

export const updateTournament = (id: number, data: Partial<{
  name: string;
  format: string;
  tournament_type: string;
  event_date: string;
  location: string;
  organizer: string;
  total_rounds: number;
  total_players: number;
  entry_fee: number;
  status: string;
  final_standing: number;
  final_record: string;
  championship_points: number;
  deck_id: number;
  deck_archetype: string;
  notes: string;
}>) => api.put(`/tournaments/${id}`, data);

export const deleteTournament = (id: number) => api.delete(`/tournaments/${id}`);

export const completeTournament = (id: number, finalStanding?: number, championshipPoints?: number) =>
  api.post(`/tournaments/${id}/complete`, null, {
    params: { final_standing: finalStanding, championship_points: championshipPoints }
  });

// Tournament Rounds
export const addTournamentRound = (tournamentId: number, data: {
  round_number: number;
  is_top_cut?: boolean;
  top_cut_round?: string;
  opponent_name?: string;
  opponent_deck?: string;
  opponent_archetype?: string;
  result: 'win' | 'loss' | 'tie' | 'bye' | 'id';
  games_won?: number;
  games_lost?: number;
  went_first_game1?: boolean;
  went_first_game2?: boolean;
  went_first_game3?: boolean;
  notes?: string;
  key_plays?: string;
}) => api.post(`/tournaments/${tournamentId}/rounds`, data);

export const updateTournamentRound = (tournamentId: number, roundId: number, data: any) =>
  api.put(`/tournaments/${tournamentId}/rounds/${roundId}`, data);

export const deleteTournamentRound = (tournamentId: number, roundId: number) =>
  api.delete(`/tournaments/${tournamentId}/rounds/${roundId}`);

// AI Coaching
export const analyzeDeck = (deckId: number) =>
  api.get(`/coaching/deck/${deckId}`);

export const getMatchupAdvice = (deckId: number, opponentArchetype: string) =>
  api.get('/coaching/matchup', { params: { deck_id: deckId, opponent_archetype: opponentArchetype } });

export const getImprovementPlan = () =>
  api.get('/coaching/improvement-plan');

export const getQuickTips = (archetype?: string, opponent?: string) =>
  api.get('/coaching/quick-tips', { params: { archetype, opponent } });

export const getMetaPositioning = (archetype: string) =>
  api.get('/coaching/meta-positioning', { params: { archetype } });

// Export & Sharing
export const exportDeck = (deckId: number, format: 'text' | 'ptcgo' | 'json' | 'limitless' = 'text') =>
  api.get(`/export/deck/${deckId}`, { params: { format }, responseType: format === 'json' ? 'json' : 'text' });

export const getDeckForClipboard = (deckId: number, format: 'text' | 'ptcgo' | 'limitless' = 'text') =>
  api.get(`/export/deck/${deckId}/clipboard`, { params: { format } });

export const exportTournament = (tournamentId: number, format: 'json' | 'csv' = 'json') =>
  api.get(`/export/tournament/${tournamentId}`, { params: { format }, responseType: format === 'json' ? 'json' : 'text' });

export const getTournamentSummary = (tournamentId: number) =>
  api.get(`/export/tournament/${tournamentId}/summary`);

export const exportMatches = (format: 'json' | 'csv' = 'json', deckId?: number) =>
  api.get('/export/matches', { params: { format, deck_id: deckId }, responseType: format === 'json' ? 'json' : 'text' });

export const exportStats = () => api.get('/export/stats');

export const getDeckShareData = (deckId: number) =>
  api.get(`/export/share/deck/${deckId}`);

export const getStatsShareData = () => api.get('/export/share/stats');
