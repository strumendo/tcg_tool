# Pokemon TCG Analysis Platform

A comprehensive platform for Pokemon TCG deck analysis, video management, and competitive insights powered by AI.

## Features

- **Deck Builder** - Create, edit, and manage Pokemon TCG decks
- **Card Collection** - Browse cards with multilingual support (10+ languages via TCGdex)
- **Video Upload** - Upload match videos from smartphones
- **Video Analysis** - AI-powered gameplay analysis using Claude
- **Match Import** - Import matches from Pokemon TCG Live via OCR
- **Meta Analysis** - Compare decks against top 10 meta with win rate predictions
- **YouTube Channels** - Curate your favorite TCG content creators
- **Dashboard** - Real-time stats, activity feed, and performance analytics
- **User Authentication** - Secure JWT-based auth with profile management
- **Tournament Tracker** - Track tournaments, rounds, standings, and championship points
- **AI Coach** - Personalized deck analysis, matchup advice, and improvement plans
- **Export & Share** - Export decks (PTCGO, Limitless, JSON) and share stats socially

## Tech Stack

### Backend
- Python 3.12+
- FastAPI (async REST API)
- PostgreSQL (database)
- Redis (caching)
- MinIO (S3-compatible storage)
- SQLAlchemy (async ORM)
- Anthropic Claude API (AI analysis)
- TCGdex SDK (multilingual card data)
- Pokemon TCG SDK (card data fallback)

### Frontend
- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- TanStack Query
- Zustand (state management)

### Infrastructure
- Docker & Docker Compose
- Tesseract OCR
- FFmpeg (video processing)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Anthropic API key for AI features

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd tcg_tool
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
```

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Importing Data

### Cards

You can import cards from JSON or CSV files:

```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/cards/import" \
  -F "file=@cards.json"
```

### Meta Data

Import meta data from LimitlessTCG or similar sources:

```bash
curl -X POST "http://localhost:8000/api/v1/meta/import/file" \
  -F "file=@meta.json" \
  -F "name=LAIC 2024"
```

### Deck Import

Import decks in PTCGO format:

```
4 Charizard ex SVI 125
3 Charmeleon SVI 124
4 Charmander SVI 123
...
```

## API Endpoints

### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/full` - Full system status

### Cards
- `GET /api/v1/cards` - List cards
- `POST /api/v1/cards/import` - Import cards from file
- `GET /api/v1/cards/sets/` - List card sets
- `GET /api/v1/cards/api/search?lang=en` - Search cards (multilingual)
- `GET /api/v1/cards/languages` - Get supported languages

### Decks
- `GET /api/v1/decks` - List decks
- `POST /api/v1/decks` - Create deck
- `POST /api/v1/decks/import/file` - Import deck from file

### Videos
- `GET /api/v1/videos` - List videos
- `POST /api/v1/videos` - Upload video
- `POST /api/v1/videos/{id}/analyze` - Analyze with AI

### Matches
- `GET /api/v1/matches` - List matches
- `POST /api/v1/matches/import/ocr` - Import from screenshot

### Meta
- `GET /api/v1/meta/top10` - Get top 10 decks
- `POST /api/v1/meta/compare` - Compare deck to meta

### YouTube
- `GET /api/v1/youtube-channels` - List channels
- `POST /api/v1/youtube-channels/from-url` - Add channel from URL

### Dashboard
- `GET /api/v1/dashboard/stats` - Aggregated statistics
- `GET /api/v1/dashboard/activity` - Recent activity feed
- `GET /api/v1/dashboard/matchup-summary` - Win rates by archetype
- `GET /api/v1/dashboard/top-decks` - Top performing decks

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login/json` - Login (JSON body)
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update profile
- `POST /api/v1/auth/change-password` - Change password

### Tournaments
- `GET /api/v1/tournaments` - List tournaments
- `POST /api/v1/tournaments` - Create tournament
- `GET /api/v1/tournaments/{id}` - Get tournament details
- `POST /api/v1/tournaments/{id}/rounds` - Add round
- `POST /api/v1/tournaments/{id}/complete` - Mark completed
- `GET /api/v1/tournaments/stats` - Tournament statistics

### AI Coaching
- `GET /api/v1/coaching/deck/{id}` - Analyze deck with AI
- `GET /api/v1/coaching/matchup` - Get matchup advice
- `GET /api/v1/coaching/improvement-plan` - Personalized improvement plan
- `GET /api/v1/coaching/quick-tips` - General gameplay tips

### Export & Sharing
- `GET /api/v1/export/deck/{id}?format=ptcgo` - Export deck (text/ptcgo/json/limitless)
- `GET /api/v1/export/tournament/{id}` - Export tournament report
- `GET /api/v1/export/matches` - Export match history (json/csv)
- `GET /api/v1/export/stats` - Export all stats
- `GET /api/v1/export/share/deck/{id}` - Get deck share data
- `GET /api/v1/export/share/stats` - Get stats share data

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI   │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend   │     │   + Redis   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │ Claude  │ │  MinIO  │ │Tesseract│
        │   API   │ │ Storage │ │   OCR   │
        └─────────┘ └─────────┘ └─────────┘
```

## Module Status

| Module | Status | Description |
|--------|--------|-------------|
| Core Infrastructure | ✅ Complete | FastAPI, PostgreSQL, Redis, MinIO |
| Card Collection | ✅ Complete | Dual-API (TCGdex + Pokemon TCG) with 10+ languages |
| Deck Builder | ✅ Complete | Create, import (PTCGO format), manage decks |
| Deck Analysis (LLM) | ✅ Complete | AI-powered deck insights |
| Match Import (OCR) | ✅ Complete | Import from Pokemon TCG Live screenshots |
| Video Upload | ✅ Complete | Smartphone video upload with streaming |
| Video Analysis (AI) | ✅ Complete | Claude-powered gameplay analysis |
| YouTube Manager | ✅ Complete | Track favorite TCG content creators |
| Meta Comparison | ✅ Complete | Compare decks to top 10 meta |
| Dashboard | ✅ Complete | Stats, activity feed, performance analytics |
| User Authentication | ✅ Complete | JWT auth, profiles, preferences |
| Tournament Tracker | ✅ Complete | Tournaments, rounds, standings, CP tracking |
| AI Coaching | ✅ Complete | Deck analysis, matchup advice, improvement plans |
| Export & Sharing | ✅ Complete | Multi-format exports, social sharing |

## Running Locally (Step by Step)

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd tcg_tool

# 2. Create environment file
cp .env.example .env

# 3. Edit .env and add your API key
nano .env
# Add: ANTHROPIC_API_KEY=your-key-here

# 4. Start all services
docker-compose up -d

# 5. Wait for services to be ready (about 30 seconds)
docker-compose logs -f

# 6. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/tcg_db"
export REDIS_URL="redis://localhost:6379"
export ANTHROPIC_API_KEY="your-key-here"

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
# 1. Navigate to frontend (in a new terminal)
cd frontend

# 2. Install dependencies
npm install

# 3. Set up environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 4. Start development server
npm run dev
```

#### Required Services

Make sure these are running locally:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **MinIO** on port 9000 (optional, for video storage)

### Verifying Installation

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend
open http://localhost:3000
```

## Supported Languages (Card Data)

| Code | Language |
|------|----------|
| en | English |
| fr | French |
| de | German |
| es | Spanish |
| it | Italian |
| pt | Portuguese |
| ja | Japanese |
| zh-tw | Traditional Chinese |
| id | Indonesian |
| th | Thai |

## License

MIT
