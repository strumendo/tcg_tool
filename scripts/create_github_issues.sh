#!/bin/bash
# Script para criar todas as issues do projeto TCG Tool no GitHub
# Autor: Bruno Strumendo
# Executar: bash scripts/create_github_issues.sh

export PATH="$HOME/.local/bin:$PATH"
REPO="strumendo/tcg_tool"

echo "=== Criando issues no projeto TCG Tool ==="
echo ""

# ============================================================
# FASE 1 - Foundation
# ============================================================

echo "[Fase 1] Criando issues..."

gh issue create --repo "$REPO" \
  --title "[Fase 1] Arquivar codigo v2.0 na pasta old/" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Mover todos os arquivos existentes do projeto v2.0 para a pasta `old/` para preservar o historico enquanto iniciamos a nova arquitetura v3.0.

## Arquivos Movidos
- `main.py`, `meta_database.py`, `deck_parser.py`, `rotation_checker.py`
- `deck_compare.py`, `substitution.py`, `card_api.py`, `models.py`
- `deck_builder.py`, `deck_suggest.py`, `abilities_database.py`, `database.py`
- `example_deck.txt`, `example_opponent.txt`
- `requirements.txt`, `requirements-dev.txt`, `README.md`
- `android_app/`, `docs/`

## Arquivos Preservados
- `CLAUDE.md`, `.gitignore`, `.python-version`
- Deck files: `dragapult.txt`, `venusaur.txt`, `BlazikenEx.txt`

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 1] Criar estrutura monorepo" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar a nova estrutura de monorepo com diretorios `backend/`, `frontend/`, `mobile/` e configuracoes Docker.

## Estrutura Criada
```
tcg_tool/
├── backend/          # Python FastAPI
│   ├── app/
│   │   ├── api/v1/   # Route handlers
│   │   ├── core/     # Domain logic puro
│   │   ├── db/       # Session + seed
│   │   ├── integrations/  # API clients
│   │   ├── models/   # SQLAlchemy ORM
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── tasks/    # Background jobs
│   ├── alembic/      # Migrations
│   └── tests/
├── frontend/         # Next.js 15
│   └── src/
│       ├── app/      # Pages (App Router)
│       ├── components/
│       ├── hooks/
│       ├── lib/
│       └── providers/
├── mobile/           # Kivy (futuro)
├── docker-compose.yml
└── .env.example
```

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 1] Configurar backend (FastAPI + SQLAlchemy + Docker)" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Configurar o backend com FastAPI, SQLAlchemy 2.0 async, Alembic, PostgreSQL e Docker.

## Arquivos Criados
- `backend/pyproject.toml` - Dependencias (fastapi, sqlalchemy, alembic, httpx, anthropic)
- `backend/Dockerfile` - Python 3.10-slim
- `backend/app/config.py` - Pydantic Settings (DATABASE_URL, API keys, etc.)
- `backend/app/main.py` - FastAPI app com CORS, lifespan, health check
- `backend/app/dependencies.py` - `DBSession` type alias para DI
- `backend/app/db/session.py` - Async engine + session factory
- `docker-compose.yml` - PostgreSQL 16 + Redis 7 + Backend + Frontend
- `.env.example` - Template de variaveis de ambiente

## Stack
| Componente | Tecnologia |
|-----------|-----------|
| Backend | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Driver | asyncpg |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 1] Criar modelos ORM SQLAlchemy (17 tabelas)" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar todos os modelos ORM do SQLAlchemy 2.0 com Mapped[] type annotations.

