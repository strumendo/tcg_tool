# DATABASE.md - Database Schema Reference

**Author:** Bruno Strumendo
**Project:** TCG Tool v3.0
**Database:** PostgreSQL
**Last Updated:** 2026-02-15

---

## Table of Contents

1. [Overview](#overview)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [Table Schemas](#table-schemas)
4. [Indexes](#indexes)
5. [Regulation Mark System](#regulation-mark-system)
6. [Migrations Guide](#migrations-guide)
7. [Seeding Guide](#seeding-guide)
8. [Query Examples](#query-examples)

---

## Overview

The TCG Tool v3.0 database consists of **17 tables** organized into the following domains:

| Domain | Tables | Purpose |
|--------|--------|---------|
| **User Management** | `users` | User accounts and preferences |
| **Card Data** | `card_sets`, `cards`, `card_abilities`, `card_attacks`, `card_functions` | Complete card database with abilities, attacks, and functions |
| **User Decks** | `decks`, `deck_cards` | Personal deck collection and deck building |
| **Meta Analysis** | `meta_decks`, `meta_deck_cards`, `meta_matchups` | Competitive meta database and matchup data |
| **Battle Tracking** | `battles`, `battle_actions` | Match history and replay data |
| **Collection** | `user_collection` | Card ownership tracking |
| **Statistics** | `card_usage_stats`, `deck_usage_stats` | Usage analytics and meta trends |
| **External Data** | `tournaments`, `news_articles` | Tournament calendar and news feed |

**Technology Stack:**
- PostgreSQL 14+
- SQLAlchemy ORM
- Alembic migrations
- JSONB for flexible data structures

---

## Entity Relationship Diagram

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

## Table Schemas

### 1. users

User accounts and preferences for the TCG Tool application.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `username`: Unique username (3-50 characters)
- `email`: Optional email for notifications
- `language`: UI language preference (en/pt)
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Constraints:**
- `username` must be unique and not null
- `email` must be unique if provided
- `language` must be 'en' or 'pt'

---

### 2. card_sets

Pokemon TCG set information with regulation marks and legality.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `code`: Set code (e.g., "sv1", "sv3", "PAL", "OBF")
- `tcgdex_id`: TCGdex API identifier
- `name_en`: English set name (e.g., "Scarlet & Violet")
- `name_pt`: Portuguese set name
- `regulation_mark`: F/G/H/I legality marker
- `release_date`: Official release date
- `total_cards`: Number of cards in set
- `is_legal`: Current legality status in Standard format
- `created_at`: Record creation timestamp

**Common Set Codes:**
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

Complete card database with multilingual support and metadata.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `name_en`: English card name (e.g., "Charizard ex")
- `name_pt`: Portuguese card name (e.g., "Charizard ex")
- `card_type`: pokemon/trainer/energy
- `trainer_subtype`: item/supporter/stadium/tool (if trainer)
- `set_id`: Foreign key to card_sets
- `set_number`: Card number in set (e.g., "125")
- `regulation_mark`: F/G/H/I legality marker
- `hp`: Hit points (Pokemon only)
- `energy_type`: Fire/Water/Grass/etc. (Pokemon only)
- `stage`: Basic/Stage 1/Stage 2/ex/VMAX/VSTAR
- `is_ex`: True if card is a Pokemon ex/EX/GX/V/VMAX/VSTAR
- `image_url`: Standard resolution image URL
- `image_url_hires`: High resolution image URL
- `tcgdex_id`: TCGdex API identifier
- `pokemontcg_id`: Pokemon TCG API identifier
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- Each card must have a unique combination of `set_id` and `set_number`
- Basic Energy cards are always legal regardless of regulation mark

---

### 4. card_abilities

Pokemon abilities (passive effects) with multilingual descriptions.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `card_id`: Foreign key to cards table
- `name_en`: English ability name (e.g., "Knock Back")
- `name_pt`: Portuguese ability name
- `effect_en`: English ability text
- `effect_pt`: Portuguese ability text
- `category`: Functional category (DRAW/SEARCH/etc.)
- `created_at`: Record creation timestamp

**Categories:**
- `DRAW`: Card draw effects
- `SEARCH`: Deck/discard searching
- `RECOVERY`: Healing or restoration
- `SWITCHING`: Retreat or switch effects
- `ENERGY_ACCEL`: Energy attachment acceleration
- `DISRUPTION`: Opponent disruption
- `DAMAGE`: Damage-dealing abilities
- `HEALING`: HP recovery
- `PROTECTION`: Damage reduction or immunity
- `OTHER`: Miscellaneous effects

---

### 5. card_attacks

Pokemon attacks with damage, energy cost, and effects.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `card_id`: Foreign key to cards table
- `name_en`: English attack name (e.g., "Burning Darkness")
- `name_pt`: Portuguese attack name
- `damage`: Base damage (e.g., "180", "30+", "")
- `energy_cost`: JSONB array of energy types (e.g., `["Fire", "Fire", "Colorless"]`)
- `effect_en`: English attack effect text
- `effect_pt`: Portuguese attack effect text
- `created_at`: Record creation timestamp

**Energy Cost Examples:**
```json
["Fire", "Fire", "Colorless"]
["Water", "Colorless", "Colorless"]
["Darkness"]
[]
```

---

### 6. card_functions

Card functional tags for deck building and analysis.

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

**Fields:**
- `card_id`: Foreign key to cards table
- `function`: Functional category tag

**Usage:**
- A single card can have multiple functions
- Used for deck analysis (e.g., "How many draw cards in this deck?")
- Supports substitution suggestions (e.g., "Replace this DRAW card with another DRAW card")

**Function Types:**
- `DRAW`: Card drawing (Professor's Research, Iono)
- `SEARCH`: Deck/discard search (Ultra Ball, Nest Ball)
- `RECOVERY`: Card recovery (Super Rod, Counter Catcher)
- `SWITCHING`: Retreat/switch (Switch, Boss's Orders)
- `ENERGY_ACCEL`: Energy acceleration (Rare Candy, Energy Switch)
- `DISRUPTION`: Opponent disruption (Iono, Judge)
- `DAMAGE`: Direct damage (Radiant Greninja, Manaphy)
- `HEALING`: HP healing (Pokémon Center Lady)
- `PROTECTION`: Damage protection (Manaphy, Path to the Peak)
- `OTHER`: Miscellaneous utility

---

### 7. decks

User-created decks with metadata and validation status.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users table
- `name`: User-defined deck name
- `archetype`: Deck archetype (e.g., "charizard-pidgeot", "lugia-archeops")
- `notes`: User notes about the deck
- `is_active`: Whether this is the user's currently active deck
- `is_valid`: Whether deck passes validation (60 cards, 4-of rule, etc.)
- `total_cards`: Computed total card count
- `created_at`: Deck creation timestamp
- `updated_at`: Last modification timestamp

**Validation Rules:**
- Exactly 60 cards
- Maximum 4 copies of any card (except Basic Energy)
- At least 1 Basic Pokemon
- All cards must be legal in Standard format

---

### 8. deck_cards

Card quantities in user decks (junction table).

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

**Fields:**
- `id`: Auto-incrementing primary key
- `deck_id`: Foreign key to decks table
- `card_id`: Foreign key to cards table
- `quantity`: Number of copies (1-60)

**Constraints:**
- Each card can appear at most once per deck (unique combination)
- Quantity must be between 1 and 60
- Maximum 4 copies enforced at application level (except Basic Energy)

---

### 9. meta_decks

Competitive meta deck archetypes with tier rankings and matchup data.

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

**Fields:**
- `id`: Archetype identifier (e.g., "charizard-pidgeot", "lugia-archeops")
- `name_en`: English deck name
- `name_pt`: Portuguese deck name
- `tier`: Competitive tier (1=top tier, 2=competitive, 3=rogue)
- `description_en`: English deck description
- `description_pt`: Portuguese deck description
- `strategy_en`: English strategy guide
- `strategy_pt`: Portuguese strategy guide
- `difficulty`: Skill requirement (Easy/Medium/Hard)
- `meta_share`: Percentage of competitive meta (0-100)
- `key_pokemon`: JSONB array of key Pokemon (e.g., `["Charizard ex", "Pidgeot ex"]`)
- `energy_types`: JSONB array of energy types (e.g., `["Fire", "Colorless"]`)
- `strengths_en`: JSONB array of English strength descriptions
- `strengths_pt`: JSONB array of Portuguese strength descriptions
- `weaknesses_en`: JSONB array of English weakness descriptions
- `weaknesses_pt`: JSONB array of Portuguese weakness descriptions
- `snapshot_date`: Meta snapshot date
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**JSONB Examples:**
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

Card lists for meta deck archetypes (junction table).

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

**Fields:**
- `id`: Auto-incrementing primary key
- `meta_deck_id`: Foreign key to meta_decks table
- `card_id`: Foreign key to cards table
- `quantity`: Number of copies (1-60)

**Usage:**
- Stores the "standard" or "reference" decklist for each meta archetype
- Used for deck comparison and suggestion
- Should total exactly 60 cards per meta deck

---

### 11. meta_matchups

Head-to-head matchup data between meta decks.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `deck_a_id`: First deck (alphabetically lower ID)
- `deck_b_id`: Second deck (alphabetically higher ID)
- `win_rate_a`: Win rate of deck_a vs deck_b (0-100)
- `notes_en`: English matchup notes
- `notes_pt`: Portuguese matchup notes
- `snapshot_date`: Meta snapshot date

**Constraints:**
- `deck_a_id` must be alphabetically before `deck_b_id` (prevents duplicates)
- `win_rate_a` represents deck A's win percentage
- To get deck B's win rate: `100 - win_rate_a`

**Matchup Interpretation:**
- 55%+ = Favored
- 46-54% = Even
- 45% or below = Unfavored

**Example:**
```sql
-- Charizard vs Lugia: Charizard wins 58% of the time
INSERT INTO meta_matchups (deck_a_id, deck_b_id, win_rate_a)
VALUES ('charizard-pidgeot', 'lugia-archeops', 58.0);
```

---

### 12. battles

User match history with results and metadata.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users table
- `deck_id`: Foreign key to decks table (nullable if deck deleted)
- `opponent_deck_name`: Free-text opponent deck name
- `opponent_meta_deck_id`: Foreign key to meta_decks if recognized archetype
- `result`: win/loss/tie
- `total_turns`: Number of turns in the match
- `went_first`: Whether user went first
- `notes`: User notes about the match
- `source`: How match was recorded (manual/video/import)
- `source_url`: URL to match video (if applicable)
- `played_at`: When match was played
- `created_at`: When record was created

**Usage:**
- Track win/loss records against specific archetypes
- Analyze going first vs going second win rates
- Link to video replays for review
- Future: AI video analysis integration

---

### 13. battle_actions

Turn-by-turn action log for match replays.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `battle_id`: Foreign key to battles table
- `turn`: Turn number (1-based)
- `player`: user/opponent
- `action_type`: Type of action performed
- `card_name`: Name of card involved (if applicable)
- `details`: Additional action details (e.g., "Drew 3 cards")
- `sequence_order`: Order of actions within the turn/player

**Action Types:**
- `attach_energy`: Energy attachment
- `play_supporter`: Supporter card played
- `play_item`: Item card played
- `play_stadium`: Stadium card played
- `evolve`: Pokemon evolution
- `attack`: Attack declaration
- `switch`: Active Pokemon switch
- `retreat`: Pokemon retreat
- `ability`: Ability activation
- `knockout`: Pokemon knocked out
- `other`: Miscellaneous action

**Future Use:**
- AI video analysis will populate this table
- Replay system for reviewing matches
- Pattern analysis (e.g., "Turn 1 Supporter usage rates")

---

### 14. user_collection

Card ownership tracking for collection management.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users table
- `card_id`: Foreign key to cards table
- `quantity_owned`: Number of copies owned (0+)

**Usage:**
- Track which cards user owns
- Deck validation (can only build decks with owned cards)
- Highlight missing cards when viewing meta decks
- Import from TCG Live collection export

---

### 15. card_usage_stats

Card popularity and usage statistics from tournament data.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `card_id`: Foreign key to cards table
- `format`: Standard/Expanded/Unlimited
- `usage_percentage`: Percentage of decks running this card (0-100)
- `avg_copies`: Average number of copies per deck (0-60)
- `sample_size`: Number of decks analyzed
- `snapshot_date`: Date of data snapshot

**Usage:**
- Show trending cards ("50% of decks run Professor's Research")
- Compare card popularity over time
- Suggest popular tech choices
- Data sourced from Limitless TCG

**Example:**
```sql
-- Professor's Research is in 85% of decks, averaging 2.3 copies
INSERT INTO card_usage_stats (card_id, usage_percentage, avg_copies, sample_size)
VALUES (1234, 85.0, 2.3, 500);
```

---

### 16. deck_usage_stats

Deck archetype popularity and performance statistics.

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

**Fields:**
- `id`: Auto-incrementing primary key
- `archetype`: Deck archetype name (e.g., "Charizard ex / Pidgeot ex")
- `meta_share`: Percentage of tournament meta (0-100)
- `avg_placement`: Average tournament placement (lower is better)
- `sample_size`: Number of tournament results analyzed
- `format`: Standard/Expanded/Unlimited
- `snapshot_date`: Date of data snapshot

**Usage:**
- Track meta trends over time
- Show rising/falling archetypes
- Performance analysis (meta share vs average placement)
- Data sourced from Limitless TCG

**Example:**
```sql
-- Charizard ex has 18% meta share, averaging 12.5 placement
INSERT INTO deck_usage_stats (archetype, meta_share, avg_placement, sample_size)
VALUES ('Charizard ex / Pidgeot ex', 18.0, 12.5, 250);
```

---

### 17. tournaments

Official and competitive tournament calendar.

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

**Fields:**
- `id`: Tournament identifier (e.g., "regional-orlando-2026-03")
- `name`: Tournament name
- `date`: Start date
- `end_date`: End date (for multi-day events)
- `location`: City or venue
- `country`: Country code or name
- `format`: Standard/Expanded/Unlimited
- `event_type`: Regional/International/World Championship/etc.
- `url`: Tournament information URL
- `created_at`: Record creation timestamp

**Usage:**
- Display upcoming tournament calendar
- Sync with device calendar (Android app)
- Link to tournament results
- Data sourced from RK9 and Pokemon.com

---

### 18. news_articles

Pokemon TCG news feed from PokeBeach and other sources.

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

**Fields:**
- `id`: Article identifier (URL slug or hash)
- `title`: Article headline
- `summary`: Article excerpt or description
- `url`: Full article URL
- `image_url`: Featured image URL
- `source`: News source (PokeBeach/Pokemon.com/etc.)
- `published_at`: Original publication timestamp
- `created_at`: Record creation timestamp

**Usage:**
- Display news feed in app
- RSS/API integration with PokeBeach
- Push notifications for breaking news
- Filter by source or date range

---

## Indexes

### Primary Keys
All tables have primary keys with automatic indexes:
- `users(id)`, `card_sets(id)`, `cards(id)`, `decks(id)`, `battles(id)`, etc.

### Foreign Key Indexes
Automatically created on all foreign key columns:
- `cards(set_id)`, `deck_cards(deck_id)`, `deck_cards(card_id)`, etc.

### Unique Constraints
- `users(username)`, `users(email)`
- `card_sets(code)`
- `cards(set_id, set_number)`
- `deck_cards(deck_id, card_id)`
- `meta_deck_cards(meta_deck_id, card_id)`
- `meta_matchups(deck_a_id, deck_b_id)`
- `user_collection(user_id, card_id)`
- `card_usage_stats(card_id, format, snapshot_date)`
- `deck_usage_stats(archetype, format, snapshot_date)`

### Performance Indexes
- `cards(name_en)`, `cards(name_pt)` - Card name search
- `cards(card_type)`, `cards(regulation_mark)` - Filtering
- `decks(user_id)`, `decks(archetype)` - User deck queries
- `battles(played_at DESC)` - Recent matches
- `meta_decks(tier)`, `meta_decks(meta_share DESC)` - Meta rankings
- `tournaments(date DESC)` - Upcoming events
- `news_articles(published_at DESC)` - Recent news

### JSONB Indexes (GIN)
- `card_attacks(energy_cost)` - Energy cost queries
- Future: JSONB fields in `meta_decks` for advanced queries

---

## Regulation Mark System

Pokemon TCG uses regulation marks to determine card legality in Standard format.

### Current Regulation Marks (as of 2026-02-15)

| Mark | Status | Sets | Notes |
|------|--------|------|-------|
| **F** | Illegal | Sword & Shield era | Already rotated |
| **G** | **Rotating March 2026** | SVI, PAL, OBF, MEW, PAR, PAF | 6 sets rotating out |
| **H** | Legal | TEF, TWM, SFA, SCR, SSP | Current Standard |
| **I** | Legal | PRE, JTG, ASC, DRI, MEV | Latest sets |

### Rotation Impact Analysis

The application calculates rotation impact for user decks:

```sql
-- Count cards by regulation mark in a deck
SELECT
    c.regulation_mark,
    COUNT(*) as card_count,
    SUM(dc.quantity) as total_copies
FROM deck_cards dc
JOIN cards c ON dc.card_id = c.id
WHERE dc.deck_id = $1
GROUP BY c.regulation_mark;
```

**Severity Levels:**
- **NONE**: 0% of deck rotating
- **LOW**: 1-20% rotating
- **MODERATE**: 21-40% rotating
- **HIGH**: 41-60% rotating
- **CRITICAL**: 61%+ rotating

### Special Cases

**Basic Energy:**
- Always legal regardless of set or regulation mark
- Identified by card name pattern: "Basic {Type} Energy"
- Should not count towards rotation impact

**Promo Cards:**
- Use regulation mark of equivalent main set printing
- Example: Charizard ex promo (sv3.5) has mark G

---

## Migrations Guide

This project uses **Alembic** for database schema migrations.

### Setup

```bash
# Install Alembic
pip install alembic psycopg2-binary

# Initialize Alembic (first time only)
alembic init alembic

# Configure alembic.ini
# Set sqlalchemy.url = postgresql://user:pass@localhost/tcg_tool
```

### Common Commands

```bash
# Create a new migration
alembic revision -m "Add user_collection table"

# Auto-generate migration from models
alembic revision --autogenerate -m "Add card_functions table"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history

# Upgrade to specific revision
alembic upgrade abc123
```

### Migration Example

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

### Best Practices

1. **Always review auto-generated migrations** - Alembic may not detect all changes
2. **Test migrations on dev database first** - Never run untested migrations on production
3. **Include both upgrade and downgrade** - Always provide rollback path
4. **One logical change per migration** - Easier to debug and rollback
5. **Add data migrations separately** - Keep schema and data migrations separate

---

## Seeding Guide

### Initial Data Requirements

1. **Card Sets** - Populate all Scarlet & Violet sets
2. **Cards** - Import from TCGdex API (10,000+ cards)
3. **Meta Decks** - Import 8 top-tier archetypes
4. **Meta Deck Cards** - Complete 60-card decklists
5. **Meta Matchups** - Import 28 matchup relationships
6. **News Articles** - Import recent PokeBeach articles
7. **Tournaments** - Import upcoming events from RK9

### Seed Scripts

```bash
# Run all seed scripts
python scripts/seed_database.py --all

# Seed specific tables
python scripts/seed_database.py --sets
python scripts/seed_database.py --cards
python scripts/seed_database.py --meta
python scripts/seed_database.py --news
python scripts/seed_database.py --tournaments
```

### Card Import Strategy

```python
# scripts/seed_cards.py
import httpx
from database import SessionLocal
from models import CardSet, Card

async def import_cards_from_tcgdex():
    """Import all Scarlet & Violet cards from TCGdex API"""
    async with httpx.AsyncClient() as client:
        # Fetch all sets
        response = await client.get("https://api.tcgdex.net/v2/en/sets")
        sets_data = response.json()

        for set_data in sets_data:
            if not set_data['id'].startswith('sv'):
                continue  # Skip non-SV sets

            # Fetch all cards in set
            response = await client.get(f"https://api.tcgdex.net/v2/en/sets/{set_data['id']}")
            cards_data = response.json()

            # Insert cards...
```

### Meta Deck Import

```python
# scripts/seed_meta.py
from meta_database import META_DECKS, MATCHUP_DATA
from database import SessionLocal
from models import MetaDeck, MetaDeckCard, MetaMatchup

def import_meta_decks():
    """Import meta decks from meta_database.py"""
    db = SessionLocal()

    for deck_id, deck_data in META_DECKS.items():
        # Create meta deck
        meta_deck = MetaDeck(
            id=deck_id,
            name_en=deck_data.name_en,
            name_pt=deck_data.name_pt,
            tier=deck_data.tier,
            # ... other fields
        )
        db.add(meta_deck)

        # Add cards
        for card_entry in deck_data.cards:
            # Lookup card_id from database
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

### Sample Data Sets

```bash
# Create sample user for testing
python scripts/create_sample_user.py --username "testuser" --email "test@example.com"

# Create sample decks for user
python scripts/create_sample_decks.py --user-id 1 --count 3

# Create sample battle history
python scripts/create_sample_battles.py --user-id 1 --count 50
```

---

## Query Examples

### Find all cards rotating in March 2026

```sql
SELECT c.name_en, cs.name_en as set_name, c.regulation_mark
FROM cards c
JOIN card_sets cs ON c.set_id = cs.id
WHERE c.regulation_mark = 'G'
ORDER BY cs.release_date, c.set_number;
```

### Get user's deck with full card details

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

### Calculate deck rotation impact

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

### Find most popular cards in meta

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

### Get user's win rate by archetype

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

### Find matchup data between two decks

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

### Get cards by function (all draw cards)

```sql
SELECT DISTINCT c.name_en, c.card_type, c.trainer_subtype
FROM cards c
JOIN card_functions cf ON c.id = cf.card_id
WHERE cf.function = 'DRAW'
  AND c.regulation_mark IN ('H', 'I')
ORDER BY c.card_type, c.name_en;
```

### Find upcoming tournaments

```sql
SELECT name, date, location, country, event_type, url
FROM tournaments
WHERE date >= CURRENT_DATE
ORDER BY date
LIMIT 10;
```

### Get recent news articles

```sql
SELECT title, summary, url, source, published_at
FROM news_articles
ORDER BY published_at DESC
LIMIT 20;
```

### Find cards missing from user's collection for a deck

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

## Database Maintenance

### Vacuum and Analyze

```sql
-- Reclaim space and update statistics
VACUUM ANALYZE;

-- Vacuum specific table
VACUUM ANALYZE cards;
```

### Backup and Restore

```bash
# Backup database
pg_dump -U postgres tcg_tool > backup_2026-02-15.sql

# Restore database
psql -U postgres tcg_tool < backup_2026-02-15.sql

# Backup specific tables
pg_dump -U postgres -t users -t decks -t deck_cards tcg_tool > user_data_backup.sql
```

### Monitor Database Size

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('tcg_tool'));

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Future Enhancements

### Planned Schema Changes

1. **Full-Text Search** - Add tsvector columns for card search
2. **Audit Logging** - Track all changes to user decks
3. **Deck Versions** - Version history for deck edits
4. **Shared Decks** - Public deck sharing and voting
5. **AI Analysis** - Store AI-generated insights from video analysis
6. **Tournament Results** - Detailed tournament standings and decklists
7. **Trading** - Card trading between users
8. **Wishlists** - Card acquisition wishlists

### Performance Optimizations

- Materialized views for complex meta queries
- Partitioning for battle_actions table (by date)
- Read replicas for analytics queries
- Connection pooling (PgBouncer)

---

**End of Database Schema Reference**
