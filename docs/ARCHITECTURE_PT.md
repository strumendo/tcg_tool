# ARCHITECTURE.md - TCG Tool v3.0

**Autor:** Bruno Strumendo
**Versão:** 3.0
**Última Atualização:** 2026-02-15

---

## 1. Visão Geral

### Descrição do Projeto

TCG Tool v3.0 é uma **plataforma de análise de decks do Pokemon Trading Card Game (TCG)** que oferece análise competitiva abrangente, construção de decks e insights baseados em IA. A plataforma permite aos jogadores:

- Importar e analisar decks do TCG Live ou arquivos de texto
- Construir e otimizar decks com busca avançada de cartas
- Comparar decks com variações meta e matchups
- Acompanhar resultados de torneios e tendências do meta
- Processar vídeos de partidas para insights estratégicos (com IA)
- Acessar notícias e calendários de torneios
- Obter recomendações e análises de decks baseadas em IA

### Objetivos

1. **Análise Competitiva**: Fornecer análise de decks de nível competitivo com verificação de rotação, previsões de matchup e posicionamento no meta
2. **Construção de Decks**: Permitir construção eficiente de decks com busca inteligente de cartas, sugestões de substituições e validação
3. **Integração de IA**: Aproveitar Claude AI para análise de decks em linguagem natural, processamento de vídeo e insights estratégicos
4. **Suporte Bilíngue**: Suporte completo em Inglês/Português para base internacional de jogadores
5. **Agregação de Dados**: Centralizar dados de múltiplas fontes (TCGdex, Limitless, PokeBeach, RK9)
6. **Experiência do Usuário**: Interface web moderna e responsiva com atualizações em tempo real

### Evolução desde v2.0

- **v1.0**: Ferramenta CLI com verificação básica de rotação
- **v2.0**: Adicionado app Android (Kivy) e base de dados meta
- **v3.0**: Reescrita completa como plataforma web full-stack com integração de IA

---

## 2. Stack Tecnológica

### Backend

| Tecnologia | Versão | Propósito |
|------------|---------|-----------|
| **FastAPI** | 0.115+ | Framework web assíncrono moderno |
| **SQLAlchemy** | 2.0+ | ORM com suporte assíncrono |
| **PostgreSQL** | 16 | Banco de dados principal |
| **Alembic** | Latest | Migrações de banco de dados |
| **Pydantic** | v2 | Validação e serialização de dados |
| **asyncpg** | Latest | Driver assíncrono PostgreSQL |
| **httpx** | 0.28+ | Cliente HTTP assíncrono |
| **Redis** | 7 | Camada de cache |
| **Uvicorn** | Latest | Servidor ASGI |

### Frontend

| Tecnologia | Versão | Propósito |
|------------|---------|-----------|
| **Next.js** | 15 | Framework React com App Router |
| **TypeScript** | 5.x | JavaScript com segurança de tipos |
| **Tailwind CSS** | 3.x | CSS utilitário |
| **TanStack Query** | v5 | Gerenciamento de estado do servidor |
| **Axios** | Latest | Cliente HTTP |
| **Shadcn/ui** | Latest | Biblioteca de componentes UI |
| **Lucide React** | Latest | Biblioteca de ícones |

### IA & Serviços Externos

| Serviço | Propósito |
|---------|-----------|
| **Anthropic Claude API** | Análise com IA, chat, processamento de vídeo |
| **TCGdex API** | Dados de cartas primários (10+ idiomas) |
| **Pokemon TCG API** | Dados de cartas de fallback (Inglês) |
| **Limitless TCG** | Dados de torneios, estatísticas de decks |
| **PokeBeach** | Feed de notícias |
| **RK9** | Calendário oficial de torneios |

### DevOps & Ferramentas

| Ferramenta | Propósito |
|------------|-----------|
| **Docker** | Containerização (PostgreSQL, Redis) |
| **Docker Compose** | Orquestração multi-container |
| **Git** | Controle de versão |
| **pytest** | Testes de backend |
| **Jest** | Testes de frontend |

---

## 3. Estrutura do Monorepo