## Tabelas Criadas (17)
| Tabela | Descricao |
|--------|-----------|
| `card_sets` | Sets de cartas (codigo, nome EN/PT, regulation mark) |
| `cards` | Dados de cartas (nome, tipo, HP, imagem, IDs externos) |
| `card_abilities` | Habilidades das cartas |
| `card_attacks` | Ataques com custo de energia (JSON) |
| `card_functions` | Funcoes das cartas (DRAW, SEARCH, etc.) |
| `users` | Usuarios |
| `decks` | Decks dos usuarios |
| `deck_cards` | Cartas nos decks (quantidade) |
| `meta_decks` | Decks meta competitivos |
| `meta_deck_cards` | Cartas nos decks meta |
| `meta_matchups` | Win rates entre decks meta |
| `user_collection` | Colecao do usuario |
| `battles` | Registros de batalhas |
| `battle_actions` | Acoes por turno |
| `tournaments` | Calendario de torneios |
| `news_articles` | Cache de noticias |
| `card_usage_stats` | Estatisticas de uso de cartas |
| `deck_usage_stats` | Estatisticas de uso de decks |

## Arquivos
- `backend/app/models/base.py` - Base + TimestampMixin
- `backend/app/models/card.py` - CardSet, Card, CardAbility, CardAttack, CardFunction
- `backend/app/models/deck.py` - Deck, DeckCard
- `backend/app/models/meta.py` - MetaDeck, MetaDeckCard, MetaMatchup
- `backend/app/models/user.py` - User
- `backend/app/models/battle.py` - Battle, BattleAction
- `backend/app/models/collection.py` - UserCollection
- `backend/app/models/tournament.py` - Tournament, NewsArticle, CardUsageStats, DeckUsageStats

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 1] Migrar logica de dominio para core/" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Migrar toda a logica de dominio do projeto v2.0 para modulos Python puros (sem dependencias de framework) em `backend/app/core/`.

## Modulos Criados (8)
| Modulo | Origem | Funcionalidade |
|--------|--------|----------------|
| `set_codes.py` | `deck_parser.py` | Mapeamento de 30+ sets, regulation marks |
| `deck_parser.py` | `deck_parser.py` | Parser PTCGO com 3 padroes regex |
| `rotation.py` | `rotation_checker.py` | Analise de rotacao Marco 2026 |
| `type_chart.py` | `deck_compare.py` | Tabela de tipos (fraquezas/resistencias) |
| `matchup_engine.py` | `deck_compare.py` | Comparacao de decks e matchups |
| `substitution_engine.py` | `substitution.py` | Substituicoes com scoring 40/40/20 |
| `deck_validation.py` | novo | Validacao 60 cartas, regra de 4 copias |
| `i18n.py` | `meta_database.py` | Internacionalizacao EN/PT |

## Decisoes
- Zero dependencias de framework (apenas dataclasses, enum, re, typing)
- `ParsedCard`/`ParsedDeck` como dataclasses leves
- Separacao de concerns: cada modulo faz uma coisa

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 1] Criar clientes de integracao (TCGdex, PokemonTCG, Claude)" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar clientes async para APIs externas com padrao de retry e fallback.

## Clientes Criados
| Cliente | API | Funcionalidades |
|---------|-----|-----------------|
| `base_client.py` | - | Retry com backoff linear (3 tentativas) |
| `tcgdex_client.py` | TCGdex API | fetch_card, search_cards, get_card_image_url |
| `pokemontcg_client.py` | Pokemon TCG API | fetch_cards, search_by_name (fallback) |
| `claude_client.py` | Anthropic Claude | chat, suggest_swaps, analyze_battle, simulate_plays |

## Padrao
- Todos async com httpx
- TCGdex como primario, PokemonTCG como fallback
- Claude com system prompts especializados por funcao

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 1] Criar schemas Pydantic, services e API routes (50+ endpoints)" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar toda a camada de schemas, services e rotas da API REST.

## Schemas Pydantic (12 arquivos)
card.py, deck.py, meta.py, analysis.py, battle.py, chat.py, stats.py, user.py, collection.py, simulation.py, tournament.py + __init__.py

## Services (3 arquivos)
- `card_service.py` - search_cards, get_card, get_card_alternatives, get_card_usage
- `deck_service.py` - CRUD, import/export, missing cards
- `meta_service.py` - get_meta_decks, get_matchups, get_tiers

