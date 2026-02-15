# ARCHITECTURE.md - TCG Tool v3.0

**Author:** Bruno Strumendo
**Version:** 3.0
**Last Updated:** 2026-02-15

---

## 1. Overview

### Project Description

TCG Tool v3.0 is a **Pokemon Trading Card Game (TCG) deck analysis platform** that provides comprehensive competitive analysis, deck building, and AI-powered insights. The platform enables players to:

- Import and analyze decks from TCG Live or text files
- Build and optimize decks with advanced card search
- Compare decks against meta variations and matchups
- Track tournament results and meta trends
- Process match videos for strategic insights (AI-powered)
- Access news and tournament calendars
- Get AI-powered deck recommendations and analysis

### Goals

1. **Competitive Analysis**: Provide tournament-grade deck analysis with rotation checking, matchup predictions, and meta positioning
2. **Deck Building**: Enable efficient deck construction with smart card search, substitution suggestions, and validation
3. **AI Integration**: Leverage Claude AI for natural language deck analysis, video processing, and strategic insights
4. **Bilingual Support**: Full English/Portuguese support for international player base
5. **Data Aggregation**: Centralize data from multiple sources (TCGdex, Limitless, PokeBeach, RK9)
6. **User Experience**: Modern, responsive web interface with real-time updates

### Evolution from v2.0

- **v1.0**: CLI tool with basic rotation checking
- **v2.0**: Added Android app (Kivy) and meta database
- **v3.0**: Complete rewrite as full-stack web platform with AI integration

---

## 2. Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115+ | Modern async web framework |
| **SQLAlchemy** | 2.0+ | ORM with async support |
| **PostgreSQL** | 16 | Primary database |
| **Alembic** | Latest | Database migrations |
| **Pydantic** | v2 | Data validation and serialization |
| **asyncpg** | Latest | Async PostgreSQL driver |
| **httpx** | 0.28+ | Async HTTP client |
| **Redis** | 7 | Caching layer |
| **Uvicorn** | Latest | ASGI server |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15 | React framework with App Router |
| **TypeScript** | 5.x | Type-safe JavaScript |
| **Tailwind CSS** | 3.x | Utility-first CSS |
| **TanStack Query** | v5 | Server state management |
| **Axios** | Latest | HTTP client |
| **Shadcn/ui** | Latest | UI component library |
| **Lucide React** | Latest | Icon library |

### AI & External Services

| Service | Purpose |
|---------|---------|
| **Anthropic Claude API** | AI-powered analysis, chat, video processing |
| **TCGdex API** | Primary card data (10+ languages) |
| **Pokemon TCG API** | Fallback card data (English) |
| **Limitless TCG** | Tournament data, deck statistics |
| **PokeBeach** | News feed |
| **RK9** | Official tournament calendar |

### DevOps & Tools

| Tool | Purpose |
|------|---------|
| **Docker** | Containerization (PostgreSQL, Redis) |
| **Docker Compose** | Multi-container orchestration |
| **Git** | Version control |
| **pytest** | Backend testing |
| **Jest** | Frontend testing |

---

## 3. Monorepo Structure

```
tcg_tool/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database session management
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/
│   │   │   └── v1/            # API routes (versioned)
│   │   ├── services/          # Business logic layer
│   │   ├── core/              # Core domain logic
│   │   ├── integrations/      # External API clients
│   │   └── tasks/             # Background tasks
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container
│
├── frontend/                   # Next.js frontend
│   ├── app/                   # App Router pages
│   ├── components/            # React components
│   ├── lib/                   # Utilities and API client
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript types
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   └── Dockerfile             # Frontend container
│
├── mobile/                     # Mobile app (deferred to v4.0)
│   └── README.md              # Placeholder
│
├── old/                        # Archived v2.0 code
│   ├── main.py                # CLI tool
│   ├── meta_database.py       # Old meta data
│   └── android_app/           # Kivy Android app
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # This file
│   ├── REQUIREMENTS.md        # Requirements specification
│   ├── BACKLOG.md             # Epics and User Stories
│   ├── FLOW.md                # Flow diagrams
│   └── INSTALL.md             # Installation guide
│
├── docker-compose.yml          # Development environment
├── .env.example                # Environment variables template
├── CLAUDE.md                   # AI assistant guide
└── README.md                   # Project overview
```

---

## 4. System Architecture

