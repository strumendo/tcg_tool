# DEPLOY.md - TCG Tool v3.0 Deployment Guide

**Author:** Bruno Strumendo
**Last Updated:** 2026-02-15

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Manual Setup (Development)](#manual-setup-development)
4. [Environment Variables](#environment-variables)
5. [Database Setup](#database-setup)
6. [Data Sync Tasks](#data-sync-tasks)
7. [Docker Compose Services](#docker-compose-services)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying TCG Tool v3.0, ensure you have the following installed:

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.10+ | Backend API (FastAPI) |
| **Node.js** | 18+ | Frontend (Next.js) |
| **PostgreSQL** | 16 | Primary database |
| **Redis** | 7 | Caching layer |
| **Docker** | 24+ | Containerization (recommended) |
| **Docker Compose** | 2.20+ | Multi-container orchestration |

### Optional Tools

- **Git** - For version control
- **Make** - For automation scripts
- **Nginx** - For production reverse proxy
- **Certbot** - For SSL/TLS certificates

---

## Quick Start with Docker

The fastest way to get TCG Tool running is using Docker Compose.

### 1. Clone the Repository

```bash
git clone https://github.com/strumendo/tcg-tool.git
cd tcg_tool
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys and configuration:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Optional
POKEMONTCG_API_KEY=your_pokemon_tcg_api_key_here
```

### 3. Start Services

```bash
docker-compose up -d
```

This will start all services in the background:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed initial data (meta decks, sets)
docker-compose exec backend python -m app.db.seed
```

### 5. Sync External Data (Optional)

```bash
# Sync card data from TCGdex
docker-compose exec backend python -m app.tasks.sync_cards

# Sync tournament data from Limitless
docker-compose exec backend python -m app.tasks.sync_limitless

# Sync news from PokeBeach
docker-compose exec backend python -m app.tasks.sync_news
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Redoc Documentation**: http://localhost:8000/redoc

---

## Manual Setup (Development)

For local development without Docker, follow these steps.

### Backend Setup

#### 1. Navigate to Backend Directory

```bash
cd backend
```

#### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs the backend package in editable mode with development dependencies.

#### 4. Configure Environment

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://tcgtool:tcgtool_dev@localhost:5432/tcgtool
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
POKEMONTCG_API_KEY=your_pokemon_tcg_api_key_here
TCGDEX_BASE_URL=https://api.tcgdex.net/v2
POKEMONTCG_BASE_URL=https://api.pokemontcg.io/v2
FRONTEND_URL=http://localhost:3000
DEFAULT_LANGUAGE=pt
LOG_LEVEL=INFO
```

#### 5. Start PostgreSQL and Redis

**PostgreSQL:**
```bash
# Install PostgreSQL 16
sudo apt install postgresql-16  # Ubuntu/Debian
brew install postgresql@16      # macOS

# Start service
sudo systemctl start postgresql  # Linux
brew services start postgresql@16  # macOS

# Create database and user
sudo -u postgres psql
```

```sql
CREATE USER tcgtool WITH PASSWORD 'tcgtool_dev';
CREATE DATABASE tcgtool OWNER tcgtool;
GRANT ALL PRIVILEGES ON DATABASE tcgtool TO tcgtool;
\q
```

**Redis:**
```bash
# Install Redis 7
sudo apt install redis-server  # Ubuntu/Debian
brew install redis             # macOS

# Start service
sudo systemctl start redis  # Linux
brew services start redis   # macOS
```

#### 6. Run Database Migrations

```bash
alembic upgrade head
```

#### 7. Seed Initial Data

```bash
python -m app.db.seed
```

#### 8. Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000.

---

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DEFAULT_LANGUAGE=pt
```

#### 4. Start Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:3000.

---

## Environment Variables

### Backend Environment Variables

Complete list of environment variables for `backend/.env`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string (asyncpg) |
| `REDIS_URL` | Yes | - | Redis connection string |
| `ANTHROPIC_API_KEY` | Yes | - | Claude API key for AI features |
| `POKEMONTCG_API_KEY` | No | - | Pokemon TCG API key (fallback) |
| `TCGDEX_BASE_URL` | No | `https://api.tcgdex.net/v2` | TCGdex API endpoint |
| `POKEMONTCG_BASE_URL` | No | `https://api.pokemontcg.io/v2` | Pokemon TCG API endpoint |
| `FRONTEND_URL` | No | `http://localhost:3000` | CORS allowed origin |
| `DEFAULT_LANGUAGE` | No | `pt` | Default UI language (pt/en) |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `SECRET_KEY` | Yes (prod) | auto-generated | JWT secret key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT token expiration |
| `API_V1_PREFIX` | No | `/api/v1` | API route prefix |
| `CORS_ORIGINS` | No | `["http://localhost:3000"]` | Allowed CORS origins |

### Frontend Environment Variables

Complete list of environment variables for `frontend/.env.local`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API base URL |
| `NEXT_PUBLIC_DEFAULT_LANGUAGE` | No | `pt` | Default UI language |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | No | `false` | Enable analytics |
| `NEXT_PUBLIC_APP_VERSION` | No | `3.0.0` | App version |

---

## Database Setup

### Migrations with Alembic

TCG Tool uses Alembic for database migrations.

#### Create a New Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

#### Apply Migrations

```bash
alembic upgrade head
```

#### Rollback Migration

```bash
alembic downgrade -1  # Rollback one version
```

#### View Migration History

```bash
alembic history
alembic current
```

### Seeding Data

The seed script populates initial data:

```bash
python -m app.db.seed
```

**What gets seeded:**
- Meta decks (Top 8 competitive decks)
- Card sets (Scarlet & Violet series)
- Matchup data (win rates between meta decks)
- Sample users (for testing)

### Manual Database Operations

```bash
# Connect to database
psql -U tcgtool -d tcgtool

# Backup database
pg_dump -U tcgtool tcgtool > backup.sql

# Restore database
psql -U tcgtool tcgtool < backup.sql
```

---

## Data Sync Tasks

TCG Tool syncs data from external APIs using background tasks.

### Sync Card Data (TCGdex)

```bash
python -m app.tasks.sync_cards
```

**What it does:**
- Fetches all Pokemon TCG cards from TCGdex API
- Updates card images, regulation marks, set info
- Supports English and Portuguese
- Caches results in PostgreSQL

**Options:**
```bash
python -m app.tasks.sync_cards --set sv7  # Sync specific set
python -m app.tasks.sync_cards --full     # Full resync (slow)
```

### Sync Tournament Data (Limitless)

```bash
python -m app.tasks.sync_limitless
```

**What it does:**
- Scrapes tournament results from Limitless TCG
- Updates meta deck statistics
- Populates deck lists and player data

**Scheduling:**
```bash
# Run daily at 2 AM via cron
0 2 * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_limitless
```

### Sync Tournament Calendar (RK9)

```bash
python -m app.tasks.sync_tournaments
```

**What it does:**
- Fetches official tournament calendar from RK9.gg
- Updates upcoming events
- Syncs to device calendar (Android)

### Sync News Feed (PokeBeach)

```bash
python -m app.tasks.sync_news
```

**What it does:**
- Scrapes news articles from PokeBeach
- Parses RSS feed
- Stores articles with translations

### Automated Scheduling

Use cron or systemd timers to automate syncs:

**crontab example:**
```cron
# Sync cards daily at 3 AM
0 3 * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_cards

# Sync tournaments every 6 hours
0 */6 * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_limitless

# Sync news every hour
0 * * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_news
```

---

## Docker Compose Services

The `docker-compose.yml` defines all services:

### Service Overview

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `db` | `postgres:16-alpine` | 5432 | PostgreSQL database |
| `redis` | `redis:7-alpine` | 6379 | Cache layer |
| `backend` | `./backend` | 8000 | FastAPI application |
| `frontend` | `./frontend` | 3000 | Next.js application |

### Service Configuration

**PostgreSQL (db):**
```yaml
db:
  image: postgres:16-alpine
  environment:
    POSTGRES_USER: tcgtool
    POSTGRES_PASSWORD: tcgtool_dev
    POSTGRES_DB: tcgtool
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

**Redis:**
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

**Backend:**
```yaml
backend:
  build: ./backend
  env_file: .env
  ports:
    - "8000:8000"
  depends_on:
    - db
    - redis
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```yaml
frontend:
  build: ./frontend
  env_file: .env
  ports:
    - "3000:3000"
  depends_on:
    - backend
  command: npm run dev
```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart service
docker-compose restart backend

# Stop all services
docker-compose down

# Remove volumes (caution: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

---

## Production Deployment

### Nginx Reverse Proxy

**Install Nginx:**
```bash
sudo apt install nginx
```

**Configure Nginx (`/etc/nginx/sites-available/tcgtool`):**
```nginx
server {
    listen 80;
    server_name tcgtool.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tcgtool.example.com;

    ssl_certificate /etc/letsencrypt/live/tcgtool.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tcgtool.example.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Docs
    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/tcgtool /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS with Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tcgtool.example.com
```

### Systemd Services

**Backend Service (`/etc/systemd/system/tcgtool-backend.service`):**
```ini
[Unit]
Description=TCG Tool Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=tcgtool
WorkingDirectory=/opt/tcg_tool/backend
Environment="PATH=/opt/tcg_tool/backend/.venv/bin"
ExecStart=/opt/tcg_tool/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Frontend Service (`/etc/systemd/system/tcgtool-frontend.service`):**
```ini
[Unit]
Description=TCG Tool Frontend
After=network.target tcgtool-backend.service

[Service]
Type=simple
User=tcgtool
WorkingDirectory=/opt/tcg_tool/frontend
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tcgtool-backend tcgtool-frontend
sudo systemctl start tcgtool-backend tcgtool-frontend
sudo systemctl status tcgtool-backend
```

### Environment Hardening

**Production `.env` settings:**
```env
# Use strong secrets
SECRET_KEY=$(openssl rand -hex 32)

# Disable debug mode
DEBUG=false

# Use production database
DATABASE_URL=postgresql+asyncpg://tcgtool:STRONG_PASSWORD@localhost:5432/tcgtool_prod

# Restrict CORS
CORS_ORIGINS=["https://tcgtool.example.com"]

# Enable security headers
ENABLE_SECURITY_HEADERS=true
```

**PostgreSQL hardening:**
```bash
# Edit /etc/postgresql/16/main/pg_hba.conf
# Change: host all all 0.0.0.0/0 md5
# To: host tcgtool tcgtool 127.0.0.1/32 md5
```

**Redis security:**
```bash
# Edit /etc/redis/redis.conf
requirepass STRONG_PASSWORD
bind 127.0.0.1
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# or
sudo netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>
```

#### 2. Database Connection Refused

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
psql -U tcgtool -d tcgtool  # Should connect

# Verify .env DATABASE_URL matches
```

#### 3. Redis Connection Error

**Error:**
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**Solution:**
```bash
# Start Redis
sudo systemctl start redis

# Test connection
redis-cli ping  # Should return PONG
```

#### 4. API Rate Limits

**Error:**
```
HTTPError: 429 Too Many Requests
```

**Solution:**
- Add `POKEMONTCG_API_KEY` to `.env` for higher limits
- Reduce sync frequency
- Use Redis caching (already enabled)

#### 5. Docker Build Fails

**Error:**
```
ERROR [backend 4/5] RUN pip install -e ".[dev]"
```

**Solution:**
```bash
# Clear Docker cache
docker-compose build --no-cache

# Check Python version in Dockerfile
FROM python:3.10-slim  # Should be 3.10+
```

#### 6. Alembic Migration Conflicts

**Error:**
```
alembic.util.exc.CommandError: Multiple head revisions are present
```

**Solution:**
```bash
# Merge heads
alembic merge heads -m "Merge migration heads"
alembic upgrade head
```

#### 7. Frontend API Connection Error

**Error:**
```
Failed to fetch: TypeError: Failed to fetch
```

**Solution:**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running on port 8000
- Check CORS settings in backend `.env`

#### 8. Docker Volume Permission Issues

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix ownership
sudo chown -R $USER:$USER postgres_data redis_data

# Or recreate volumes
docker-compose down -v
docker-compose up -d
```

### Debug Mode

Enable debug logging:

**Backend:**
```env
LOG_LEVEL=DEBUG
```

**Frontend:**
```bash
npm run dev  # Development mode includes debug logs
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Database
psql -U tcgtool -d tcgtool -c "SELECT version();"

# Redis
redis-cli ping
```

---

## Support

For issues not covered in this guide:

1. Check [GitHub Issues](https://github.com/strumendo/tcg-tool/issues)
2. Review logs: `docker-compose logs -f`
3. Contact: strumendo@gmail.com

---

**Document Version:** 3.0.0
**Last Updated:** 2026-02-15
**Author:** Bruno Strumendo