## API Routes (11 routers, 50+ endpoints)
| Router | Prefix | Endpoints |
|--------|--------|-----------|
| cards | `/cards` | search, detail, alternatives, usage, abilities |
| decks | `/decks` | CRUD, import, export, missing |
| meta | `/meta` | decks, matchups, tiers |
| analysis | `/analysis` | rotation, compare, matchup, substitutions |
| battles | `/battles` | CRUD |
| chat | `/chat` | message (Claude AI) |
| stats | `/stats` | cards, decks, user |
| collection | `/collection` | list, update, missing |
| suggestions | `/suggestions` | AI swaps |
| simulation | `/simulation` | play-sequence |
| tournaments | `/tournaments` | list, news |

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 1] Configurar Alembic e seed data" \
  --label "fase-1,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Configurar Alembic para migrations e criar seed data inicial.

## Arquivos
- `backend/alembic.ini` - Configuracao Alembic
- `backend/alembic/env.py` - Async-compatible com conversao asyncpg -> psycopg2
- `backend/alembic/versions/001_initial_schema.py` - Migration inicial com 18 tabelas
- `backend/app/db/seed.py` - Seed de usuario default + 9 meta decks + 36 matchups

## Seed Data
- 1 usuario default (id=1, language="pt")
- 9 meta decks do old/meta_database.py
- 36 matchups entre os decks

## Uso
```bash
cd backend
alembic upgrade head    # Criar tabelas
python -m app.db.seed   # Popular dados
```

## Status: CONCLUIDO
EOF
)"

echo ""
echo "[Fase 1] Issues criadas!"
echo ""

# ============================================================
# FASE 2 - Deck Management
# ============================================================

echo "[Fase 2] Criando issues..."

gh issue create --repo "$REPO" \
  --title "[Fase 2] Criar paginas de gerenciamento de decks" \
  --label "fase-2,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar todas as paginas frontend para gerenciamento de decks.

## Paginas Criadas
| Pagina | Funcionalidade |
|--------|----------------|
| `/decks` | Lista de decks com cards, contagem Pokemon/Trainer/Energy |
| `/decks/new` | Criacao de deck com busca de cartas e controle de quantidade |
| `/decks/import` | Importacao no formato PTCGO/TCG Live |
| `/decks/[id]` | Detalhe com DeckGrid visual, export, missing cards |
| `/decks/[id]/analysis` | Analise com tabs Rotacao/Comparacao/Substituicoes |

## Componentes Criados
| Componente | Funcionalidade |
|------------|----------------|
| `DeckGrid` | Grid visual de cartas organizado por Pokemon/Trainer/Energy |
| `CardImage` | Imagem da carta com badge de regulation mark |
| `DeckImportForm` | Formulario de importacao PTCGO com exemplo |
| `DeckExportModal` | Modal de exportacao com copy-to-clipboard |
| `CardDetailPanel` | Painel lateral com detalhes completos da carta |

## Hooks Utilizados
useDecks, useDeck, useCreateDeck, useImportDeck, useDeleteDeck, useExportDeck, useDeckMissingCards

## Status: CONCLUIDO
EOF
)"

# ============================================================
# FASE 3 - Analysis Engine
# ============================================================

echo "[Fase 3] Criando issues..."

gh issue create --repo "$REPO" \
  --title "[Fase 3] Criar componentes de analise e meta game" \
  --label "fase-3,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar componentes de visualizacao de analise e meta game no frontend.

## Paginas
| Pagina | Funcionalidade |
|--------|----------------|
| `/meta` | Tier list + matchup matrix com toggle |
| `/meta/[id]` | Detalhe do meta deck (estrategia, matchups, forcas/fraquezas) |

## Componentes de Meta
| Componente | Funcionalidade |
|------------|----------------|
| `TierList` | Decks agrupados por Tier 1/2/3 com cores distintas |
| `MatchupMatrix` | Grid interativa de win rates com gradiente de cores |
| `WinRateBadge` | Badge de win rate colorido (verde/amarelo/vermelho) |