### High-Level Architecture (Mermaid)

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end

    subgraph "Frontend Layer"
        NextJS[Next.js 15 App Router]
        TanStack[TanStack Query]
    end

    subgraph "Backend Layer"
        FastAPI[FastAPI Application]
        Services[Service Layer]
        Core[Core Logic]
        Tasks[Background Tasks]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL 16)]
        Redis[(Redis 7)]
    end

    subgraph "External Services"
        TCGdex[TCGdex API]
        PokemonAPI[Pokemon TCG API]
        Limitless[Limitless TCG]
        PokeBeach[PokeBeach]
        RK9[RK9 Events]
        Claude[Claude AI API]
    end

    Browser --> NextJS
    NextJS --> TanStack
    TanStack --> FastAPI

    FastAPI --> Services
    Services --> Core
    Services --> PostgreSQL
    Services --> Redis

    Tasks --> PostgreSQL
    Tasks --> TCGdex
    Tasks --> PokemonAPI
    Tasks --> Limitless
    Tasks --> PokeBeach
    Tasks --> RK9

    Services --> Claude
    Services --> TCGdex
    Services --> PokemonAPI
    Services --> Limitless

    style FastAPI fill:#00d1b2
    style NextJS fill:#0070f3
    style PostgreSQL fill:#336791
    style Claude fill:#b08d57
```

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Pages   │  │Components│  │  Hooks   │  │API Client│       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┴─────────────┴─────────────┘              │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/SSE
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Routes (v1)                       │  │
│  │  /cards  /decks  /meta  /analysis  /ai  /tournaments   │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │                   Service Layer                          │  │
│  │  CardService  DeckService  MetaService  AIService       │  │
│  └────────────┬─────────────────┬─────────────────┬────────┘  │
│               │                 │                 │            │
│  ┌────────────▼─────┐  ┌────────▼────────┐  ┌────▼────────┐  │
│  │   Core Logic     │  │  Integrations   │  │   Models    │  │
│  │  - Parser        │  │  - TCGdex       │  │  - Card     │  │
│  │  - Rotation      │  │  - Claude       │  │  - Deck     │  │
│  │  - Matchup       │  │  - Limitless    │  │  - User     │  │
│  │  - Substitution  │  │  - PokeBeach    │  │  - Meta     │  │
│  └──────────────────┘  └─────────────────┘  └─────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │   PostgreSQL    │         │      Redis      │
    │   - Cards       │         │   - API Cache   │
    │   - Decks       │         │   - Session     │
    │   - Users       │         │   - Rate Limit  │
    │   - Meta        │         └─────────────────┘
    └─────────────────┘
```

---