```
tcg_tool/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── main.py            # Ponto de entrada da aplicação FastAPI
│   │   ├── config.py          # Gerenciamento de configuração
│   │   ├── database.py        # Gerenciamento de sessão do banco de dados
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Schemas Pydantic
│   │   ├── api/
│   │   │   └── v1/            # Rotas da API (versionadas)
│   │   ├── services/          # Camada de lógica de negócio
│   │   ├── core/              # Lógica de domínio principal
│   │   ├── integrations/      # Clientes de APIs externas
│   │   └── tasks/             # Tarefas em background
│   ├── alembic/               # Migrações de banco de dados
│   ├── tests/                 # Testes de backend
│   ├── requirements.txt       # Dependências Python
│   └── Dockerfile             # Container do backend
│
├── frontend/                   # Frontend Next.js
│   ├── app/                   # Páginas do App Router
│   ├── components/            # Componentes React
│   ├── lib/                   # Utilitários e cliente da API
│   ├── hooks/                 # Hooks personalizados React
│   ├── types/                 # Tipos TypeScript
│   ├── public/                # Assets estáticos
│   ├── package.json           # Dependências Node
│   └── Dockerfile             # Container do frontend
│
├── mobile/                     # App mobile (adiado para v4.0)
│   └── README.md              # Placeholder
│
├── old/                        # Código arquivado v2.0
│   ├── main.py                # Ferramenta CLI
│   ├── meta_database.py       # Dados meta antigos
│   └── android_app/           # App Android Kivy
│
├── docs/                       # Documentação
│   ├── ARCHITECTURE.md        # Este arquivo
│   ├── REQUIREMENTS.md        # Especificação de requisitos
│   ├── BACKLOG.md             # Epics e User Stories
│   ├── FLOW.md                # Diagramas de fluxo
│   └── INSTALL.md             # Guia de instalação
│
├── docker-compose.yml          # Ambiente de desenvolvimento
├── .env.example                # Template de variáveis de ambiente
├── CLAUDE.md                   # Guia do assistente de IA
└── README.md                   # Visão geral do projeto
```

---

## 4. Arquitetura do Sistema

### Arquitetura de Alto Nível (Mermaid)

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

### Diagrama de Interação de Componentes

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

## 5. Arquitetura do Backend

### Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (api/v1/)                      │
│         Tratamento de Requisições HTTP, Validação, Resposta         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Service Layer (services/)                  │
│           Lógica de Negócio, Orquestração, Caching          │
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

### Estrutura de Diretórios

```
backend/app/
├── main.py                          # Aplicação FastAPI
├── config.py                        # Configurações (Pydantic BaseSettings)
├── database.py                      # Sessão do banco de dados, pool de conexões
│
├── models/                          # Modelos ORM SQLAlchemy
│   ├── __init__.py
│   ├── user.py                      # Modelo User
│   ├── card.py                      # Modelo Card
│   ├── deck.py                      # Modelos Deck, DeckCard
│   ├── meta.py                      # MetaDeck, MatchupData
│   ├── collection.py                # UserCollection
│   ├── battle.py                    # BattleLog, BattleAction
│   ├── news.py                      # NewsArticle
│   └── tournament.py                # Tournament, Event
│
├── schemas/                         # Schemas Pydantic (v2)
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
│   └── v1/                          # Rotas da API (versão 1)
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
├── services/                        # Serviços de Lógica de Negócio
│   ├── __init__.py
│   ├── card_service.py              # Busca, fetch, cache de cartas
│   ├── deck_service.py              # CRUD de decks, validação
│   ├── meta_service.py              # Gerenciamento de decks meta
│   ├── analysis_service.py          # Rotação, matchup, comparação
│   ├── ai_service.py                # Integração Claude, chat, vídeo
│   ├── collection_service.py        # Gerenciamento de coleção do usuário
│   ├── news_service.py              # Agregação de notícias
│   └── tournament_service.py        # Dados de torneios
│
├── core/                            # Lógica de Domínio Principal (funções puras)
│   ├── __init__.py
│   ├── deck_parser.py               # Parse de formato PTCGO/TCG Live
│   ├── rotation.py                  # Análise de impacto de rotação
│   ├── matchup_engine.py            # Cálculo de matchup
│   ├── substitution_engine.py       # Lógica de substituição de cartas
│   ├── type_chart.py                # Efetividade de tipos
│   ├── set_codes.py                 # Mapeamentos de códigos de sets
│   ├── i18n.py                      # Helpers de strings bilíngues
│   └── deck_validation.py           # Regras de 60 cartas, 4 cópias
│
├── integrations/                    # Clientes de APIs Externas
│   ├── __init__.py
│   ├── tcgdex_client.py             # Cliente API TCGdex
│   ├── pokemontcg_client.py         # Cliente API Pokemon TCG
│   ├── limitless_client.py          # Scraper/API Limitless
│   ├── pokebeach_client.py          # RSS/scraper PokeBeach
│   ├── rk9_client.py                # Scraper de eventos RK9
│   └── claude_client.py             # API Anthropic Claude
│
└── tasks/                           # Tarefas em Background (Celery/FastAPI BG)
    ├── __init__.py
    ├── sync_cards.py                # Sincronizar banco de dados de cartas
    ├── sync_limitless.py            # Sincronizar dados de torneios
    ├── sync_tournaments.py          # Sincronizar calendário de eventos
    ├── sync_news.py                 # Sincronizar feed de notícias
    └── seed_abilities.py            # Seed de habilidades Pokemon
```

