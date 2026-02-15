# TCG Tool v3.0

Plataforma completa de analise de decks para Pokemon Trading Card Game (TCG) com suporte bilingue (Ingles/Portugues).

## Funcionalidades

- **Gerenciamento de Decks** - Criar, importar (PTCGO/TCG Live), exportar e validar decks
- **Meta Game** - Tier list com os melhores decks competitivos e matriz de matchups
- **Analise de Decks** - Rotacao (Marco 2026), comparacao, substituicoes
- **Busca de Cartas** - Pesquisa avancada com filtros, alternativas e estatisticas de uso
- **Colecao** - Gerenciar cartas que voce possui e ver o que falta por deck
- **Batalhas** - Registrar batalhas e obter analise com IA
- **Chat IA** - Assistente inteligente para estrategia com streaming em tempo real
- **Simulacao** - Simular sequencias de jogadas otimas
- **Torneios e Noticias** - Calendario de torneios (RK9) e noticias (PokeBeach)

## Tech Stack

| Componente | Tecnologia |
|-----------|-----------|
| Backend | Python 3.10+ / FastAPI / SQLAlchemy 2.0 async / PostgreSQL 16 |
| Frontend | Next.js 15 / React 19 / TypeScript / Tailwind CSS / TanStack Query |
| AI | Claude API (Anthropic) |
| Cache | Redis 7 |
| Infra | Docker + Docker Compose |

## Quick Start

```bash
# Clonar repositorio
git clone https://github.com/strumendo/tcg-tool.git
cd tcg_tool

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com suas API keys (ANTHROPIC_API_KEY, etc.)

# Iniciar com Docker
docker-compose up -d

# Acessar:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Desenvolvimento Manual

### Backend

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Estrutura do Projeto

```
tcg_tool/
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── api/v1/   # Rotas da API (11 modulos)
│   │   ├── core/     # Logica de dominio pura
│   │   ├── models/   # Modelos SQLAlchemy (17 tabelas)
│   │   ├── schemas/  # Schemas Pydantic v2
│   │   ├── services/ # Camada de servicos
│   │   ├── integrations/ # Clientes de APIs externas
│   │   └── tasks/    # Tarefas de sincronizacao
│   └── tests/
├── frontend/         # Next.js 15 App Router
│   └── src/
│       ├── app/      # 20 paginas
│       ├── components/ # 24+ componentes React
│       ├── hooks/    # React Query hooks
│       └── lib/      # Utilitarios e tipos
├── docs/             # Documentacao completa
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── DEPLOY.md
│   └── USER_GUIDE.md
├── old/              # Codigo v2.0 arquivado
└── docker-compose.yml
```

## Documentacao

| Documento | Descricao |
|-----------|-----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura do sistema e decisoes tecnicas |
| [API.md](docs/API.md) | Referencia completa da API REST |
| [DATABASE.md](docs/DATABASE.md) | Schema do banco de dados (17 tabelas) |
| [DEPLOY.md](docs/DEPLOY.md) | Guia de implantacao e configuracao |
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Guia do usuario (Portugues) |

## APIs Externas

| Fonte | Uso |
|-------|-----|
| [TCGdex](https://tcgdex.dev) | Dados de cartas (primario, 10+ idiomas) |
| [Pokemon TCG API](https://pokemontcg.io) | Dados de cartas (fallback) |
| [Limitless TCG](https://limitlesstcg.com) | Estatisticas de torneios |
| [PokeBeach](https://pokebeach.com) | Feed de noticias |
| [RK9](https://rk9.gg) | Calendario de torneios |

## Autor

**Bruno Strumendo** - [GitHub](https://github.com/strumendo)

## Licenca

Este projeto e de uso privado.