## 5. Backend Architecture

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (api/v1/)                      │
│         HTTP Request Handling, Validation, Response         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Service Layer (services/)                  │
│           Business Logic, Orchestration, Caching            │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
│  Core Logic    │ │ Integrations│ │  Data Layer     │
│  (core/)       │ │(integrations│ │  (models/)      │
│                │ │     /)      │ │                 │
│ - deck_parser  │ │ - tcgdex    │ │ SQLAlchemy      │
│ - rotation     │ │ - claude    │ │ Models          │
│ - matchup      │ │ - limitless │ │                 │
│ - substitution │ │ - pokebeach │ │ AsyncSession    │
│ - type_chart   │ │ - rk9       │ │                 │
└────────────────┘ └─────────────┘ └─────────────────┘
```

### Directory Structure

```
backend/app/
├── main.py                          # FastAPI application
├── config.py                        # Settings (Pydantic BaseSettings)
├── database.py                      # Database session, connection pool
│
├── models/                          # SQLAlchemy ORM Models
│   ├── __init__.py
│   ├── user.py                      # User model
│   ├── card.py                      # Card model
│   ├── deck.py                      # Deck, DeckCard models
│   ├── meta.py                      # MetaDeck, MatchupData
│   ├── collection.py                # UserCollection
│   ├── battle.py                    # BattleLog, BattleAction
│   ├── news.py                      # NewsArticle
│   └── tournament.py                # Tournament, Event
│
├── schemas/                         # Pydantic Schemas (v2)
│   ├── __init__.py
│   ├── user.py                      # UserCreate, UserResponse
│   ├── card.py                      # CardResponse, CardSearch
│   ├── deck.py                      # DeckCreate, DeckResponse
│   ├── meta.py                      # MetaDeckResponse
│   ├── analysis.py                  # RotationAnalysis, MatchupAnalysis
│   ├── ai.py                        # ChatMessage, ChatResponse
│   └── common.py                    # Pagination, Language enum
│
├── api/
│   └── v1/                          # API Routes (version 1)
│       ├── __init__.py
│       ├── cards.py                 # /api/v1/cards
│       ├── decks.py                 # /api/v1/decks
│       ├── meta.py                  # /api/v1/meta
│       ├── analysis.py              # /api/v1/analysis
│       ├── ai.py                    # /api/v1/ai
│       ├── collection.py            # /api/v1/collection
│       ├── news.py                  # /api/v1/news
│       ├── tournaments.py           # /api/v1/tournaments
│       └── user.py                  # /api/v1/user
│
├── services/                        # Business Logic Services
│   ├── __init__.py
│   ├── card_service.py              # Card search, fetch, cache
│   ├── deck_service.py              # Deck CRUD, validation
│   ├── meta_service.py              # Meta deck management
│   ├── analysis_service.py          # Rotation, matchup, comparison
│   ├── ai_service.py                # Claude integration, chat, video
│   ├── collection_service.py        # User collection management
│   ├── news_service.py              # News aggregation
│   └── tournament_service.py        # Tournament data
│
├── core/                            # Core Domain Logic (pure functions)
│   ├── __init__.py
│   ├── deck_parser.py               # Parse PTCGO/TCG Live format
│   ├── rotation.py                  # Rotation impact analysis
│   ├── matchup_engine.py            # Matchup calculation
│   ├── substitution_engine.py       # Card substitution logic
│   ├── type_chart.py                # Type effectiveness
│   ├── set_codes.py                 # Set code mappings
│   ├── i18n.py                      # Bilingual string helpers
│   └── deck_validation.py           # 60-card, 4-copy rules
│
├── integrations/                    # External API Clients
│   ├── __init__.py
│   ├── tcgdex_client.py             # TCGdex API client
│   ├── pokemontcg_client.py         # Pokemon TCG API client
│   ├── limitless_client.py          # Limitless scraper/API
│   ├── pokebeach_client.py          # PokeBeach RSS/scraper
│   ├── rk9_client.py                # RK9 events scraper
│   └── claude_client.py             # Anthropic Claude API
│
└── tasks/                           # Background Tasks (Celery/FastAPI BG)
    ├── __init__.py
    ├── sync_cards.py                # Sync card database
    ├── sync_limitless.py            # Sync tournament data
    ├── sync_tournaments.py          # Sync event calendar
    ├── sync_news.py                 # Sync news feed
    └── seed_abilities.py            # Seed Pokemon abilities
```

### Dependency Injection Pattern

FastAPI uses dependency injection for database sessions and services:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Database session dependency
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Type alias for clean injection
DBSession = Annotated[AsyncSession, Depends(get_db)]

# Usage in route
@router.get("/cards/{card_id}")
async def get_card(card_id: int, db: DBSession):
    return await CardService.get_by_id(db, card_id)
```

### Async Stack

Full async implementation throughout:

- **FastAPI**: Async route handlers
- **SQLAlchemy 2.0**: Async ORM with `async_session`
- **asyncpg**: Async PostgreSQL driver
- **httpx**: Async HTTP client for external APIs
- **Uvicorn**: ASGI server with async workers

Example async service:

```python
class CardService:
    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        lang: Language = Language.EN
    ) -> list[Card]:
        stmt = select(Card).where(
            Card.name_en.ilike(f"%{query}%")
        ).options(selectinload(Card.abilities))

        result = await db.execute(stmt)
        return result.scalars().all()
```

---

## 6. Frontend Architecture

### Next.js App Router Structure