### Padrão de Injeção de Dependência

FastAPI usa injeção de dependência para sessões de banco de dados e serviços:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Dependência de sessão do banco de dados
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Alias de tipo para injeção limpa
DBSession = Annotated[AsyncSession, Depends(get_db)]

# Uso na rota
@router.get("/cards/{card_id}")
async def get_card(card_id: int, db: DBSession):
    return await CardService.get_by_id(db, card_id)
```

### Stack Assíncrona

Implementação assíncrona completa em toda a aplicação:

- **FastAPI**: Handlers de rota assíncronos
- **SQLAlchemy 2.0**: ORM assíncrono com `async_session`
- **asyncpg**: Driver assíncrono PostgreSQL
- **httpx**: Cliente HTTP assíncrono para APIs externas
- **Uvicorn**: Servidor ASGI com workers assíncronos

Exemplo de serviço assíncrono:

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

## 6. Arquitetura do Frontend

### Estrutura do Next.js App Router

```
frontend/app/
├── layout.tsx                       # Layout raiz
├── page.tsx                         # Página inicial
├── globals.css                      # Estilos globais
│
├── cards/
│   ├── page.tsx                     # Página de busca de cartas
│   └── [id]/page.tsx                # Página de detalhe da carta
│
├── decks/
│   ├── page.tsx                     # Lista de meus decks
│   ├── new/page.tsx                 # Página de novo deck
│   ├── import/page.tsx              # Página de importar deck
│   ├── [id]/
│   │   ├── page.tsx                 # Detalhe do deck
│   │   ├── edit/page.tsx            # Editor de deck
│   │   └── analysis/page.tsx        # Análise do deck
│   └── builder/page.tsx             # Construtor de deck
│
├── meta/
│   ├── page.tsx                     # Visão geral do meta
│   ├── [deckId]/page.tsx            # Detalhe do deck meta
│   └── matchups/page.tsx            # Matriz de matchups
│
├── analysis/
│   ├── rotation/page.tsx            # Verificador de rotação
│   └── compare/page.tsx             # Comparação de decks
│
├── collection/
│   ├── page.tsx                     # Gerenciador de coleção
│   └── import/page.tsx              # Importar coleção
│
├── battle/
│   ├── page.tsx                     # Lista de logs de batalha
│   ├── new/page.tsx                 # Novo log de batalha
│   └── [id]/page.tsx                # Análise de batalha
│
├── ai/
│   ├── chat/page.tsx                # Interface de chat com IA
│   └── video/page.tsx               # Análise de vídeo
│
├── news/
│   └── page.tsx                     # Feed de notícias
│
├── tournaments/
│   ├── page.tsx                     # Lista de torneios
│   ├── calendar/page.tsx            # Calendário de eventos
│   └── [id]/page.tsx                # Detalhe do torneio
│
└── profile/
    └── page.tsx                     # Perfil do usuário
