# Pokemon TCG Analysis Platform

A comprehensive platform for Pokemon TCG deck analysis, video management, and competitive insights powered by AI.

## Features

- **Deck Builder** - Create, edit, and manage Pokemon TCG decks
- **Card Collection** - Browse and import Pokemon TCG card database
- **Video Upload** - Upload match videos from smartphones
- **Video Analysis** - AI-powered gameplay analysis using Claude
- **Match Import** - Import matches from Pokemon TCG Live via OCR
- **Meta Analysis** - Compare decks against top 10 meta with win rate predictions
- **YouTube Channels** - Curate your favorite TCG content creators

## Tech Stack

### Backend
- Python 3.12+
- FastAPI (async REST API)
- PostgreSQL (database)
- Redis (caching)
- MinIO (S3-compatible storage)
- SQLAlchemy (async ORM)
- Anthropic Claude API (AI analysis)

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

| Module | Status |
|--------|--------|
| Core Infrastructure | ✅ Complete |
| Card Collection | ✅ Complete |
| Deck Builder | ✅ Complete |
| Deck Analysis (LLM) | ✅ Complete |
| Match Import (OCR) | ✅ Complete |
| Video Upload | ✅ Complete |
| Video Analysis (AI) | ✅ Complete |
| YouTube Manager | ✅ Complete |
| Meta Comparison | ✅ Complete |

## License

MIT