```
frontend/app/
├── layout.tsx                       # Root layout
├── page.tsx                         # Home page
├── globals.css                      # Global styles
│
├── cards/
│   ├── page.tsx                     # Card search page
│   └── [id]/page.tsx                # Card detail page
│
├── decks/
│   ├── page.tsx                     # My decks list
│   ├── new/page.tsx                 # New deck page
│   ├── import/page.tsx              # Import deck page
│   ├── [id]/
│   │   ├── page.tsx                 # Deck detail
│   │   ├── edit/page.tsx            # Deck editor
│   │   └── analysis/page.tsx        # Deck analysis
│   └── builder/page.tsx             # Deck builder
│
├── meta/
│   ├── page.tsx                     # Meta overview
│   ├── [deckId]/page.tsx            # Meta deck detail
│   └── matchups/page.tsx            # Matchup matrix
│
├── analysis/
│   ├── rotation/page.tsx            # Rotation checker
│   └── compare/page.tsx             # Deck comparison
│
├── collection/
│   ├── page.tsx                     # Collection manager
│   └── import/page.tsx              # Collection import
│
├── battle/
│   ├── page.tsx                     # Battle logs list
│   ├── new/page.tsx                 # New battle log
│   └── [id]/page.tsx                # Battle analysis
│
├── ai/
│   ├── chat/page.tsx                # AI chat interface
│   └── video/page.tsx               # Video analysis
│
├── news/
│   └── page.tsx                     # News feed
│
├── tournaments/
│   ├── page.tsx                     # Tournament list
│   ├── calendar/page.tsx            # Event calendar
│   └── [id]/page.tsx                # Tournament detail
│
└── profile/
    └── page.tsx                     # User profile
```

### Component Organization

```
frontend/components/
├── ui/                              # shadcn/ui components
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── table.tsx
│   └── ...
│
├── layout/                          # Layout components
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── Footer.tsx
│   └── LanguageToggle.tsx
│
├── deck/                            # Deck-related components
│   ├── DeckCard.tsx                 # Deck preview card
│   ├── DeckList.tsx                 # Deck card list
│   ├── DeckStats.tsx                # Deck statistics
│   ├── DeckBuilder.tsx              # Deck builder UI
│   └── DeckImporter.tsx             # Deck import form
│
├── cards/                           # Card-related components
│   ├── CardImage.tsx                # Card image display
│   ├── CardSearchBar.tsx            # Search input
│   ├── CardGrid.tsx                 # Card grid layout
│   ├── CardFilter.tsx               # Filter controls
│   └── CardDetail.tsx               # Card detail view
│
├── meta/                            # Meta components
│   ├── MetaDeckCard.tsx             # Meta deck card
│   ├── MatchupMatrix.tsx            # Matchup table
│   └── TierList.tsx                 # Tier list display
│
├── analysis/                        # Analysis components
│   ├── RotationReport.tsx           # Rotation analysis
│   ├── MatchupAnalysis.tsx          # Matchup breakdown
│   ├── ComparisonTable.tsx          # Deck comparison
│   └── SubstitutionSuggestions.tsx  # Card suggestions
│
├── battle/                          # Battle log components
│   ├── BattleLogCard.tsx            # Battle log preview
│   ├── TurnTimeline.tsx             # Turn-by-turn timeline
│   └── ActionLog.tsx                # Action list
│
├── chat/                            # AI chat components
│   ├── ChatInterface.tsx            # Chat UI
│   ├── MessageBubble.tsx            # Message display
│   └── StreamingIndicator.tsx       # Loading state
│
├── collection/                      # Collection components
│   ├── CollectionGrid.tsx           # Card grid with counts
│   ├── SetProgress.tsx              # Set completion
│   └── WantlistManager.tsx          # Wantlist UI
│
└── tournament/                      # Tournament components
    ├── TournamentCard.tsx           # Tournament preview
    ├── EventCalendar.tsx            # Calendar view
    └── StandingTable.tsx            # Standings table
```

### Hooks Pattern

Custom React hooks using TanStack Query:

```typescript
// hooks/useCards.ts
export function useCardSearch(query: string, filters: CardFilters) {
  return useQuery({
    queryKey: ['cards', 'search', query, filters],
    queryFn: () => api.cards.search(query, filters),
    enabled: query.length > 0,
  })
}

// hooks/useDecks.ts
export function useUserDecks() {
  return useQuery({
    queryKey: ['decks'],
    queryFn: () => api.decks.list(),
  })
}

export function useDeckMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.decks.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] })
    },
  })
}

// hooks/useAIChat.ts
export function useAIChat(deckId?: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([])

  const sendMessage = async (content: string) => {
    // SSE streaming implementation
    const eventSource = api.ai.streamChat(content, deckId)
    // Handle streaming response
  }

  return { messages, sendMessage }
}
```

### API Client

Axios-based API client with TypeScript:

```typescript
// lib/api.ts
const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
})

export const api = {
  cards: {
    search: (query: string, filters: CardFilters) =>
      axiosInstance.get<CardResponse[]>('/api/v1/cards/search', {
        params: { q: query, ...filters },
      }),
    getById: (id: number) =>
      axiosInstance.get<CardResponse>(`/api/v1/cards/${id}`),
  },

  decks: {
    list: () => axiosInstance.get<DeckResponse[]>('/api/v1/decks'),
    create: (data: DeckCreate) =>
      axiosInstance.post<DeckResponse>('/api/v1/decks', data),
    update: (id: number, data: DeckUpdate) =>
      axiosInstance.put<DeckResponse>(`/api/v1/decks/${id}`, data),
    delete: (id: number) =>
      axiosInstance.delete(`/api/v1/decks/${id}`),
    analyze: (id: number) =>
      axiosInstance.get<RotationAnalysis>(`/api/v1/decks/${id}/analyze`),
  },

  ai: {
    streamChat: (message: string, deckId?: number) => {
      // SSE implementation
      return new EventSource(
        `/api/v1/ai/chat?message=${encodeURIComponent(message)}&deck_id=${deckId}`
      )
    },
  },
}
```

---

## 7. Data Flow Diagrams

### Card Search Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Cache
    participant TCGdex
    participant DB

    User->>Frontend: Enter search query
    Frontend->>Frontend: Debounce input (300ms)
    Frontend->>Backend: GET /api/v1/cards/search?q=pikachu
    Backend->>Cache: Check Redis cache

    alt Cache Hit
        Cache-->>Backend: Return cached results
        Backend-->>Frontend: CardResponse[]
    else Cache Miss
        Backend->>DB: Query local database

        alt Found in DB
            DB-->>Backend: Card records
            Backend->>Cache: Store in Redis (TTL: 1h)
            Backend-->>Frontend: CardResponse[]
        else Not in DB
            Backend->>TCGdex: GET /v2/en/cards?name=pikachu
            TCGdex-->>Backend: API response
            Backend->>DB: Insert/Update cards
            Backend->>Cache: Store in Redis (TTL: 1h)
            Backend-->>Frontend: CardResponse[]
        end
    end

    Frontend->>Frontend: Update UI with results
    Frontend-->>User: Display cards
```

### AI Chat Flow (SSE Streaming)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Claude
    participant DB

    User->>Frontend: Send chat message
    Frontend->>Backend: POST /api/v1/ai/chat (SSE)
    Backend->>DB: Load deck context (if deck_id)
    DB-->>Backend: Deck data

    Backend->>Backend: Build prompt with context
    Backend->>Claude: POST /v1/messages (stream=true)

    loop Stream chunks
        Claude-->>Backend: Content delta
        Backend-->>Frontend: SSE event: data
        Frontend->>Frontend: Append to message
        Frontend-->>User: Update UI incrementally
    end

    Claude-->>Backend: Stream complete
    Backend->>DB: Save conversation
    Backend-->>Frontend: SSE event: done
    Frontend-->>User: Final message displayed
```

### Deck Import Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Parser
    participant CardAPI
    participant DB

    User->>Frontend: Paste deck text
    Frontend->>Backend: POST /api/v1/decks/import
    Backend->>Parser: parse_deck(text)

    loop For each card line
        Parser->>Parser: Extract name, set, number
        Parser->>CardAPI: Resolve card identity

        alt Card in cache/DB
            CardAPI-->>Parser: Card object
        else Fetch from API
            CardAPI->>TCGdex: GET /v2/en/cards/{set}/{number}
            TCGdex-->>CardAPI: Card data
            CardAPI->>DB: Cache card
            CardAPI-->>Parser: Card object
        end
    end

    Parser-->>Backend: Deck object (60 cards)
    Backend->>Backend: Validate deck (60 cards, 4-copy rule)

    alt Validation success
        Backend->>DB: INSERT deck + deck_cards
        DB-->>Backend: Deck ID
        Backend-->>Frontend: DeckResponse (201)
        Frontend-->>User: Redirect to deck detail
    else Validation error
        Backend-->>Frontend: ValidationError (400)
        Frontend-->>User: Show error message
    end