```

### Organização de Componentes

```
frontend/components/
├── ui/                              # Componentes shadcn/ui
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── table.tsx
│   └── ...
│
├── layout/                          # Componentes de layout
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── Footer.tsx
│   └── LanguageToggle.tsx
│
├── deck/                            # Componentes relacionados a decks
│   ├── DeckCard.tsx                 # Card de preview do deck
│   ├── DeckList.tsx                 # Lista de cartas do deck
│   ├── DeckStats.tsx                # Estatísticas do deck
│   ├── DeckBuilder.tsx              # UI do construtor de deck
│   └── DeckImporter.tsx             # Formulário de importação de deck
│
├── cards/                           # Componentes relacionados a cartas
│   ├── CardImage.tsx                # Exibição de imagem da carta
│   ├── CardSearchBar.tsx            # Input de busca
│   ├── CardGrid.tsx                 # Layout em grid de cartas
│   ├── CardFilter.tsx               # Controles de filtro
│   └── CardDetail.tsx               # Visão de detalhe da carta
│
├── meta/                            # Componentes do meta
│   ├── MetaDeckCard.tsx             # Card do deck meta
│   ├── MatchupMatrix.tsx            # Tabela de matchups
│   └── TierList.tsx                 # Exibição de tier list
│
├── analysis/                        # Componentes de análise
│   ├── RotationReport.tsx           # Análise de rotação
│   ├── MatchupAnalysis.tsx          # Detalhamento de matchup
│   ├── ComparisonTable.tsx          # Comparação de decks
│   └── SubstitutionSuggestions.tsx  # Sugestões de cartas
│
├── battle/                          # Componentes de log de batalha
│   ├── BattleLogCard.tsx            # Preview de log de batalha
│   ├── TurnTimeline.tsx             # Timeline turno a turno
│   └── ActionLog.tsx                # Lista de ações
│
├── chat/                            # Componentes de chat com IA
│   ├── ChatInterface.tsx            # UI do chat
│   ├── MessageBubble.tsx            # Exibição de mensagem
│   └── StreamingIndicator.tsx       # Estado de carregamento
│
├── collection/                      # Componentes de coleção
│   ├── CollectionGrid.tsx           # Grid de cartas com contagens
│   ├── SetProgress.tsx              # Completude do set
│   └── WantlistManager.tsx          # UI de lista de desejos
│
└── tournament/                      # Componentes de torneio
    ├── TournamentCard.tsx           # Preview de torneio
    ├── EventCalendar.tsx            # Visão de calendário
    └── StandingTable.tsx            # Tabela de classificação
```

### Padrão de Hooks

Hooks React personalizados usando TanStack Query:

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
    // Implementação de streaming SSE
    const eventSource = api.ai.streamChat(content, deckId)
    // Tratar resposta em streaming
  }

  return { messages, sendMessage }
}
```

### Cliente da API

Cliente da API baseado em Axios com TypeScript:

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
      // Implementação SSE
      return new EventSource(
        `/api/v1/ai/chat?message=${encodeURIComponent(message)}&deck_id=${deckId}`
      )
    },
  },
}
```

---

## 7. Diagramas de Fluxo de Dados

### Fluxo de Busca de Cartas

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

### Fluxo de Chat com IA (Streaming SSE)

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

### Fluxo de Importação de Deck

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

### Fluxo de Análise de Batalha

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

## 8. Estratégia de APIs Externas

### Prioridade de APIs & Fallback

```
Primária: TCGdex API
    ├─ Prós: 10+ idiomas, abrangente, gratuita
    ├─ Contras: Limites de taxa (desconhecidos), sem SLA oficial
    └─ Fallback em: 429, erros 5xx, timeout
           ↓
Secundária: Pokemon TCG API
    ├─ Prós: Oficial, confiável, bem documentada
    ├─ Contras: Apenas inglês, requer chave API para uso pesado
    └─ Fallback em: N/A (intervenção manual)
```

### Estratégia de Caching

| Tipo de Dado | Camada de Cache | TTL | Invalidação |
|--------------|-----------------|-----|-------------|
| Dados de cartas | Redis + PostgreSQL | 24h | Tarefa de sincronização manual |
| Dados de torneios | PostgreSQL | 1h | Sincronização em background (a cada hora) |
| Artigos de notícias | PostgreSQL | 30m | Sincronização em background (30m) |
| Snapshots do meta | PostgreSQL | N/A | Atualização manual |
| Respostas da API | Redis | 1h | Expiração por TTL |

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
                    # Fallback para Pokemon TCG API
                    return await pokemon_api_client.fetch_card(...)
                raise
```

### Arquitetura do Cliente da API

```python
# Cliente base com lógica de retry
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

# Implementações concretas
class TCGdexClient(BaseAPIClient): ...
class PokemonTCGClient(BaseAPIClient): ...
class LimitlessClient(BaseAPIClient): ...
```

---

## 9. Decisões de Design Principais

### 1. Bilíngue Primeiro (name_en / name_pt)

**Decisão**: Armazenar nomes em Inglês e Português em todos os modelos de banco de dados

**Justificativa**:
- Base de usuários principal é falantes de Inglês e Português
- Evita lookups de tradução em tempo de execução
- Permite filtragem eficiente em ambos os idiomas
- Simplifica respostas da API (sempre inclui ambos)

