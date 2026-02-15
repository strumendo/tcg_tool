# CLAUDE.md - AI Assistant Guide for TCG Tool v3.0

## Git Configuration (IMPORTANT)

**All commits must use the following credentials:**

```bash
git config user.name "Bruno Strumendo"
git config user.email "strumendo@gmail.com"
```

**Always configure before making commits.**

### Branch Naming Convention

```
{issue_number}/{branch-name}
```

Example: `44/phase-7-battles-simulation`

### Commit Messages

- Write in Portuguese
- End with `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

---

## Project Overview

**TCG Tool v3.0** is a full-stack Pokemon Trading Card Game deck analysis platform with bilingual support (English/Portuguese).

### Architecture

- **Backend**: Python FastAPI + SQLAlchemy 2.0 async + PostgreSQL 16 + Alembic + Pydantic v2
- **Frontend**: Next.js 15 App Router + React 19 + TypeScript + Tailwind CSS + TanStack Query
- **AI**: Claude API (Anthropic) via `app.integrations.claude_client`
- **Cache**: Redis 7
- **Infrastructure**: Docker Compose (PostgreSQL + Redis + Backend + Frontend)

### Monorepo Structure

```
tcg_tool/
├── backend/           # FastAPI backend (80+ Python files)
│   └── app/
│       ├── api/v1/    # Route handlers (11 modules)
│       ├── core/      # Pure domain logic (deck_parser, rotation, matchup_engine, etc.)
│       ├── models/    # SQLAlchemy ORM (17 tables)
│       ├── schemas/   # Pydantic v2 request/response schemas
│       ├── services/  # Business logic layer
│       ├── integrations/ # External API clients
│       ├── tasks/     # Background sync tasks
│       └── db/        # Session factory, seed data
├── frontend/          # Next.js 15 frontend (55+ TS/TSX files)
│   └── src/
│       ├── app/       # 20 pages (App Router)
│       ├── components/ # 24+ React components
│       ├── hooks/     # TanStack Query hooks
│       └── lib/       # api.ts, types.ts, constants.ts
├── docs/              # Documentation
├── old/               # Archived v2.0 code
└── docker-compose.yml
```

---

## Key Patterns

### Backend

- **Import paths**: Use `app.xxx` (NOT `backend.app.xxx`) - app runs from `backend/` dir
- **DB dependency**: `DBSession = Annotated[AsyncSession, Depends(get_db)]`
- **User scope**: `user_id = 1` hardcoded (auth not yet implemented)
- **ORM schemas**: Pydantic v2 with `ConfigDict(from_attributes=True)`
- **Eager loading**: `selectinload` for relationships in services
- **Async stack**: FastAPI + SQLAlchemy async + asyncpg + httpx

### Frontend

- **Data fetching**: TanStack Query hooks (useDecks, useCards, useMeta, etc.)
- **API client**: Axios instance in `lib/api.ts`
- **UI text**: Portuguese (Brazilian user)
- **Bilingual data**: `name_en`/`name_pt` pattern throughout
- **AI streaming**: SSE via fetch/ReadableStream with POST fallback

### External API Strategy

| API | Role | URL |
|-----|------|-----|
| TCGdex | Primary card data | `https://api.tcgdex.net/v2` |
| Pokemon TCG API | Fallback | `https://api.pokemontcg.io/v2` |
| Limitless TCG | Tournament stats | `https://limitlesstcg.com` |
| PokeBeach | News RSS | `https://pokebeach.com` |
| RK9 | Tournament calendar | `https://rk9.gg/events/pokemon` |

---

## API Endpoints (50+)

All routes under `/api/v1`:

| Resource | Endpoints |
|----------|-----------|
| `/cards` | Search, get by ID, alternatives, abilities, usage stats |
| `/decks` | CRUD, import (PTCGO), export (TCG Live), missing cards |
| `/meta` | Meta decks, matchups, tiers |
| `/analysis` | Rotation, compare, matchup, substitutions |
| `/battles` | CRUD, AI analysis |
| `/chat` | Message (POST), stream (SSE) |
| `/stats` | Card usage, deck usage, user stats, battle stats |
| `/collection` | CRUD, missing per deck |
| `/suggestions` | AI card swap suggestions |
| `/simulation` | Play sequence simulation |
| `/tournaments` | Calendar, news feed |

See [docs/API.md](docs/API.md) for full reference.

---

## Database (17 tables)

Core: `users`, `cards`, `card_sets`, `card_abilities`, `card_attacks`, `card_functions`
Decks: `decks`, `deck_cards`
Meta: `meta_decks`, `meta_deck_cards`, `meta_matchups`
Battles: `battles`, `battle_actions`
Collection: `user_collection`
Stats: `card_usage_stats`, `deck_usage_stats`
External: `tournaments`, `news_articles`

See [docs/DATABASE.md](docs/DATABASE.md) for full schema.

---

## Running the Project

### With Docker

```bash
docker-compose up -d
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Development

```bash
# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Data Sync Tasks

```bash
python -m app.tasks.sync_cards       # Sync cards from TCGdex
python -m app.tasks.sync_limitless   # Sync Limitless stats
python -m app.tasks.sync_tournaments # Sync RK9 tournaments
python -m app.tasks.sync_news        # Sync PokeBeach news
python -m app.tasks.seed_abilities   # Seed ability categories
```

---

## Regulation Mark System

| Mark | Status | Sets |
|------|--------|------|
| G | Rotating Mar 2026 | SVI, PAL, OBF, MEW, PAR, PAF |
| H | Legal | TEF, TWM, SFA, SCR, SSP |
| I | Legal | PRE, JTG, ASC, DRI, MEV |
| F or earlier | Already illegal | Sword & Shield era |

Basic energies are ALWAYS legal regardless of set.

---

## Documentation (Bilingual: EN + PT-BR)

| Document | English | Portugues |
|----------|---------|-----------|
| Architecture | [ARCHITECTURE.md](docs/ARCHITECTURE.md) | [ARCHITECTURE_PT.md](docs/ARCHITECTURE_PT.md) |
| API Reference | [API.md](docs/API.md) | [API_PT.md](docs/API_PT.md) |
| Database Schema | [DATABASE.md](docs/DATABASE.md) | [DATABASE_PT.md](docs/DATABASE_PT.md) |
| Deployment | [DEPLOY.md](docs/DEPLOY.md) | [DEPLOY_PT.md](docs/DEPLOY_PT.md) |
| User Guide | [USER_GUIDE_EN.md](docs/USER_GUIDE_EN.md) | [USER_GUIDE.md](docs/USER_GUIDE.md) |

---

## Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Foundation | COMPLETE | Models, schemas, services, routes, Alembic, seed |
| 2. Deck Management | COMPLETE | Deck pages, import/export, card grid |
| 3. Analysis Engine | COMPLETE | Rotation, comparison, substitution, meta/tier views |
| 4. Card Intelligence | COMPLETE | Sync tasks, Limitless scraper, card detail page |
| 5. Collection | COMPLETE | Collection grid, missing cards, add modal |
| 6. AI Chatbot | COMPLETE | Streaming SSE, chat components, deck context |
| 7. Battles/Simulation | COMPLETE | Battle recording, AI analysis, stats dashboard |
| 8. Mobile App | COMPLETE | Kivy restructured with API client, offline cache |
| 9. Tournaments/News | COMPLETE | RK9 scraper, PokeBeach RSS, calendar/news pages |
| 10. Documentation | COMPLETE | Architecture, API, Database, Deploy, User Guide |