```

### Battle Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant VideoProcessor
    participant Claude
    participant DB

    User->>Frontend: Upload match video
    Frontend->>Backend: POST /api/v1/battles/analyze (multipart)
    Backend->>Backend: Save video to storage

    Backend->>VideoProcessor: Extract frames (30s intervals)
    VideoProcessor-->>Backend: Frame images

    loop For each frame
        Backend->>Claude: Analyze frame (vision)
        Claude-->>Backend: Game state detection
        Backend->>Backend: Parse actions, cards, HP
    end

    Backend->>Claude: Generate insights summary
    Claude-->>Backend: Strategic analysis

    Backend->>DB: Save battle log + actions
    DB-->>Backend: Battle ID

    Backend-->>Frontend: BattleAnalysis (201)
    Frontend-->>User: Show turn timeline + insights
```

---

## 8. External API Strategy

### API Priority & Fallback

```
Primary: TCGdex API
    ├─ Pros: 10+ languages, comprehensive, free
    ├─ Cons: Rate limits (unknown), no official SLA
    └─ Fallback on: 429, 5xx errors, timeout
           ↓
Secondary: Pokemon TCG API
    ├─ Pros: Official, reliable, well-documented
    ├─ Cons: English only, requires API key for heavy use
    └─ Fallback on: N/A (manual intervention)
```

### Caching Strategy

| Data Type | Cache Layer | TTL | Invalidation |
|-----------|-------------|-----|--------------|
| Card data | Redis + PostgreSQL | 24h | Manual sync task |
| Tournament data | PostgreSQL | 1h | Background sync (hourly) |
| News articles | PostgreSQL | 30m | Background sync (30m) |
| Meta snapshots | PostgreSQL | N/A | Manual update |
| API responses | Redis | 1h | TTL expiration |

### Rate Limiting

```python
# integrations/tcgdex_client.py
class TCGdexClient:
    def __init__(self):
        self.limiter = AsyncLimiter(max_rate=100, time_period=60)

    async def fetch_card(self, set_id: str, card_number: str):
        async with self.limiter:
            try:
                response = await httpx_client.get(
                    f"https://api.tcgdex.net/v2/en/cards/{set_id}/{card_number}",
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Fallback to Pokemon TCG API
                    return await pokemon_api_client.fetch_card(...)
                raise
```

### API Client Architecture

```python
# Base client with retry logic
class BaseAPIClient:
    async def request(self, method: str, url: str, **kwargs):
        for attempt in range(3):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise

# Concrete implementations
class TCGdexClient(BaseAPIClient): ...
class PokemonTCGClient(BaseAPIClient): ...
class LimitlessClient(BaseAPIClient): ...
```

---

## 9. Key Design Decisions

### 1. Bilingual First (name_en / name_pt)

**Decision**: Store both English and Portuguese names in all database models

**Rationale**:
- Primary user base is English and Portuguese speakers
- Avoids runtime translation lookups
- Enables efficient filtering in both languages
- Simplifies API responses (always include both)

**Implementation**:
```python
class Card(Base):
    __tablename__ = "cards"

    name_en = Column(String, nullable=False, index=True)
    name_pt = Column(String, nullable=False, index=True)

    @property
    def name(self, lang: Language = Language.EN) -> str:
        return self.name_en if lang == Language.EN else self.name_pt
```

### 2. Hardcoded user_id = 1 (Auth Planned)

**Decision**: Use hardcoded `user_id = 1` for all operations in v3.0

**Rationale**:
- Auth system is planned for v3.1
- Avoids blocking development on auth implementation
- Database schema already supports multiple users
- Easy migration path (just add auth middleware)

**Implementation**:
```python
# Current (v3.0)
CURRENT_USER_ID = 1

@router.get("/decks")
async def list_decks(db: DBSession):
    return await DeckService.get_user_decks(db, user_id=CURRENT_USER_ID)

# Future (v3.1)
@router.get("/decks")
async def list_decks(db: DBSession, user: User = Depends(get_current_user)):
    return await DeckService.get_user_decks(db, user_id=user.id)
```

### 3. SSE for AI Streaming

**Decision**: Use Server-Sent Events for streaming AI responses

**Rationale**:
- Native browser support (EventSource API)
- Simpler than WebSockets for unidirectional streaming
- Works with standard HTTP infrastructure
- Perfect for Claude API streaming

**Implementation**:
```python
from sse_starlette.sse import EventSourceResponse

@router.get("/ai/chat")
async def chat_stream(message: str, deck_id: Optional[int] = None):
    async def event_generator():
        async for chunk in claude_client.stream_chat(message):
            yield {
                "event": "message",
                "data": json.dumps({"content": chunk})
            }
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
```

### 4. selectinload for Eager Loading

