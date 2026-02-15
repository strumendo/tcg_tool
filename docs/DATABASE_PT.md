# DATABASE.md - Referência do Esquema do Banco de Dados

**Autor:** Bruno Strumendo
**Projeto:** TCG Tool v3.0
**Banco de Dados:** PostgreSQL
**Última Atualização:** 2026-02-15

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Diagrama de Relacionamento de Entidades](#diagrama-de-relacionamento-de-entidades)
3. [Esquemas de Tabelas](#esquemas-de-tabelas)
4. [Índices](#índices)
5. [Sistema de Marcas de Regulação](#sistema-de-marcas-de-regulação)
6. [Guia de Migrações](#guia-de-migrações)
7. [Guia de Seeding](#guia-de-seeding)
8. [Exemplos de Consultas](#exemplos-de-consultas)

---

## Visão Geral

O banco de dados TCG Tool v3.0 consiste em **17 tabelas** organizadas nos seguintes domínios:

| Domínio | Tabelas | Propósito |
|---------|---------|-----------|
| **Gerenciamento de Usuários** | `users` | Contas de usuários e preferências |
| **Dados de Cartas** | `card_sets`, `cards`, `card_abilities`, `card_attacks`, `card_functions` | Base de dados completa de cartas com habilidades, ataques e funções |
| **Decks de Usuários** | `decks`, `deck_cards` | Coleção pessoal de decks e construção de decks |
| **Análise Meta** | `meta_decks`, `meta_deck_cards`, `meta_matchups` | Base de dados meta competitiva e dados de matchup |
| **Rastreamento de Batalhas** | `battles`, `battle_actions` | Histórico de partidas e dados de replay |
| **Coleção** | `user_collection` | Rastreamento de propriedade de cartas |
| **Estatísticas** | `card_usage_stats`, `deck_usage_stats` | Analytics de uso e tendências do meta |
| **Dados Externos** | `tournaments`, `news_articles` | Calendário de torneios e feed de notícias |

**Stack Tecnológica:**
- PostgreSQL 14+
- SQLAlchemy ORM
- Migrações Alembic
- JSONB para estruturas de dados flexíveis

---

## Diagrama de Relacionamento de Entidades

```mermaid
erDiagram
    users ||--o{ decks : owns
    users ||--o{ battles : plays
    users ||--o{ user_collection : has

    card_sets ||--o{ cards : contains

    cards ||--o{ card_abilities : has
    cards ||--o{ card_attacks : has
    cards ||--o{ card_functions : has
    cards ||--o{ deck_cards : used_in
    cards ||--o{ meta_deck_cards : used_in
    cards ||--o{ user_collection : owned
    cards ||--o{ card_usage_stats : tracked

    decks ||--o{ deck_cards : contains
    decks ||--o{ battles : used_in

    meta_decks ||--o{ meta_deck_cards : contains
    meta_decks ||--o{ meta_matchups : participates_in_a
    meta_decks ||--o{ meta_matchups : participates_in_b
    meta_decks ||--o{ battles : opponent

    battles ||--o{ battle_actions : contains

    users {
        SERIAL id PK
        VARCHAR username
        VARCHAR email
        VARCHAR language
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    card_sets {
        SERIAL id PK
        VARCHAR code UK
        VARCHAR tcgdex_id
        VARCHAR name_en
        VARCHAR name_pt
        VARCHAR regulation_mark
        TIMESTAMPTZ release_date
        INTEGER total_cards
        BOOLEAN is_legal
        TIMESTAMPTZ created_at
    }

    cards {
        SERIAL id PK
        VARCHAR name_en
        VARCHAR name_pt
        VARCHAR card_type
        VARCHAR trainer_subtype
        INTEGER set_id FK
        VARCHAR set_number
        VARCHAR regulation_mark
        INTEGER hp
        VARCHAR energy_type
        VARCHAR stage
        BOOLEAN is_ex
        VARCHAR image_url
        VARCHAR tcgdex_id
        VARCHAR pokemontcg_id
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    decks {
        SERIAL id PK
        INTEGER user_id FK
        VARCHAR name
        VARCHAR archetype
        TEXT notes
        BOOLEAN is_active
        BOOLEAN is_valid
        INTEGER total_cards
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    meta_decks {
        VARCHAR id PK
        VARCHAR name_en
        VARCHAR name_pt
        INTEGER tier
        TEXT description_en
        JSONB key_pokemon
        NUMERIC meta_share
        DATE snapshot_date
        TIMESTAMPTZ created_at
    }

    battles {
        SERIAL id PK
        INTEGER user_id FK
        INTEGER deck_id FK
        VARCHAR opponent_deck_name
        VARCHAR result
        INTEGER total_turns
        BOOLEAN went_first
        TIMESTAMPTZ played_at
        TIMESTAMPTZ created_at
    }
```

---

## Esquemas de Tabelas

### 1. users

Contas de usuários e preferências para a aplicação TCG Tool.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE,
    language VARCHAR(2) DEFAULT 'en' CHECK (language IN ('en', 'pt')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `username`: Nome de usuário único (3-50 caracteres)
- `email`: Email opcional para notificações
- `language`: Preferência de idioma da UI (en/pt)
- `created_at`: Timestamp de criação da conta
- `updated_at`: Timestamp da última atualização do perfil

**Restrições:**
- `username` deve ser único e não nulo
- `email` deve ser único se fornecido
- `language` deve ser 'en' ou 'pt'

---

### 2. card_sets

Informações de sets Pokemon TCG com marcas de regulação e legalidade.

```sql
CREATE TABLE card_sets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    tcgdex_id VARCHAR(20),
    name_en VARCHAR(200) NOT NULL,
    name_pt VARCHAR(200),
    regulation_mark VARCHAR(1) CHECK (regulation_mark IN ('F', 'G', 'H', 'I')),
    release_date TIMESTAMPTZ,
    total_cards INTEGER,
    is_legal BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_card_sets_code ON card_sets(code);
CREATE INDEX idx_card_sets_regulation_mark ON card_sets(regulation_mark);
CREATE INDEX idx_card_sets_is_legal ON card_sets(is_legal);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `code`: Código do set (ex: "sv1", "sv3", "PAL", "OBF")
- `tcgdex_id`: Identificador da API TCGdex
- `name_en`: Nome do set em inglês (ex: "Scarlet & Violet")
- `name_pt`: Nome do set em português
- `regulation_mark`: Marcador de legalidade F/G/H/I
- `release_date`: Data oficial de lançamento
- `total_cards`: Número de cartas no set
- `is_legal`: Status de legalidade atual no formato Standard
- `created_at`: Timestamp de criação do registro

**Códigos de Sets Comuns:**
- `sv1` = Scarlet & Violet (SVI)
- `sv2` = Paldea Evolved (PAL)
- `sv3` = Obsidian Flames (OBF)
- `sv4` = Paradox Rift (PAR)
- `sv5` = Temporal Forces (TEF)
- `sv6` = Twilight Masquerade (TWM)
- `sv7` = Shrouded Fable (SFA)
- `sv8` = Stellar Crown (SCR)
- `sv9` = Surging Sparks (SSP)
- `sv10` = Prismatic Evolutions (PRE)
- `sv11` = Journey Together (JTG)
- `sv12` = Astranova Clash (ASC)

---

### 3. cards

Base de dados completa de cartas com suporte multilíngue e metadados.

```sql
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(200) NOT NULL,
    name_pt VARCHAR(200),
    card_type VARCHAR(20) NOT NULL CHECK (card_type IN ('pokemon', 'trainer', 'energy')),
    trainer_subtype VARCHAR(20) CHECK (trainer_subtype IN ('item', 'supporter', 'stadium', 'tool')),
    set_id INTEGER NOT NULL REFERENCES card_sets(id) ON DELETE CASCADE,
    set_number VARCHAR(10),
    regulation_mark VARCHAR(1) CHECK (regulation_mark IN ('F', 'G', 'H', 'I')),
    hp INTEGER CHECK (hp > 0),
    energy_type VARCHAR(20),
    stage VARCHAR(20) CHECK (stage IN ('Basic', 'Stage 1', 'Stage 2', 'VMAX', 'VSTAR', 'ex')),
    is_ex BOOLEAN DEFAULT FALSE,
    image_url VARCHAR(500),
    image_url_hires VARCHAR(500),
    tcgdex_id VARCHAR(50),
    pokemontcg_id VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(set_id, set_number)
);

CREATE INDEX idx_cards_name_en ON cards(name_en);
CREATE INDEX idx_cards_name_pt ON cards(name_pt);
CREATE INDEX idx_cards_card_type ON cards(card_type);
CREATE INDEX idx_cards_set_id ON cards(set_id);
CREATE INDEX idx_cards_regulation_mark ON cards(regulation_mark);
CREATE INDEX idx_cards_is_ex ON cards(is_ex);
CREATE INDEX idx_cards_tcgdex_id ON cards(tcgdex_id);
CREATE INDEX idx_cards_pokemontcg_id ON cards(pokemontcg_id);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `name_en`: Nome da carta em inglês (ex: "Charizard ex")
- `name_pt`: Nome da carta em português (ex: "Charizard ex")
- `card_type`: pokemon/trainer/energy
- `trainer_subtype`: item/supporter/stadium/tool (se trainer)
- `set_id`: Chave estrangeira para card_sets
- `set_number`: Número da carta no set (ex: "125")
- `regulation_mark`: Marcador de legalidade F/G/H/I
- `hp`: Pontos de vida (apenas Pokemon)
- `energy_type`: Fire/Water/Grass/etc. (apenas Pokemon)
- `stage`: Basic/Stage 1/Stage 2/ex/VMAX/VSTAR
- `is_ex`: True se a carta é Pokemon ex/EX/GX/V/VMAX/VSTAR
- `image_url`: URL da imagem em resolução padrão
- `image_url_hires`: URL da imagem em alta resolução
- `tcgdex_id`: Identificador da API TCGdex
- `pokemontcg_id`: Identificador da API Pokemon TCG
- `created_at`: Timestamp de criação do registro
- `updated_at`: Timestamp da última atualização

**Restrições:**
- Cada carta deve ter uma combinação única de `set_id` e `set_number`
- Cartas de Energia Básica são sempre legais independentemente do set ou marca de regulação

---

### 4. card_abilities

Habilidades de Pokemon (efeitos passivos) com descrições multilíngues.

```sql
CREATE TABLE card_abilities (
    id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    name_en VARCHAR(200),
    name_pt VARCHAR(200),
    effect_en TEXT,
    effect_pt TEXT,
    category VARCHAR(30) CHECK (category IN (
        'DRAW', 'SEARCH', 'RECOVERY', 'SWITCHING', 'ENERGY_ACCEL',
        'DISRUPTION', 'DAMAGE', 'HEALING', 'PROTECTION', 'OTHER'
    )),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_card_abilities_card_id ON card_abilities(card_id);
CREATE INDEX idx_card_abilities_category ON card_abilities(category);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `card_id`: Chave estrangeira para tabela cards
- `name_en`: Nome da habilidade em inglês (ex: "Knock Back")
- `name_pt`: Nome da habilidade em português
- `effect_en`: Texto da habilidade em inglês
- `effect_pt`: Texto da habilidade em português
- `category`: Categoria funcional (DRAW/SEARCH/etc.)
- `created_at`: Timestamp de criação do registro

**Categorias:**
- `DRAW`: Efeitos de compra de cartas
- `SEARCH`: Busca em deck/descarte
- `RECOVERY`: Cura ou restauração
- `SWITCHING`: Efeitos de recuo ou troca
- `ENERGY_ACCEL`: Aceleração de anexação de energia
- `DISRUPTION`: Disrupção do oponente
- `DAMAGE`: Habilidades que causam dano
- `HEALING`: Recuperação de HP
- `PROTECTION`: Redução de dano ou imunidade
- `OTHER`: Efeitos diversos

---

### 5. card_attacks

Ataques de Pokemon com dano, custo de energia e efeitos.

```sql
CREATE TABLE card_attacks (
    id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    name_en VARCHAR(200),
    name_pt VARCHAR(200),
    damage VARCHAR(20),
    energy_cost JSONB,
    effect_en TEXT,
    effect_pt TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_card_attacks_card_id ON card_attacks(card_id);
CREATE INDEX idx_card_attacks_energy_cost ON card_attacks USING GIN(energy_cost);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `card_id`: Chave estrangeira para tabela cards
- `name_en`: Nome do ataque em inglês (ex: "Burning Darkness")
- `name_pt`: Nome do ataque em português
- `damage`: Dano base (ex: "180", "30+", "")
- `energy_cost`: Array JSONB de tipos de energia (ex: `["Fire", "Fire", "Colorless"]`)
- `effect_en`: Texto do efeito do ataque em inglês
- `effect_pt`: Texto do efeito do ataque em português
- `created_at`: Timestamp de criação do registro

**Exemplos de Custo de Energia:**
```json
["Fire", "Fire", "Colorless"]
["Water", "Colorless", "Colorless"]
["Darkness"]
[]
```

---

### 6. card_functions

Tags funcionais de cartas para construção de deck e análise.

```sql
CREATE TABLE card_functions (
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    function VARCHAR(20) NOT NULL CHECK (function IN (
        'DRAW', 'SEARCH', 'RECOVERY', 'SWITCHING', 'ENERGY_ACCEL',
        'DISRUPTION', 'DAMAGE', 'HEALING', 'PROTECTION', 'OTHER'
    )),
    PRIMARY KEY (card_id, function)
);

CREATE INDEX idx_card_functions_function ON card_functions(function);
```

**Campos:**
- `card_id`: Chave estrangeira para tabela cards
- `function`: Tag de categoria funcional

**Uso:**
- Uma única carta pode ter múltiplas funções
- Usado para análise de deck (ex: "Quantas cartas de compra neste deck?")
- Suporta sugestões de substituição (ex: "Substituir esta carta de DRAW por outra carta de DRAW")

**Tipos de Função:**
- `DRAW`: Compra de cartas (Professor's Research, Iono)
- `SEARCH`: Busca em deck/descarte (Ultra Ball, Nest Ball)
- `RECOVERY`: Recuperação de cartas (Super Rod, Counter Catcher)
- `SWITCHING`: Recuo/troca (Switch, Boss's Orders)
- `ENERGY_ACCEL`: Aceleração de energia (Rare Candy, Energy Switch)
- `DISRUPTION`: Disrupção do oponente (Iono, Judge)
- `DAMAGE`: Dano direto (Radiant Greninja, Manaphy)
- `HEALING`: Cura de HP (Pokémon Center Lady)
- `PROTECTION`: Proteção contra dano (Manaphy, Path to the Peak)
- `OTHER`: Utilidade diversa

---

### 7. decks

Decks criados por usuários com metadados e status de validação.

```sql
CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    archetype VARCHAR(50),
    notes TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    is_valid BOOLEAN DEFAULT FALSE,
    total_cards INTEGER DEFAULT 0 CHECK (total_cards BETWEEN 0 AND 60),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_decks_user_id ON decks(user_id);
CREATE INDEX idx_decks_archetype ON decks(archetype);
CREATE INDEX idx_decks_is_active ON decks(is_active);
CREATE INDEX idx_decks_is_valid ON decks(is_valid);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `user_id`: Chave estrangeira para tabela users
- `name`: Nome do deck definido pelo usuário
- `archetype`: Arquétipo do deck (ex: "charizard-pidgeot", "lugia-archeops")
- `notes`: Notas do usuário sobre o deck
- `is_active`: Se este é o deck ativo atual do usuário
- `is_valid`: Se o deck passa na validação (60 cartas, regra de 4 cópias, etc.)
- `total_cards`: Contagem total de cartas computada
- `created_at`: Timestamp de criação do deck
- `updated_at`: Timestamp da última modificação

**Regras de Validação:**
- Exatamente 60 cartas
- Máximo de 4 cópias de qualquer carta (exceto Energia Básica)
- Pelo menos 1 Pokemon Básico
- Todas as cartas devem ser legais no formato Standard

---

### 8. deck_cards

Quantidades de cartas em decks de usuários (tabela de junção).

```sql
CREATE TABLE deck_cards (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id),
    quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 60),
    UNIQUE(deck_id, card_id)
);

CREATE INDEX idx_deck_cards_deck_id ON deck_cards(deck_id);
CREATE INDEX idx_deck_cards_card_id ON deck_cards(card_id);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `deck_id`: Chave estrangeira para tabela decks
- `card_id`: Chave estrangeira para tabela cards
- `quantity`: Número de cópias (1-60)

**Restrições:**
- Cada carta pode aparecer no máximo uma vez por deck (combinação única)
- Quantidade deve estar entre 1 e 60
- Máximo de 4 cópias aplicado no nível da aplicação (exceto Energia Básica)

---

### 9. meta_decks

Arquétipos de decks meta competitivos com rankings de tier e dados de matchup.

```sql
CREATE TABLE meta_decks (
    id VARCHAR(50) PRIMARY KEY,
    name_en VARCHAR(200) NOT NULL,
    name_pt VARCHAR(200) NOT NULL,
    tier INTEGER NOT NULL CHECK (tier BETWEEN 1 AND 3),
    description_en TEXT,
    description_pt TEXT,
    strategy_en TEXT,
    strategy_pt TEXT,
    difficulty VARCHAR(20) CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    meta_share NUMERIC(5,2) CHECK (meta_share BETWEEN 0 AND 100),
    key_pokemon JSONB,
    energy_types JSONB,
    strengths_en JSONB,
    strengths_pt JSONB,
    weaknesses_en JSONB,
    weaknesses_pt JSONB,
    snapshot_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_meta_decks_tier ON meta_decks(tier);
CREATE INDEX idx_meta_decks_meta_share ON meta_decks(meta_share DESC);
CREATE INDEX idx_meta_decks_snapshot_date ON meta_decks(snapshot_date);
```

**Campos:**
- `id`: Identificador do arquétipo (ex: "charizard-pidgeot", "lugia-archeops")
- `name_en`: Nome do deck em inglês
- `name_pt`: Nome do deck em português
- `tier`: Tier competitivo (1=top tier, 2=competitivo, 3=rogue)
- `description_en`: Descrição do deck em inglês
- `description_pt`: Descrição do deck em português
- `strategy_en`: Guia de estratégia em inglês
- `strategy_pt`: Guia de estratégia em português
- `difficulty`: Requisito de habilidade (Easy/Medium/Hard)
- `meta_share`: Porcentagem do meta competitivo (0-100)
- `key_pokemon`: Array JSONB de Pokemon chave (ex: `["Charizard ex", "Pidgeot ex"]`)
- `energy_types`: Array JSONB de tipos de energia (ex: `["Fire", "Colorless"]`)
- `strengths_en`: Array JSONB de descrições de forças em inglês
- `strengths_pt`: Array JSONB de descrições de forças em português
- `weaknesses_en`: Array JSONB de descrições de fraquezas em inglês
- `weaknesses_pt`: Array JSONB de descrições de fraquezas em português
- `snapshot_date`: Data do snapshot do meta
- `created_at`: Timestamp de criação do registro
- `updated_at`: Timestamp da última atualização

**Exemplos JSONB:**
```json
{
  "key_pokemon": ["Charizard ex", "Pidgeot ex", "Radiant Charizard"],
  "energy_types": ["Fire"],
  "strengths_en": ["Fast setup", "High damage output", "Consistent draw"],
  "weaknesses_en": ["Water weakness", "Energy-dependent", "Prize trade issues"]
}
```

---

### 10. meta_deck_cards

Listas de cartas para arquétipos de decks meta (tabela de junção).

```sql
CREATE TABLE meta_deck_cards (
    id SERIAL PRIMARY KEY,
    meta_deck_id VARCHAR(50) NOT NULL REFERENCES meta_decks(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id),
    quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 60),
    UNIQUE(meta_deck_id, card_id)
);

CREATE INDEX idx_meta_deck_cards_meta_deck_id ON meta_deck_cards(meta_deck_id);
CREATE INDEX idx_meta_deck_cards_card_id ON meta_deck_cards(card_id);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `meta_deck_id`: Chave estrangeira para tabela meta_decks
- `card_id`: Chave estrangeira para tabela cards
- `quantity`: Número de cópias (1-60)

**Uso:**
- Armazena a decklist "padrão" ou "de referência" para cada arquétipo meta
- Usado para comparação de decks e sugestões
- Deve totalizar exatamente 60 cartas por deck meta

---

### 11. meta_matchups

Dados de matchup head-to-head entre decks meta.

```sql
CREATE TABLE meta_matchups (
    id SERIAL PRIMARY KEY,
    deck_a_id VARCHAR(50) NOT NULL REFERENCES meta_decks(id) ON DELETE CASCADE,
    deck_b_id VARCHAR(50) NOT NULL REFERENCES meta_decks(id) ON DELETE CASCADE,
    win_rate_a NUMERIC(5,2) NOT NULL CHECK (win_rate_a BETWEEN 0 AND 100),
    notes_en TEXT,
    notes_pt TEXT,
    snapshot_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(deck_a_id, deck_b_id),
    CHECK (deck_a_id < deck_b_id)
);

CREATE INDEX idx_meta_matchups_deck_a_id ON meta_matchups(deck_a_id);
CREATE INDEX idx_meta_matchups_deck_b_id ON meta_matchups(deck_b_id);
CREATE INDEX idx_meta_matchups_snapshot_date ON meta_matchups(snapshot_date);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `deck_a_id`: Primeiro deck (ID alfabeticamente menor)
- `deck_b_id`: Segundo deck (ID alfabeticamente maior)
- `win_rate_a`: Taxa de vitória do deck_a vs deck_b (0-100)
- `notes_en`: Notas do matchup em inglês
- `notes_pt`: Notas do matchup em português
- `snapshot_date`: Data do snapshot do meta

**Restrições:**
- `deck_a_id` deve estar alfabeticamente antes de `deck_b_id` (previne duplicatas)
- `win_rate_a` representa a porcentagem de vitória do deck A
- Para obter a taxa de vitória do deck B: `100 - win_rate_a`

**Interpretação de Matchup:**
- 55%+ = Favorável
- 46-54% = Equilibrado
- 45% ou menos = Desfavorável

**Exemplo:**
```sql
-- Charizard vs Lugia: Charizard vence 58% das vezes
INSERT INTO meta_matchups (deck_a_id, deck_b_id, win_rate_a)
VALUES ('charizard-pidgeot', 'lugia-archeops', 58.0);
```

---

### 12. battles

Histórico de partidas de usuários com resultados e metadados.

```sql
CREATE TABLE battles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    deck_id INTEGER REFERENCES decks(id) ON DELETE SET NULL,
    opponent_deck_name VARCHAR(200),
    opponent_meta_deck_id VARCHAR(50) REFERENCES meta_decks(id) ON DELETE SET NULL,
    result VARCHAR(10) NOT NULL CHECK (result IN ('win', 'loss', 'tie')),
    total_turns INTEGER CHECK (total_turns > 0),
    went_first BOOLEAN,
    notes TEXT,
    source VARCHAR(20) DEFAULT 'manual' CHECK (source IN ('manual', 'video', 'import')),
    source_url VARCHAR(500),
    played_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_battles_user_id ON battles(user_id);
CREATE INDEX idx_battles_deck_id ON battles(deck_id);
CREATE INDEX idx_battles_opponent_meta_deck_id ON battles(opponent_meta_deck_id);
CREATE INDEX idx_battles_result ON battles(result);
CREATE INDEX idx_battles_played_at ON battles(played_at DESC);
CREATE INDEX idx_battles_source ON battles(source);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `user_id`: Chave estrangeira para tabela users
- `deck_id`: Chave estrangeira para tabela decks (nullable se deck deletado)
- `opponent_deck_name`: Nome do deck oponente em texto livre
- `opponent_meta_deck_id`: Chave estrangeira para meta_decks se arquétipo reconhecido
- `result`: win/loss/tie
- `total_turns`: Número de turnos na partida
- `went_first`: Se o usuário começou primeiro
- `notes`: Notas do usuário sobre a partida
- `source`: Como a partida foi registrada (manual/video/import)
- `source_url`: URL para vídeo da partida (se aplicável)
- `played_at`: Quando a partida foi jogada
- `created_at`: Quando o registro foi criado

**Uso:**
- Rastrear registros de vitórias/derrotas contra arquétipos específicos
- Analisar taxas de vitória começando primeiro vs segundo
- Link para replays de vídeo para revisão
- Futuro: integração de análise de vídeo com IA

---

### 13. battle_actions

Log de ações turno a turno para replays de partidas.

```sql
CREATE TABLE battle_actions (
    id SERIAL PRIMARY KEY,
    battle_id INTEGER NOT NULL REFERENCES battles(id) ON DELETE CASCADE,
    turn INTEGER NOT NULL CHECK (turn > 0),
    player VARCHAR(10) NOT NULL CHECK (player IN ('user', 'opponent')),
    action_type VARCHAR(30) NOT NULL CHECK (action_type IN (
        'attach_energy', 'play_supporter', 'play_item', 'play_stadium',
        'evolve', 'attack', 'switch', 'retreat', 'ability', 'knockout', 'other'
    )),
    card_name VARCHAR(200),
    details TEXT,
    sequence_order INTEGER NOT NULL,
    UNIQUE(battle_id, turn, player, sequence_order)
);

CREATE INDEX idx_battle_actions_battle_id ON battle_actions(battle_id);
CREATE INDEX idx_battle_actions_turn ON battle_actions(turn);
CREATE INDEX idx_battle_actions_action_type ON battle_actions(action_type);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `battle_id`: Chave estrangeira para tabela battles
- `turn`: Número do turno (baseado em 1)
- `player`: user/opponent
- `action_type`: Tipo de ação realizada
- `card_name`: Nome da carta envolvida (se aplicável)
- `details`: Detalhes adicionais da ação (ex: "Comprou 3 cartas")
- `sequence_order`: Ordem das ações dentro do turno/jogador

**Tipos de Ação:**
- `attach_energy`: Anexação de energia
- `play_supporter`: Carta de Supporter jogada
- `play_item`: Carta de Item jogada
- `play_stadium`: Carta de Stadium jogada
- `evolve`: Evolução de Pokemon
- `attack`: Declaração de ataque
- `switch`: Troca de Pokemon ativo
- `retreat`: Recuo de Pokemon
- `ability`: Ativação de habilidade
- `knockout`: Pokemon nocauteado
- `other`: Ação diversa

**Uso Futuro:**
- Análise de vídeo com IA populará esta tabela
- Sistema de replay para revisão de partidas
- Análise de padrões (ex: "Taxas de uso de Supporter no Turno 1")

---

### 14. user_collection

Rastreamento de propriedade de cartas para gerenciamento de coleção.

```sql
CREATE TABLE user_collection (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id),
    quantity_owned INTEGER DEFAULT 0 CHECK (quantity_owned >= 0),
    UNIQUE(user_id, card_id)
);

CREATE INDEX idx_user_collection_user_id ON user_collection(user_id);
CREATE INDEX idx_user_collection_card_id ON user_collection(card_id);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `user_id`: Chave estrangeira para tabela users
- `card_id`: Chave estrangeira para tabela cards
- `quantity_owned`: Número de cópias possuídas (0+)

**Uso:**
- Rastrear quais cartas o usuário possui
- Validação de deck (só pode construir decks com cartas possuídas)
- Destacar cartas faltantes ao visualizar decks meta
- Importar de exportação de coleção do TCG Live

---

### 15. card_usage_stats

Estatísticas de popularidade e uso de cartas de dados de torneios.

```sql
CREATE TABLE card_usage_stats (
    id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL REFERENCES cards(id),
    format VARCHAR(20) DEFAULT 'Standard' CHECK (format IN ('Standard', 'Expanded', 'Unlimited')),
    usage_percentage NUMERIC(5,2) CHECK (usage_percentage BETWEEN 0 AND 100),
    avg_copies NUMERIC(3,1) CHECK (avg_copies BETWEEN 0 AND 60),
    sample_size INTEGER CHECK (sample_size > 0),
    snapshot_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(card_id, format, snapshot_date)
);

CREATE INDEX idx_card_usage_stats_card_id ON card_usage_stats(card_id);
CREATE INDEX idx_card_usage_stats_format ON card_usage_stats(format);
CREATE INDEX idx_card_usage_stats_snapshot_date ON card_usage_stats(snapshot_date);
CREATE INDEX idx_card_usage_stats_usage_percentage ON card_usage_stats(usage_percentage DESC);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `card_id`: Chave estrangeira para tabela cards
- `format`: Standard/Expanded/Unlimited
- `usage_percentage`: Porcentagem de decks usando esta carta (0-100)
- `avg_copies`: Número médio de cópias por deck (0-60)
- `sample_size`: Número de decks analisados
- `snapshot_date`: Data do snapshot de dados

**Uso:**
- Mostrar cartas em tendência ("50% dos decks usam Professor's Research")
- Comparar popularidade de cartas ao longo do tempo
- Sugerir escolhas de tech populares
- Dados originados do Limitless TCG

**Exemplo:**
```sql
-- Professor's Research está em 85% dos decks, média de 2.3 cópias
INSERT INTO card_usage_stats (card_id, usage_percentage, avg_copies, sample_size)
VALUES (1234, 85.0, 2.3, 500);
```

---

### 16. deck_usage_stats

Estatísticas de popularidade e desempenho de arquétipos de deck.

```sql
CREATE TABLE deck_usage_stats (
    id SERIAL PRIMARY KEY,
    archetype VARCHAR(100) NOT NULL,
    meta_share NUMERIC(5,2) CHECK (meta_share BETWEEN 0 AND 100),
    avg_placement NUMERIC(5,1) CHECK (avg_placement > 0),
    sample_size INTEGER CHECK (sample_size > 0),
    format VARCHAR(20) DEFAULT 'Standard' CHECK (format IN ('Standard', 'Expanded', 'Unlimited')),
    snapshot_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(archetype, format, snapshot_date)
);

CREATE INDEX idx_deck_usage_stats_archetype ON deck_usage_stats(archetype);
CREATE INDEX idx_deck_usage_stats_format ON deck_usage_stats(format);
CREATE INDEX idx_deck_usage_stats_snapshot_date ON deck_usage_stats(snapshot_date);
CREATE INDEX idx_deck_usage_stats_meta_share ON deck_usage_stats(meta_share DESC);
```

**Campos:**
- `id`: Chave primária auto-incrementada
- `archetype`: Nome do arquétipo do deck (ex: "Charizard ex / Pidgeot ex")
- `meta_share`: Porcentagem do meta de torneios (0-100)
- `avg_placement`: Colocação média em torneios (menor é melhor)
- `sample_size`: Número de resultados de torneios analisados
- `format`: Standard/Expanded/Unlimited
- `snapshot_date`: Data do snapshot de dados

**Uso:**
- Rastrear tendências do meta ao longo do tempo
- Mostrar arquétipos em ascensão/queda
- Análise de desempenho (meta share vs colocação média)
- Dados originados do Limitless TCG

**Exemplo:**
```sql
-- Charizard ex tem 18% de meta share, média de colocação 12.5
INSERT INTO deck_usage_stats (archetype, meta_share, avg_placement, sample_size)
VALUES ('Charizard ex / Pidgeot ex', 18.0, 12.5, 250);
```

---

### 17. tournaments

Calendário de torneios oficiais e competitivos.

```sql
CREATE TABLE tournaments (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    date DATE NOT NULL,
    end_date DATE,
    location VARCHAR(200),
    country VARCHAR(100),
    format VARCHAR(20) DEFAULT 'Standard' CHECK (format IN ('Standard', 'Expanded', 'Unlimited')),
    event_type VARCHAR(30) CHECK (event_type IN (
        'Regional', 'International', 'World Championship', 'League Cup', 'League Challenge', 'Other'
    )),
    url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tournaments_date ON tournaments(date DESC);
CREATE INDEX idx_tournaments_country ON tournaments(country);
CREATE INDEX idx_tournaments_format ON tournaments(format);
CREATE INDEX idx_tournaments_event_type ON tournaments(event_type);
```

**Campos:**
- `id`: Identificador do torneio (ex: "regional-orlando-2026-03")
- `name`: Nome do torneio
- `date`: Data de início
- `end_date`: Data de término (para eventos de múltiplos dias)
- `location`: Cidade ou local
- `country`: Código ou nome do país
- `format`: Standard/Expanded/Unlimited
- `event_type`: Regional/International/World Championship/etc.
- `url`: URL de informações do torneio
- `created_at`: Timestamp de criação do registro

**Uso:**
- Exibir calendário de torneios futuros
- Sincronizar com calendário do dispositivo (app Android)
- Link para resultados de torneios
- Dados originados de RK9 e Pokemon.com

---

### 18. news_articles

Feed de notícias Pokemon TCG do PokeBeach e outras fontes.

```sql
CREATE TABLE news_articles (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    url VARCHAR(500) NOT NULL,
    image_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'PokeBeach',
    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_news_articles_published_at ON news_articles(published_at DESC);
CREATE INDEX idx_news_articles_source ON news_articles(source);
```

**Campos:**
- `id`: Identificador do artigo (slug da URL ou hash)
- `title`: Título do artigo
- `summary`: Trecho ou descrição do artigo
- `url`: URL do artigo completo
- `image_url`: URL da imagem em destaque
- `source`: Fonte da notícia (PokeBeach/Pokemon.com/etc.)
- `published_at`: Timestamp de publicação original
- `created_at`: Timestamp de criação do registro

**Uso:**
- Exibir feed de notícias no app
- Integração RSS/API com PokeBeach
- Notificações push para breaking news
- Filtrar por fonte ou intervalo de datas

---

## Índices

### Chaves Primárias
Todas as tabelas têm chaves primárias com índices automáticos:
- `users(id)`, `card_sets(id)`, `cards(id)`, `decks(id)`, `battles(id)`, etc.

### Índices de Chave Estrangeira
Criados automaticamente em todas as colunas de chave estrangeira:
- `cards(set_id)`, `deck_cards(deck_id)`, `deck_cards(card_id)`, etc.

### Restrições Únicas
- `users(username)`, `users(email)`
- `card_sets(code)`
- `cards(set_id, set_number)`
- `deck_cards(deck_id, card_id)`
- `meta_deck_cards(meta_deck_id, card_id)`
- `meta_matchups(deck_a_id, deck_b_id)`
- `user_collection(user_id, card_id)`
- `card_usage_stats(card_id, format, snapshot_date)`
- `deck_usage_stats(archetype, format, snapshot_date)`

### Índices de Performance
- `cards(name_en)`, `cards(name_pt)` - Busca de nome de carta
- `cards(card_type)`, `cards(regulation_mark)` - Filtragem
- `decks(user_id)`, `decks(archetype)` - Consultas de decks de usuário
- `battles(played_at DESC)` - Partidas recentes
- `meta_decks(tier)`, `meta_decks(meta_share DESC)` - Rankings meta
- `tournaments(date DESC)` - Eventos futuros
- `news_articles(published_at DESC)` - Notícias recentes

### Índices JSONB (GIN)
- `card_attacks(energy_cost)` - Consultas de custo de energia
- Futuro: campos JSONB em `meta_decks` para consultas avançadas

---

## Sistema de Marcas de Regulação

Pokemon TCG usa marcas de regulação para determinar a legalidade de cartas no formato Standard.

### Marcas de Regulação Atuais (em 2026-02-15)

| Marca | Status | Sets | Notas |
|-------|--------|------|-------|
| **F** | Ilegal | Era Sword & Shield | Já rotacionado |
| **G** | **Rotacionando Março 2026** | SVI, PAL, OBF, MEW, PAR, PAF | 6 sets rotacionando |
| **H** | Legal | TEF, TWM, SFA, SCR, SSP | Standard atual |
| **I** | Legal | PRE, JTG, ASC, DRI, MEV | Sets mais recentes |

### Análise de Impacto de Rotação

A aplicação calcula o impacto de rotação para decks de usuários:

```sql
-- Contar cartas por marca de regulação em um deck
SELECT
    c.regulation_mark,
    COUNT(*) as card_count,
    SUM(dc.quantity) as total_copies
FROM deck_cards dc
JOIN cards c ON dc.card_id = c.id
WHERE dc.deck_id = $1
GROUP BY c.regulation_mark;
```

**Níveis de Severidade:**
- **NONE**: 0% do deck rotacionando
- **LOW**: 1-20% rotacionando
- **MODERATE**: 21-40% rotacionando
- **HIGH**: 41-60% rotacionando
- **CRITICAL**: 61%+ rotacionando

### Casos Especiais

**Energia Básica:**
- Sempre legal independentemente do set ou marca de regulação
- Identificada por padrão de nome da carta: "Basic {Type} Energy"
- Não deve contar para impacto de rotação

**Cartas Promo:**
- Usam marca de regulação da impressão equivalente do set principal
- Exemplo: Charizard ex promo (sv3.5) tem marca G

---

## Guia de Migrações

Este projeto usa **Alembic** para migrações de esquema de banco de dados.

### Configuração

```bash
# Instalar Alembic
pip install alembic psycopg2-binary

# Inicializar Alembic (primeira vez apenas)
alembic init alembic

# Configurar alembic.ini
# Definir: sqlalchemy.url = postgresql://user:pass@localhost/tcg_tool
```

### Comandos Comuns

```bash
# Criar uma nova migração
alembic revision -m "Add user_collection table"

# Gerar migração automaticamente a partir de modelos
alembic revision --autogenerate -m "Add card_functions table"

# Aplicar todas as migrações pendentes
alembic upgrade head

# Reverter última migração
alembic downgrade -1

# Mostrar revisão atual
alembic current

# Mostrar histórico de migrações
alembic history

# Atualizar para revisão específica
alembic upgrade abc123
```

### Exemplo de Migração

```python
# alembic/versions/001_create_users.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(200), unique=True),
        sa.Column('language', sa.String(2), server_default='en'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'))
    )
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_username', 'users')
    op.drop_table('users')
```

### Melhores Práticas

1. **Sempre revise migrações auto-geradas** - Alembic pode não detectar todas as mudanças
2. **Teste migrações em banco dev primeiro** - Nunca execute migrações não testadas em produção
3. **Inclua upgrade e downgrade** - Sempre forneça caminho de rollback
4. **Uma mudança lógica por migração** - Mais fácil de debugar e reverter
5. **Adicione migrações de dados separadamente** - Mantenha migrações de esquema e dados separadas

---

## Guia de Seeding

### Requisitos de Dados Iniciais

1. **Card Sets** - Popula todos os sets Scarlet & Violet
2. **Cards** - Importa da API TCGdex (10.000+ cartas)
3. **Meta Decks** - Importa 8 arquétipos top-tier
4. **Meta Deck Cards** - Decklists completas de 60 cartas
5. **Meta Matchups** - Importa 28 relacionamentos de matchup
6. **News Articles** - Importa artigos recentes do PokeBeach
7. **Tournaments** - Importa eventos futuros do RK9

### Scripts de Seed

```bash
# Executar todos os scripts de seed
python scripts/seed_database.py --all

# Seed de tabelas específicas
python scripts/seed_database.py --sets
python scripts/seed_database.py --cards
python scripts/seed_database.py --meta
python scripts/seed_database.py --news
python scripts/seed_database.py --tournaments
```

### Estratégia de Importação de Cartas

```python
# scripts/seed_cards.py
import httpx
from database import SessionLocal
from models import CardSet, Card

async def import_cards_from_tcgdex():
    """Importar todas as cartas Scarlet & Violet da API TCGdex"""
    async with httpx.AsyncClient() as client:
        # Buscar todos os sets
        response = await client.get("https://api.tcgdex.net/v2/en/sets")
        sets_data = response.json()

        for set_data in sets_data:
            if not set_data['id'].startswith('sv'):
                continue  # Pular sets não-SV

            # Buscar todas as cartas no set
            response = await client.get(f"https://api.tcgdex.net/v2/en/sets/{set_data['id']}")
            cards_data = response.json()

            # Inserir cartas...
```

### Importação de Deck Meta

```python
# scripts/seed_meta.py
from meta_database import META_DECKS, MATCHUP_DATA
from database import SessionLocal
from models import MetaDeck, MetaDeckCard, MetaMatchup

def import_meta_decks():
    """Importar decks meta de meta_database.py"""
    db = SessionLocal()

    for deck_id, deck_data in META_DECKS.items():
        # Criar deck meta
        meta_deck = MetaDeck(
            id=deck_id,
            name_en=deck_data.name_en,
            name_pt=deck_data.name_pt,
            tier=deck_data.tier,
            # ... outros campos
        )
        db.add(meta_deck)

        # Adicionar cartas
        for card_entry in deck_data.cards:
            # Buscar card_id do banco de dados
            card = db.query(Card).filter_by(name_en=card_entry.name_en).first()
            if card:
                meta_deck_card = MetaDeckCard(
                    meta_deck_id=deck_id,
                    card_id=card.id,
                    quantity=card_entry.quantity
                )
                db.add(meta_deck_card)

    db.commit()
```

### Conjuntos de Dados de Amostra

```bash
# Criar usuário de amostra para testes
python scripts/create_sample_user.py --username "testuser" --email "test@example.com"

# Criar decks de amostra para usuário
python scripts/create_sample_decks.py --user-id 1 --count 3

# Criar histórico de batalhas de amostra
python scripts/create_sample_battles.py --user-id 1 --count 50
```

---

## Exemplos de Consultas

### Encontrar todas as cartas rotacionando em Março 2026

```sql
SELECT c.name_en, cs.name_en as set_name, c.regulation_mark
FROM cards c
JOIN card_sets cs ON c.set_id = cs.id
WHERE c.regulation_mark = 'G'
ORDER BY cs.release_date, c.set_number;
```

### Obter deck do usuário com detalhes completos das cartas

```sql
SELECT
    c.name_en,
    c.card_type,
    dc.quantity,
    cs.code as set_code,
    c.regulation_mark
FROM deck_cards dc
JOIN cards c ON dc.card_id = c.id
JOIN card_sets cs ON c.set_id = cs.id
WHERE dc.deck_id = 1
ORDER BY c.card_type, c.name_en;
```

### Calcular impacto de rotação do deck

```sql
SELECT
    d.name as deck_name,
    COUNT(*) FILTER (WHERE c.regulation_mark = 'G') as rotating_cards,
    SUM(dc.quantity) FILTER (WHERE c.regulation_mark = 'G') as rotating_copies,
    d.total_cards,
    ROUND(100.0 * SUM(dc.quantity) FILTER (WHERE c.regulation_mark = 'G') / d.total_cards, 2) as rotation_percentage
FROM decks d
JOIN deck_cards dc ON d.id = dc.deck_id
JOIN cards c ON dc.card_id = c.id
WHERE d.user_id = 1
GROUP BY d.id, d.name, d.total_cards;
```

### Encontrar cartas mais populares no meta

```sql
SELECT
    c.name_en,
    COUNT(DISTINCT mdc.meta_deck_id) as deck_count,
    AVG(mdc.quantity) as avg_copies
FROM cards c
JOIN meta_deck_cards mdc ON c.id = mdc.card_id
GROUP BY c.id, c.name_en
HAVING COUNT(DISTINCT mdc.meta_deck_id) >= 5
ORDER BY deck_count DESC, avg_copies DESC
LIMIT 20;
```

### Obter taxa de vitória do usuário por arquétipo

```sql
SELECT
    md.name_en as opponent_archetype,
    COUNT(*) FILTER (WHERE b.result = 'win') as wins,
    COUNT(*) FILTER (WHERE b.result = 'loss') as losses,
    COUNT(*) as total_games,
    ROUND(100.0 * COUNT(*) FILTER (WHERE b.result = 'win') / COUNT(*), 2) as win_rate
FROM battles b
LEFT JOIN meta_decks md ON b.opponent_meta_deck_id = md.id
WHERE b.user_id = 1
GROUP BY md.id, md.name_en
HAVING COUNT(*) >= 3
ORDER BY win_rate DESC;
```

### Encontrar dados de matchup entre dois decks

```sql
SELECT
    deck_a.name_en as deck_a,
    deck_b.name_en as deck_b,
    mm.win_rate_a,
    100 - mm.win_rate_a as win_rate_b,
    mm.notes_en
FROM meta_matchups mm
JOIN meta_decks deck_a ON mm.deck_a_id = deck_a.id
JOIN meta_decks deck_b ON mm.deck_b_id = deck_b.id
WHERE mm.deck_a_id = 'charizard-pidgeot'
  AND mm.deck_b_id = 'lugia-archeops';
```

### Obter cartas por função (todas as cartas de compra)

```sql
SELECT DISTINCT c.name_en, c.card_type, c.trainer_subtype
FROM cards c
JOIN card_functions cf ON c.id = cf.card_id
WHERE cf.function = 'DRAW'
  AND c.regulation_mark IN ('H', 'I')
ORDER BY c.card_type, c.name_en;
```

### Encontrar torneios futuros

```sql
SELECT name, date, location, country, event_type, url
FROM tournaments
WHERE date >= CURRENT_DATE
ORDER BY date
LIMIT 10;
```

### Obter artigos de notícias recentes

```sql
SELECT title, summary, url, source, published_at
FROM news_articles
ORDER BY published_at DESC
LIMIT 20;
```

### Encontrar cartas faltantes da coleção do usuário para um deck

```sql
SELECT
    c.name_en,
    dc.quantity as needed,
    COALESCE(uc.quantity_owned, 0) as owned,
    dc.quantity - COALESCE(uc.quantity_owned, 0) as missing
FROM deck_cards dc
JOIN cards c ON dc.card_id = c.id
LEFT JOIN user_collection uc ON c.id = uc.card_id AND uc.user_id = 1
WHERE dc.deck_id = 1
  AND dc.quantity > COALESCE(uc.quantity_owned, 0)
ORDER BY missing DESC;
```

---

## Manutenção do Banco de Dados

### Vacuum e Analyze

```sql
-- Recuperar espaço e atualizar estatísticas
VACUUM ANALYZE;

-- Vacuum de tabela específica
VACUUM ANALYZE cards;
```

### Backup e Restore

```bash
# Backup do banco de dados
pg_dump -U postgres tcg_tool > backup_2026-02-15.sql

# Restore do banco de dados
psql -U postgres tcg_tool < backup_2026-02-15.sql

# Backup de tabelas específicas
pg_dump -U postgres -t users -t decks -t deck_cards tcg_tool > user_data_backup.sql
```

### Monitorar Tamanho do Banco de Dados

```sql
-- Tamanho do banco de dados
SELECT pg_size_pretty(pg_database_size('tcg_tool'));

-- Tamanhos de tabelas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Aprimoramentos Futuros

### Mudanças de Esquema Planejadas

1. **Full-Text Search** - Adicionar colunas tsvector para busca de cartas
2. **Audit Logging** - Rastrear todas as mudanças em decks de usuários
3. **Deck Versions** - Histórico de versões para edições de deck
4. **Shared Decks** - Compartilhamento público de decks e votação
5. **AI Analysis** - Armazenar insights gerados por IA da análise de vídeo
6. **Tournament Results** - Classificações detalhadas de torneios e decklists
7. **Trading** - Trading de cartas entre usuários
8. **Wishlists** - Listas de desejos de aquisição de cartas

### Otimizações de Performance

- Materialized views para consultas meta complexas
- Particionamento da tabela battle_actions (por data)
- Read replicas para consultas de analytics
- Connection pooling (PgBouncer)

---

**Fim da Referência do Esquema do Banco de Dados**