**Implementação**:
```python
class Card(Base):
    __tablename__ = "cards"

    name_en = Column(String, nullable=False, index=True)
    name_pt = Column(String, nullable=False, index=True)

    @property
    def name(self, lang: Language = Language.EN) -> str:
        return self.name_en if lang == Language.EN else self.name_pt
```

### 2. user_id = 1 fixo (Auth Planejada)

**Decisão**: Usar `user_id = 1` fixo para todas as operações na v3.0

**Justificativa**:
- Sistema de autenticação está planejado para v3.1
- Evita bloquear desenvolvimento na implementação de auth
- Esquema de banco de dados já suporta múltiplos usuários
- Caminho de migração fácil (apenas adicionar middleware de auth)

**Implementação**:
```python
# Atual (v3.0)
CURRENT_USER_ID = 1

@router.get("/decks")
async def list_decks(db: DBSession):
    return await DeckService.get_user_decks(db, user_id=CURRENT_USER_ID)

# Futuro (v3.1)
@router.get("/decks")
async def list_decks(db: DBSession, user: User = Depends(get_current_user)):
    return await DeckService.get_user_decks(db, user_id=user.id)
```

### 3. SSE para Streaming de IA

**Decisão**: Usar Server-Sent Events para streaming de respostas de IA

**Justificativa**:
- Suporte nativo do navegador (EventSource API)
- Mais simples que WebSockets para streaming unidirecional
- Funciona com infraestrutura HTTP padrão
- Perfeito para streaming da API Claude

**Implementação**:
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

### 4. selectinload para Eager Loading

**Decisão**: Usar `selectinload()` do SQLAlchemy para relacionamentos

**Justificativa**:
- Evita problema de consultas N+1
- Funciona com sessões assíncronas
- Mais eficiente que `joinedload` para one-to-many
- Controle explícito sobre dados carregados

**Implementação**:
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

### 5. Pydantic v2 com from_attributes

**Decisão**: Usar Pydantic v2 com `model_config = ConfigDict(from_attributes=True)`

**Justificativa**:
- Melhor desempenho que v1
- `from_attributes` substitui `orm_mode`
- Suporte a validador assíncrono nativo
- Geração aprimorada de JSON schema

**Implementação**:
```python
from pydantic import BaseModel, ConfigDict

class DeckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int
    cards: list[CardInDeck]

    # Funciona com modelos SQLAlchemy
    # deck = Deck(...) -> DeckResponse.model_validate(deck)
```

### 6. Lógica Core Modular

**Decisão**: Separar lógica de domínio pura de serviços

**Justificativa**:
- Testável sem dependências de banco de dados/API
- Reutilizável em diferentes interfaces (CLI, API, mobile)
- Separação clara de responsabilidades
- Fácil de portar lógica para outras linguagens se necessário

**Exemplo**:
```python
# core/deck_parser.py (função pura)
def parse_deck(text: str) -> ParsedDeck:
    # Sem DB, sem API, apenas lógica
    lines = text.strip().split('\n')
    cards = []
    for line in lines:
        if match := CARD_LINE_REGEX.match(line):
            cards.append(parse_card_line(match))
    return ParsedDeck(cards=cards)

# services/deck_service.py (orquestração)
async def import_deck(db: AsyncSession, text: str):
    parsed = parse_deck(text)  # Lógica pura
    cards = await resolve_cards(db, parsed.cards)  # I/O
    deck = await create_deck(db, cards)  # I/O
    return deck
```

---

## 10. Considerações de Segurança

### Configuração CORS

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Desenvolvimento
        "https://tcgtool.app"     # Produção
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Validação de Entrada

Todas as entradas validadas com schemas Pydantic:

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

### Gerenciamento de Chaves de API

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
    SECRET_KEY: str  # Para auth futura

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**Variáveis de Ambiente** (nunca commitadas):
```bash
# .env (não no git)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/tcg_tool
CLAUDE_API_KEY=sk-ant-...
SECRET_KEY=random-secret-key
```

### Prevenção de SQL Injection

ORM SQLAlchemy previne SQL injection:

```python
# Seguro (parametrizado)
stmt = select(Card).where(Card.name_en.ilike(f"%{user_input}%"))

# NUNCA faça isso (vulnerável)
# db.execute(f"SELECT * FROM cards WHERE name LIKE '%{user_input}%'")
```

### Sanitização de Dados

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

## 11. Roadmap Futuro

### v3.1 - Autenticação & Autorização

**Cronograma**: Q2 2026