**Decision**: Use SQLAlchemy `selectinload()` for relationships

**Rationale**:
- Avoids N+1 query problem
- Works with async sessions
- More efficient than `joinedload` for one-to-many
- Explicit control over loaded data

**Implementation**:
```python
from sqlalchemy.orm import selectinload

async def get_deck_with_cards(db: AsyncSession, deck_id: int):
    stmt = (
        select(Deck)
        .where(Deck.id == deck_id)
        .options(
            selectinload(Deck.deck_cards).selectinload(DeckCard.card)
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

### 5. Pydantic v2 with from_attributes

**Decision**: Use Pydantic v2 with `model_config = ConfigDict(from_attributes=True)`

**Rationale**:
- Better performance than v1
- `from_attributes` replaces `orm_mode`
- Native async validator support
- Improved JSON schema generation

**Implementation**:
```python
from pydantic import BaseModel, ConfigDict

class DeckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int
    cards: list[CardInDeck]

    # Works with SQLAlchemy models
    # deck = Deck(...) -> DeckResponse.model_validate(deck)
```

### 6. Modular Core Logic

**Decision**: Separate pure domain logic from services

**Rationale**:
- Testable without database/API dependencies
- Reusable across different interfaces (CLI, API, mobile)
- Clear separation of concerns
- Easy to port logic to other languages if needed

**Example**:
```python
# core/deck_parser.py (pure function)
def parse_deck(text: str) -> ParsedDeck:
    # No DB, no API, just logic
    lines = text.strip().split('\n')
    cards = []
    for line in lines:
        if match := CARD_LINE_REGEX.match(line):
            cards.append(parse_card_line(match))
    return ParsedDeck(cards=cards)

# services/deck_service.py (orchestration)
async def import_deck(db: AsyncSession, text: str):
    parsed = parse_deck(text)  # Pure logic
    cards = await resolve_cards(db, parsed.cards)  # I/O
    deck = await create_deck(db, cards)  # I/O
    return deck
```

---

## 10. Security Considerations

### CORS Configuration

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://tcgtool.app"     # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Input Validation

All inputs validated with Pydantic schemas:

```python
from pydantic import BaseModel, Field, validator

class DeckCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: bool = False
    cards: list[DeckCardInput]

    @validator('cards')
    def validate_card_count(cls, v):
        if len(v) != 60:
            raise ValueError('Deck must have exactly 60 cards')
        return v
```

### API Key Management

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # External APIs
    CLAUDE_API_KEY: str
    POKEMON_TCG_API_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str  # For future auth

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**Environment Variables** (never committed):
```bash
# .env (not in git)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/tcg_tool
CLAUDE_API_KEY=sk-ant-...
SECRET_KEY=random-secret-key
```

### SQL Injection Prevention

SQLAlchemy ORM prevents SQL injection:

```python
# Safe (parameterized)
stmt = select(Card).where(Card.name_en.ilike(f"%{user_input}%"))

# NEVER do this (vulnerable)
# db.execute(f"SELECT * FROM cards WHERE name LIKE '%{user_input}%'")
```

### Data Sanitization

```python
# schemas/deck.py
from pydantic import field_validator
import bleach

