# TCG Tool v3.0

[🇧🇷 Português](#português) | [🇺🇸 English](#english)

---

## Português

Plataforma completa de análise de decks para Pokémon Trading Card Game (TCG) com suporte bilíngue (Inglês/Português).

### Funcionalidades

- **Gerenciamento de Decks** - Criar, importar (PTCGO/TCG Live), exportar e validar decks
- **Meta Game** - Tier list com os melhores decks competitivos e matriz de matchups
- **Análise de Decks** - Rotação (Março 2026), comparação, substituições
- **Busca de Cartas** - Pesquisa avançada com filtros, alternativas e estatísticas de uso
- **Coleção** - Gerenciar cartas que você possui e ver o que falta por deck
- **Batalhas** - Registrar batalhas e obter análise com IA
- **Chat IA** - Assistente inteligente para estratégia com streaming em tempo real
- **Simulação** - Simular sequências de jogadas ótimas
- **Torneios e Notícias** - Calendário de torneios (RK9) e notícias (PokeBeach)

### Tech Stack

| Componente | Tecnologia |
|-----------|-----------|
| Backend | Python 3.10+ / FastAPI / SQLAlchemy 2.0 async / PostgreSQL 16 |
| Frontend | Next.js 15 / React 19 / TypeScript / Tailwind CSS / TanStack Query |
| AI | Claude API (Anthropic) |
| Cache | Redis 7 |
| Infra | Docker + Docker Compose |

### Quick Start

```bash
# Clonar repositório
git clone https://github.com/strumendo/tcg-tool.git
cd tcg_tool

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas API keys (ANTHROPIC_API_KEY, etc.)

# Iniciar com Docker
docker-compose up -d

# Acessar:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Desenvolvimento Manual

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configurar banco de dados
alembic upgrade head
python -m app.db.seed

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Estrutura do Projeto

```
tcg_tool/
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── api/v1/   # Rotas da API (11 módulos)
│   │   ├── core/     # Lógica de domínio pura
│   │   ├── models/   # Modelos SQLAlchemy (17 tabelas)
│   │   ├── schemas/  # Schemas Pydantic v2
│   │   ├── services/ # Camada de serviços
│   │   ├── integrations/ # Clientes de APIs externas
│   │   └── tasks/    # Tarefas de sincronização
│   └── tests/
├── frontend/         # Next.js 15 App Router
│   └── src/
│       ├── app/      # 20 páginas
│       ├── components/ # 24+ componentes React
│       ├── hooks/    # React Query hooks
│       └── lib/      # Utilitários e tipos
├── docs/             # Documentação completa
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── DEPLOY.md
│   ├── USER_GUIDE.md (Português)
│   └── USER_GUIDE_EN.md (English)
├── old/              # Código v2.0 arquivado
└── docker-compose.yml
```

### Documentação

| Documento | Descrição |
|-----------|-----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura do sistema e decisões técnicas |
| [API.md](docs/API.md) | Referência completa da API REST |
| [DATABASE.md](docs/DATABASE.md) | Schema do banco de dados (17 tabelas) |
| [DEPLOY.md](docs/DEPLOY.md) | Guia de implantação e configuração |
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Guia do usuário (Português) |
| [USER_GUIDE_EN.md](docs/USER_GUIDE_EN.md) | User guide (English) |

### APIs Externas

| Fonte | Uso |
|-------|-----|
| [TCGdex](https://tcgdex.dev) | Dados de cartas (primário, 10+ idiomas) |
| [Pokemon TCG API](https://pokemontcg.io) | Dados de cartas (fallback) |
| [Limitless TCG](https://limitlesstcg.com) | Estatísticas de torneios |
| [PokeBeach](https://pokebeach.com) | Feed de notícias |
| [RK9](https://rk9.gg) | Calendário de torneios |

### Autor

**Bruno Strumendo** - [GitHub](https://github.com/strumendo)

### Licença

Este projeto é de uso privado.

---

## English

Complete deck analysis platform for Pokémon Trading Card Game (TCG) with bilingual support (English/Portuguese).

### Features

- **Deck Management** - Create, import (PTCGO/TCG Live), export, and validate decks
- **Meta Game** - Tier list with best competitive decks and matchup matrix
- **Deck Analysis** - Rotation (March 2026), comparison, substitutions
- **Card Search** - Advanced search with filters, alternatives, and usage statistics
- **Collection** - Manage cards you own and see what's missing per deck
- **Battles** - Record battles and get AI analysis
- **AI Chat** - Intelligent strategy assistant with real-time streaming
- **Simulation** - Simulate optimal play sequences
- **Tournaments & News** - Tournament calendar (RK9) and news feed (PokeBeach)

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+ / FastAPI / SQLAlchemy 2.0 async / PostgreSQL 16 |
| Frontend | Next.js 15 / React 19 / TypeScript / Tailwind CSS / TanStack Query |
| AI | Claude API (Anthropic) |
| Cache | Redis 7 |
| Infra | Docker + Docker Compose |

### Quick Start

```bash
# Clone repository
git clone https://github.com/strumendo/tcg-tool.git
cd tcg_tool

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys (ANTHROPIC_API_KEY, etc.)

# Start with Docker
docker-compose up -d

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Development

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Setup database
alembic upgrade head
python -m app.db.seed

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Project Structure

```
tcg_tool/
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── api/v1/   # API routes (11 modules)
│   │   ├── core/     # Pure domain logic
│   │   ├── models/   # SQLAlchemy models (17 tables)
│   │   ├── schemas/  # Pydantic v2 schemas
│   │   ├── services/ # Service layer
│   │   ├── integrations/ # External API clients
│   │   └── tasks/    # Sync tasks
│   └── tests/
├── frontend/         # Next.js 15 App Router
│   └── src/
│       ├── app/      # 20 pages
│       ├── components/ # 24+ React components
│       ├── hooks/    # React Query hooks
│       └── lib/      # Utilities and types
├── docs/             # Complete documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── DEPLOY.md
│   ├── USER_GUIDE.md (Português)
│   └── USER_GUIDE_EN.md (English)
├── old/              # Archived v2.0 code
└── docker-compose.yml
```

### Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and technical decisions |
| [API.md](docs/API.md) | Complete REST API reference |
| [DATABASE.md](docs/DATABASE.md) | Database schema (17 tables) |
| [DEPLOY.md](docs/DEPLOY.md) | Deployment and configuration guide |
| [USER_GUIDE.md](docs/USER_GUIDE.md) | User guide (Português) |
| [USER_GUIDE_EN.md](docs/USER_GUIDE_EN.md) | User guide (English) |

### External APIs

| Source | Usage |
|--------|-------|
| [TCGdex](https://tcgdex.dev) | Card data (primary, 10+ languages) |
| [Pokemon TCG API](https://pokemontcg.io) | Card data (fallback) |
| [Limitless TCG](https://limitlesstcg.com) | Tournament statistics |
| [PokeBeach](https://pokebeach.com) | News feed |
| [RK9](https://rk9.gg) | Tournament calendar |

### Author

**Bruno Strumendo** - [GitHub](https://github.com/strumendo)

### License

This project is for private use.