## Componentes de Analise
| Componente | Funcionalidade |
|------------|----------------|
| `RotationReport` | Badge de severidade, breakdown por tipo, barras de progresso |
| `ComparisonView` | Comparacao lado-a-lado com scores de Speed/Consistency/Power |
| `SubstitutionList` | Sugestoes de substituicao com score e razoes |

## Features
- Cores por severidade (NONE/LOW/MODERATE/HIGH/CRITICAL)
- Gradiente de cores no matchup matrix (30% vermelho -> 50% amarelo -> 70% verde)
- Texto em portugues em toda interface
- Design responsivo

## Status: CONCLUIDO
EOF
)"

# ============================================================
# FASE 4 - Card Intelligence
# ============================================================

echo "[Fase 4] Criando issues..."

gh issue create --repo "$REPO" \
  --title "[Fase 4] Criar sync tasks e Limitless scraper (backend)" \
  --label "fase-4,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar tasks de sincronizacao de dados e scraper do Limitless TCG.

## Arquivos Criados
| Arquivo | Funcionalidade |
|---------|----------------|
| `integrations/limitless_client.py` | Scraper de usage data do Limitless TCG |
| `tasks/sync_cards.py` | Sync TCGdex -> PostgreSQL (sets, cards, abilities, attacks) |
| `tasks/sync_limitless.py` | Sync de estatisticas de uso (cards + decks) |
| `tasks/seed_abilities.py` | Seed do catalogo de habilidades do old/ |

## Sync Cards
- `sync_all_sets()` - Busca todos os sets via TCGdex
- `sync_set_cards(set_code)` - Busca cartas de um set com delay de 150ms
- `sync_all_cards()` - Sync completo de sets + cartas
- Upsert por tcgdex_id, recria abilities/attacks

## Limitless Scraper
- `fetch_card_usage()` - Scrape de uso de cartas (regex-based)
- `fetch_deck_usage()` - Scrape de uso de archetypes
- Fallback para lista vazia se scraping falhar

## Uso
```bash
cd backend
python -m app.tasks.sync_cards          # Sync todas as cartas
python -m app.tasks.sync_cards SVI PAL  # Sync sets especificos
python -m app.tasks.sync_limitless      # Sync dados do Limitless
python -m app.tasks.seed_abilities      # Seed habilidades
```

## Status: CONCLUIDO
EOF
)"

gh issue create --repo "$REPO" \
  --title "[Fase 4] Criar pagina de detalhe de cartas e componentes" \
  --label "fase-4,concluido" \
  --body "$(cat <<'EOF'
## Descricao
Criar pagina de detalhe de cartas com alternativas e estatisticas de uso.

## Paginas
| Pagina | Funcionalidade |
|--------|----------------|
| `/cards/[id]` | Detalhe completo com tabs (Detalhes/Alternativas/Estatisticas) |
| `/cards` (melhorada) | Filtros de energia/regulation, toggle lista/grid, load more |

## Componentes Criados
| Componente | Funcionalidade |
|------------|----------------|
| `CardAlternatives` | Grid de cartas alternativas com overlap de funcoes |
| `CardUsageChart` | Estatisticas de uso com barras Tailwind (sem recharts) |
| `EnergyBadge` | Badge de tipo de energia com cor e nome em portugues |

## Melhorias na Pagina /cards
- Filtro por tipo de energia
- Filtro por regulation mark (G/H/I)
- Toggle entre vista de lista e grid
- Botao "Carregar mais" (24 items por vez)
- Navegacao para /cards/[id] ao clicar
- Contagem de resultados
- Botao limpar filtros

## Status: CONCLUIDO
EOF
)"

echo ""
echo "=== Todas as issues foram criadas! ==="
echo ""
echo "Total: 12 issues (Fase 1: 8, Fase 2: 1, Fase 3: 1, Fase 4: 2)"