class DeckCreate(BaseModel):
    description: Optional[str] = None

    @field_validator('description')
    def sanitize_html(cls, v):
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v
```

---

## 11. Future Roadmap

### v3.1 - Authentication & Authorization

**Timeline**: Q2 2026

**Features**:
- User registration and login
- JWT-based authentication
- Password hashing (bcrypt)
- Protected routes (deck privacy)
- Email verification
- Password reset flow

**Tech Stack**:
- FastAPI Security utilities
- python-jose (JWT)
- passlib (password hashing)
- FastAPI-Mail (email)

### v3.2 - Redis Caching Optimization

**Timeline**: Q2 2026

**Features**:
- Distributed caching for API responses
- Session management
- Rate limiting storage
- Real-time deck view counts
- Popular searches tracking

**Tech Stack**:
- redis-py (async)
- FastAPI-Cache2
- Custom cache decorators

### v3.3 - Mobile PWA

**Timeline**: Q3 2026

**Features**:
- Progressive Web App (PWA)
- Offline support
- Push notifications
- Add to home screen
- Camera integration (card scanning)
- Mobile-optimized UI

**Tech Stack**:
- Next.js PWA plugin
- Workbox (service workers)
- IndexedDB (offline storage)

### v3.4 - Video Analysis Enhancement

**Timeline**: Q3 2026

**Features**:
- Automatic card recognition (OCR)
- Turn detection and segmentation
- Probability calculator integration
- Multi-game analysis
- Export to video editor

**Tech Stack**:
- Claude Vision API
- OpenCV (video processing)
- Tesseract OCR
- FFmpeg (video manipulation)

### v4.0 - Native Mobile App

**Timeline**: Q4 2026

**Features**:
- React Native mobile app
- Native camera integration
- Offline mode with sync
- AR card preview
- NFC support (future cards)

**Tech Stack**:
- React Native
- Expo
- React Native Camera
- AsyncStorage
- Background sync

### Future Considerations

- **Blockchain Integration**: NFT card ownership tracking
- **Marketplace**: Card trading platform
- **Tournament Management**: Organize local events
- **Live Streaming**: Integrate with Twitch/YouTube
- **Social Features**: Follow players, share decks
- **Premium Tier**: Advanced analytics, AI features

---

## Appendix A: Database Schema

### Core Tables

```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cards
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    tcgdex_id VARCHAR(50) UNIQUE,
    name_en VARCHAR(255) NOT NULL,
    name_pt VARCHAR(255) NOT NULL,
    card_type VARCHAR(20) NOT NULL,
    supertype VARCHAR(20),
    subtype VARCHAR(50),
    set_id VARCHAR(20),
    set_name_en VARCHAR(100),
    set_name_pt VARCHAR(100),
    regulation_mark VARCHAR(2),
    image_url TEXT,
    hp INTEGER,
    energy_types JSONB,
    retreat_cost INTEGER,
    rarity VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cards_name_en ON cards (name_en);
CREATE INDEX idx_cards_name_pt ON cards (name_pt);
CREATE INDEX idx_cards_set_id ON cards (set_id);
CREATE INDEX idx_cards_regulation_mark ON cards (regulation_mark);

-- Decks
CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    archetype VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Deck Cards (junction table)
CREATE TABLE deck_cards (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity >= 1 AND quantity <= 4),
    UNIQUE (deck_id, card_id)
);

-- Meta Decks
CREATE TABLE meta_decks (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    name_pt VARCHAR(100) NOT NULL,
    archetype VARCHAR(100),
    tier VARCHAR(10),
    win_rate DECIMAL(5,2),
    play_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Matchup Data
CREATE TABLE matchup_data (
    id SERIAL PRIMARY KEY,
    deck_a_id INTEGER REFERENCES meta_decks(id),
    deck_b_id INTEGER REFERENCES meta_decks(id),
    win_rate_a DECIMAL(5,2),
    sample_size INTEGER,
    UNIQUE (deck_a_id, deck_b_id)
);
```

---

## Appendix B: API Endpoints Summary

### Cards API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cards` | List all cards |
| GET | `/api/v1/cards/search` | Search cards |
| GET | `/api/v1/cards/{id}` | Get card by ID |
| GET | `/api/v1/cards/sets` | List all sets |
| GET | `/api/v1/cards/sets/{set_id}` | Get cards in set |

### Decks API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/decks` | List user decks |
| POST | `/api/v1/decks` | Create new deck |
| GET | `/api/v1/decks/{id}` | Get deck detail |
| PUT | `/api/v1/decks/{id}` | Update deck |
| DELETE | `/api/v1/decks/{id}` | Delete deck |
| POST | `/api/v1/decks/import` | Import deck from text |
| GET | `/api/v1/decks/{id}/export` | Export deck to PTCGO format |

### Analysis API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analysis/rotation` | Analyze rotation impact |
| POST | `/api/v1/analysis/matchup` | Calculate matchup |
| POST | `/api/v1/analysis/compare` | Compare two decks |
| POST | `/api/v1/analysis/substitution` | Get card substitutions |

### AI API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ai/chat` | Chat with AI (SSE stream) |
| POST | `/api/v1/ai/video` | Analyze match video |
| POST | `/api/v1/ai/recommend` | Get deck recommendations |

### Meta API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/meta/decks` | List meta decks |
| GET | `/api/v1/meta/decks/{id}` | Get meta deck detail |
| GET | `/api/v1/meta/matchups` | Get matchup matrix |
| GET | `/api/v1/meta/tiers` | Get tier list |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-15 | Bruno Strumendo | Initial architecture document |

---

**End of Document**