**Recursos**:
- Registro e login de usuários
- Autenticação baseada em JWT
- Hashing de senhas (bcrypt)
- Rotas protegidas (privacidade de decks)
- Verificação de email
- Fluxo de reset de senha

**Stack Tecnológica**:
- Utilitários de Segurança FastAPI
- python-jose (JWT)
- passlib (hashing de senha)
- FastAPI-Mail (email)

### v3.2 - Otimização de Caching Redis

**Cronograma**: Q2 2026

**Recursos**:
- Caching distribuído para respostas da API
- Gerenciamento de sessão
- Armazenamento de rate limiting
- Contadores de visualizações de deck em tempo real
- Rastreamento de buscas populares

**Stack Tecnológica**:
- redis-py (async)
- FastAPI-Cache2
- Decoradores de cache customizados

### v3.3 - PWA Mobile

**Cronograma**: Q3 2026

**Recursos**:
- Progressive Web App (PWA)
- Suporte offline
- Notificações push
- Adicionar à tela inicial
- Integração com câmera (scan de cartas)
- UI otimizada para mobile

**Stack Tecnológica**:
- Plugin PWA Next.js
- Workbox (service workers)
- IndexedDB (armazenamento offline)

### v3.4 - Aprimoramento de Análise de Vídeo

**Cronograma**: Q3 2026

**Recursos**:
- Reconhecimento automático de cartas (OCR)
- Detecção e segmentação de turnos
- Integração de calculadora de probabilidades
- Análise multi-jogo
- Exportação para editor de vídeo

**Stack Tecnológica**:
- Claude Vision API
- OpenCV (processamento de vídeo)
- Tesseract OCR
- FFmpeg (manipulação de vídeo)

### v4.0 - App Mobile Nativo

**Cronograma**: Q4 2026

**Recursos**:
- App mobile React Native
- Integração nativa de câmera
- Modo offline com sincronização
- Preview de carta em AR
- Suporte NFC (cartas futuras)

**Stack Tecnológica**:
- React Native
- Expo
- React Native Camera
- AsyncStorage
- Sincronização em background

### Considerações Futuras

- **Integração Blockchain**: Rastreamento de propriedade de cartas NFT
- **Marketplace**: Plataforma de trading de cartas
- **Gerenciamento de Torneios**: Organizar eventos locais
- **Live Streaming**: Integração com Twitch/YouTube
- **Recursos Sociais**: Seguir jogadores, compartilhar decks
- **Nível Premium**: Analytics avançados, recursos de IA

---

## Apêndice A: Esquema do Banco de Dados

### Tabelas Principais

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

## Apêndice B: Resumo de Endpoints da API

### API de Cartas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/cards` | Listar todas as cartas |
| GET | `/api/v1/cards/search` | Buscar cartas |
| GET | `/api/v1/cards/{id}` | Obter carta por ID |
| GET | `/api/v1/cards/sets` | Listar todos os sets |
| GET | `/api/v1/cards/sets/{set_id}` | Obter cartas no set |

### API de Decks

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/decks` | Listar decks do usuário |
| POST | `/api/v1/decks` | Criar novo deck |
| GET | `/api/v1/decks/{id}` | Obter detalhe do deck |
| PUT | `/api/v1/decks/{id}` | Atualizar deck |
| DELETE | `/api/v1/decks/{id}` | Deletar deck |
| POST | `/api/v1/decks/import` | Importar deck de texto |
| GET | `/api/v1/decks/{id}/export` | Exportar deck para formato PTCGO |

### API de Análise

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/analysis/rotation` | Analisar impacto de rotação |
| POST | `/api/v1/analysis/matchup` | Calcular matchup |
| POST | `/api/v1/analysis/compare` | Comparar dois decks |
| POST | `/api/v1/analysis/substitution` | Obter substituições de cartas |

### API de IA

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/ai/chat` | Chat com IA (stream SSE) |
| POST | `/api/v1/ai/video` | Analisar vídeo de partida |
| POST | `/api/v1/ai/recommend` | Obter recomendações de deck |

### API do Meta

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/meta/decks` | Listar decks meta |
| GET | `/api/v1/meta/decks/{id}` | Obter detalhe do deck meta |
| GET | `/api/v1/meta/matchups` | Obter matriz de matchups |
| GET | `/api/v1/meta/tiers` | Obter tier list |

---

## Histórico de Revisões

| Versão | Data | Autor | Mudanças |
|---------|------|--------|----------|
| 1.0 | 2026-02-15 | Bruno Strumendo | Documento inicial de arquitetura |

---

**Fim do Documento**
