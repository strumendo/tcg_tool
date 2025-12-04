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
