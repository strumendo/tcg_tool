# API Reference - TCG Tool v3.0

**Author:** Bruno Strumendo
**Version:** 3.0.0
**Base URL:** `http://localhost:8000/api/v1`

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Cards](#cards-cards)
  - [Decks](#decks-decks)
  - [Meta](#meta-meta)
  - [Analysis](#analysis-analysis)
  - [Battles](#battles-battles)
  - [Chat](#chat-chat)
  - [Stats](#stats-stats)
  - [Collection](#collection-collection)
  - [Suggestions](#suggestions-suggestions)
  - [Simulation](#simulation-simulation)
  - [Tournaments](#tournaments-tournaments)
  - [Health](#health-health)

---

## Overview

The TCG Tool API provides comprehensive endpoints for Pokemon TCG deck management, analysis, and competitive insights. All endpoints return JSON unless otherwise specified.

**API Versioning:** All endpoints are prefixed with `/api/v1`

---

## Authentication

**Current Status:** Authentication is currently handled via hardcoded `user_id=1`.

**Planned:** JWT-based authentication will be implemented in a future release. When implemented, all protected endpoints will require an `Authorization: Bearer <token>` header.

---

## Response Formats

### Success Response (200 OK)

```json
{
  "id": 1,
  "name": "Charizard ex",
  "card_type": "POKEMON"
}
```

### List Response (200 OK)

```json
[
  {
    "id": 1,
    "name": "Charizard ex"
  },
  {
    "id": 2,
    "name": "Pidgeot ex"
  }
]
```

### Created Response (201 Created)

```json
{
  "id": 5,
  "name": "My New Deck",
  "created_at": "2026-02-15T10:30:00Z"
}
```

### No Content Response (204 No Content)

No response body. Used for successful deletions.

---

## Error Handling

### 400 Bad Request

Invalid request data or malformed JSON.

```json
{
  "detail": "Invalid deck format"
}
```

### 404 Not Found

Resource does not exist.

```json
{
  "detail": "Deck not found"
}
```

### 422 Unprocessable Entity

Validation error with detailed field information.

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

Server error.

```json
{
  "detail": "Internal server error"
}
```

---

## Endpoints

### Cards (`/cards`)

#### `GET /cards/`

Search and list cards with optional filters.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Filter by card name (partial match) |
| `card_type` | string | Filter by type: `POKEMON`, `TRAINER`, `ENERGY` |
| `ability` | string | Filter by ability category |
| `energy` | string | Filter by energy type (e.g., `Fire`, `Water`) |
| `regulation_mark` | string | Filter by regulation mark (e.g., `G`, `H`, `I`) |
| `set_code` | string | Filter by set code (e.g., `sv1`, `sv7`) |
| `is_ex` | boolean | Filter for ex/V/VSTAR cards |
| `skip` | integer | Pagination offset (default: 0) |
| `limit` | integer | Results per page (default: 100, max: 500) |

**Response:** `Card[]`

```json
[
  {
    "id": 1,
    "name": "Charizard ex",
    "card_type": "POKEMON",
    "set_code": "sv3.5",
    "set_name": "151",
    "regulation_mark": "G",
    "hp": 330,
    "types": ["Fire"],
    "evolves_from": "Charmeleon",
    "rarity": "Double Rare",
    "is_ex": true,
    "retreat_cost": 2,
    "image_url": "https://...",
    "abilities": [
      {
        "name": "Infernal Reign",
        "text": "Once during your turn...",
        "category": "ability"
      }
    ],
    "attacks": [
      {
        "name": "Burning Darkness",
        "cost": ["Fire", "Fire", "Colorless"],
        "damage": "180+",
        "text": "This attack does 30 more damage..."
      }
    ],
    "functions": ["DAMAGE", "ACCELERATION"]
  }
]
```

---

#### `GET /cards/abilities`

List all distinct ability categories.

**Response:** `string[]`

```json
[
  "ability",
  "draw",
  "search",
  "damage",
  "protection",
  "disruption"
]
```

---

#### `GET /cards/{card_id}`

Get detailed card information by ID.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `card_id` | integer | Card ID |

**Response:** `Card`

```json
{
  "id": 1,
  "name": "Charizard ex",
  "card_type": "POKEMON",
  "set_code": "sv3.5",
  "set_name": "151",
  "regulation_mark": "G",
  "hp": 330,
  "types": ["Fire"],
  "evolves_from": "Charmeleon",
  "rarity": "Double Rare",
  "is_ex": true,
  "retreat_cost": 2,
  "image_url": "https://...",
  "abilities": [
    {
      "name": "Infernal Reign",
      "text": "Once during your turn...",
      "category": "ability"
    }
  ],
  "attacks": [
    {
      "name": "Burning Darkness",
      "cost": ["Fire", "Fire", "Colorless"],
      "damage": "180+",
      "text": "This attack does 30 more damage..."
    }
  ],
  "functions": ["DAMAGE", "ACCELERATION"]
}
```

---

#### `GET /cards/{card_id}/alternatives`

Get alternative cards (reprints, different versions).

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `card_id` | integer | Card ID |

**Response:** `Card[]`

```json
[
  {
    "id": 45,
    "name": "Charizard ex",
    "set_code": "sv7",
    "set_name": "Stellar Crown",
    "regulation_mark": "H",
    "image_url": "https://..."
  }
]
```

---

#### `GET /cards/{card_id}/usage`

Get usage statistics for a card across meta decks.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `card_id` | integer | Card ID |

**Response:** `CardUsageStat[]`

```json
[
  {
    "card_id": 1,
    "card_name": "Charizard ex",
    "deck_count": 12,
    "total_copies": 48,
    "avg_copies": 4.0,
    "format": "Standard"
  }
]
```

---

### Decks (`/decks`)

#### `GET /decks/`

List all user decks.

**Response:** `Deck[]`

```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Charizard ex / Pidgeot ex",
    "archetype": "Charizard",
    "notes": "Main tournament deck",
    "created_at": "2026-02-01T10:00:00Z",
    "updated_at": "2026-02-15T14:30:00Z"
  }
]
```

---

#### `POST /decks/`

Create a new empty deck.

**Request Body:**

```json
{
  "name": "My New Deck",
  "archetype": "Charizard",
  "notes": "Testing rotation-proof build"
}
```

**Response:** `Deck` (201 Created)

```json
{
  "id": 5,
  "user_id": 1,
  "name": "My New Deck",
  "archetype": "Charizard",
  "notes": "Testing rotation-proof build",
  "created_at": "2026-02-15T15:00:00Z",
  "updated_at": "2026-02-15T15:00:00Z"
}
```

---

#### `POST /decks/import`

Import a deck from PTCGO/TCG Live text format.

**Request Body:**

```json
{
  "deck_text": "Pokémon: 12\n3 Charmander MEW 4\n2 Charmeleon OBF 26\n...",
  "name": "Imported Charizard Deck",
  "archetype": "Charizard"
}
```

**Response:** `Deck` (201 Created)

```json
{
  "id": 6,
  "user_id": 1,
  "name": "Imported Charizard Deck",
  "archetype": "Charizard",
  "notes": null,
  "created_at": "2026-02-15T15:05:00Z",
  "updated_at": "2026-02-15T15:05:00Z",
  "cards": [
    {
      "card_id": 4,
      "quantity": 3,
      "card": {
        "name": "Charmander",
        "set_code": "sv3.5"
      }
    }
  ]
}
```

---

#### `GET /decks/{deck_id}`

Get deck details with all cards.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID |

**Response:** `Deck`

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Charizard ex / Pidgeot ex",
  "archetype": "Charizard",
  "notes": "Main tournament deck",
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-15T14:30:00Z",
  "cards": [
    {
      "card_id": 1,
      "quantity": 2,
      "card": {
        "id": 1,
        "name": "Charizard ex",
        "card_type": "POKEMON",
        "set_code": "sv3.5"
      }
    },
    {
      "card_id": 15,
      "quantity": 4,
      "card": {
        "id": 15,
        "name": "Rare Candy",
        "card_type": "TRAINER",
        "set_code": "sv1"
      }
    }
  ]
}
```

---

#### `PUT /decks/{deck_id}`

Update deck information and card list.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID |

**Request Body:**

```json
{
  "name": "Updated Deck Name",
  "archetype": "Charizard",
  "notes": "New notes",
  "cards": [
    {
      "card_id": 1,
      "quantity": 3
    },
    {
      "card_id": 15,
      "quantity": 4
    }
  ]
}
```

**Response:** `Deck`

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Updated Deck Name",
  "archetype": "Charizard",
  "notes": "New notes",
  "updated_at": "2026-02-15T16:00:00Z"
}
```

---

#### `DELETE /decks/{deck_id}`

Delete a deck.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID |

**Response:** 204 No Content

---

#### `GET /decks/{deck_id}/export`

Export deck to PTCGO/TCG Live text format.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID |

**Response:**

```json
{
  "text": "Pokémon: 12\n3 Charmander MEW 4\n2 Charmeleon OBF 26\n2 Charizard ex MEW 6\n...\n\nTotal Cards: 60"
}
```

---

#### `GET /decks/{deck_id}/missing`

Get cards missing from user's collection for this deck.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID |

**Response:** `MissingCard[]`

```json
[
  {
    "card_id": 1,
    "card_name": "Charizard ex",
    "quantity_needed": 2,
    "quantity_owned": 0,
    "quantity_missing": 2,
    "set_code": "sv3.5",
    "rarity": "Double Rare"
  }
]
```

---

### Meta (`/meta`)

#### `GET /meta/decks`

List all meta decks.

**Response:** `MetaDeck[]`

```json
[
  {
    "id": 1,
    "name": "Charizard ex / Pidgeot ex",
    "archetype": "Charizard",
    "tier": 1,
    "win_rate": 0.58,
    "popularity": 0.15,
    "description": "Dominant control deck with draw power",
    "strengths": ["Consistency", "Late game power"],
    "weaknesses": ["Slow setup", "Water weakness"],
    "key_cards": [1, 2, 15]
  }
]
```

---

#### `GET /meta/decks/{deck_id}`

Get meta deck details with full card list.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Meta deck ID |

**Response:** `MetaDeck`

```json
{
  "id": 1,
  "name": "Charizard ex / Pidgeot ex",
  "archetype": "Charizard",
  "tier": 1,
  "win_rate": 0.58,
  "popularity": 0.15,
  "description": "Dominant control deck with draw power",
  "strengths": ["Consistency", "Late game power"],
  "weaknesses": ["Slow setup", "Water weakness"],
  "key_cards": [1, 2, 15],
  "cards": [
    {
      "card_id": 1,
      "quantity": 2,
      "card": {
        "name": "Charizard ex",
        "set_code": "sv3.5"
      }
    }
  ]
}
```

---

#### `GET /meta/matchups`

List all meta matchup data.

**Response:** `MetaMatchup[]`

```json
[
  {
    "id": 1,
    "deck_a_id": 1,
    "deck_b_id": 2,
    "deck_a_name": "Charizard ex",
    "deck_b_name": "Lugia VSTAR",
    "deck_a_win_rate": 0.52,
    "sample_size": 150,
    "notes": "Even matchup, depends on setup speed"
  }
]
```

---

#### `GET /meta/tiers`

Get meta decks grouped by tier.

**Response:**

```json
[
  {
    "tier": 1,
    "decks": [
      {
        "id": 1,
        "name": "Charizard ex / Pidgeot ex",
        "archetype": "Charizard",
        "win_rate": 0.58
      }
    ]
  },
  {
    "tier": 2,
    "decks": [
      {
        "id": 3,
        "name": "Lost Zone Box",
        "archetype": "Lost Zone",
        "win_rate": 0.51
      }
    ]
  }
]
```

---

### Analysis (`/analysis`)

#### `POST /analysis/rotation`

Analyze deck rotation impact.

**Request Body:**

```json
{
  "deck_id": 1
}
```

**Response:** `RotationReport`

```json
{
  "deck_id": 1,
  "deck_name": "Charizard ex / Pidgeot ex",
  "rotation_date": "2026-03-01",
  "total_cards": 60,
  "rotating_cards": 18,
  "rotation_percentage": 30.0,
  "severity": "MODERATE",
  "affected_cards": [
    {
      "card_id": 15,
      "card_name": "Rare Candy",
      "quantity": 4,
      "regulation_mark": "G",
      "set_code": "sv1",
      "function": "EVOLUTION_SUPPORT"
    }
  ],
  "substitution_suggestions": [
    {
      "original_card_id": 15,
      "original_card_name": "Rare Candy",
      "substitute_card_id": 89,
      "substitute_card_name": "Rare Candy",
      "substitute_set_code": "sv7",
      "reason": "Reprint in newer set"
    }
  ]
}
```

---

#### `POST /analysis/compare`

Compare two decks (composition, strategy, card overlap).

**Request Body:**

```json
{
  "deck_a_id": 1,
  "deck_b_id": 2
}
```

**Response:** `ComparisonResult`

```json
{
  "deck_a": {
    "id": 1,
    "name": "Charizard ex / Pidgeot ex"
  },
  "deck_b": {
    "id": 2,
    "name": "Lugia VSTAR"
  },
  "shared_cards": [
    {
      "card_id": 20,
      "card_name": "Professor's Research",
      "quantity_a": 4,
      "quantity_b": 3
    }
  ],
  "unique_to_a": [
    {
      "card_id": 1,
      "card_name": "Charizard ex",
      "quantity": 2
    }
  ],
  "unique_to_b": [
    {
      "card_id": 5,
      "card_name": "Lugia VSTAR",
      "quantity": 2
    }
  ],
  "similarity_score": 0.35,
  "strategy_comparison": {
    "deck_a_speed": "MODERATE",
    "deck_b_speed": "FAST",
    "deck_a_consistency": "HIGH",
    "deck_b_consistency": "MODERATE"
  }
}
```

---

#### `POST /analysis/matchup`

Analyze matchup between two decks.

**Request Body:**

```json
{
  "deck_a_id": 1,
  "deck_b_id": 2
}
```

**Response:** `MatchupResult`

```json
{
  "deck_a": {
    "id": 1,
    "name": "Charizard ex / Pidgeot ex"
  },
  "deck_b": {
    "id": 2,
    "name": "Lugia VSTAR"
  },
  "win_rate": 0.52,
  "matchup_type": "EVEN",
  "sample_size": 150,
  "key_interactions": [
    "Charizard ex can OHKO Lugia VSTAR with Burning Darkness",
    "Lugia's VSTAR Power provides explosive turns"
  ],
  "recommended_techs": [
    {
      "card_id": 45,
      "card_name": "Boss's Orders",
      "reason": "KO benched Arceus V before VSTAR evolution"
    }
  ]
}
```

---

#### `POST /analysis/substitutions`

Find card substitutions for rotating cards.

**Request Body:**

```json
{
  "deck_id": 1
}
```

**Response:** `SubstitutionResult`

```json
{
  "deck_id": 1,
  "substitutions": [
    {
      "original_card_id": 15,
      "original_card_name": "Rare Candy",
      "original_set_code": "sv1",
      "substitute_card_id": 89,
      "substitute_card_name": "Rare Candy",
      "substitute_set_code": "sv7",
      "substitute_regulation_mark": "H",
      "reason": "Identical reprint in rotation-legal set",
      "confidence": "HIGH"
    }
  ]
}
```

---

### Battles (`/battles`)

#### `GET /battles/`

List user's battle history.

**Response:** `Battle[]`

```json
[
  {
    "id": 1,
    "user_id": 1,
    "deck_id": 1,
    "opponent_deck_name": "Lugia VSTAR",
    "result": "WIN",
    "total_turns": 12,
    "went_first": true,
    "notes": "Strong opening, Pidgeot on turn 2",
    "played_at": "2026-02-14T19:30:00Z",
    "created_at": "2026-02-14T20:00:00Z"
  }
]
```

---

#### `POST /battles/`

Create a new battle record.

**Request Body:**

```json
{
  "deck_id": 1,
  "opponent_deck_name": "Lugia VSTAR",
  "result": "WIN",
  "total_turns": 12,
  "went_first": true,
  "notes": "Strong opening, Pidgeot on turn 2",
  "played_at": "2026-02-14T19:30:00Z"
}
```

**Response:** `Battle` (201 Created)

```json
{
  "id": 5,
  "user_id": 1,
  "deck_id": 1,
  "opponent_deck_name": "Lugia VSTAR",
  "result": "WIN",
  "total_turns": 12,
  "went_first": true,
  "notes": "Strong opening, Pidgeot on turn 2",
  "played_at": "2026-02-14T19:30:00Z",
  "created_at": "2026-02-14T20:00:00Z"
}
```

---

#### `GET /battles/{battle_id}`

Get battle details with actions.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `battle_id` | integer | Battle ID |

**Response:** `Battle`

```json
{
  "id": 1,
  "user_id": 1,
  "deck_id": 1,
  "opponent_deck_name": "Lugia VSTAR",
  "result": "WIN",
  "total_turns": 12,
  "went_first": true,
  "notes": "Strong opening, Pidgeot on turn 2",
  "played_at": "2026-02-14T19:30:00Z",
  "created_at": "2026-02-14T20:00:00Z",
  "actions": [
    {
      "id": 1,
      "turn_number": 1,
      "action_type": "DRAW",
      "card_id": 20,
      "description": "Drew Professor's Research",
      "timestamp": "2026-02-14T19:31:00Z"
    }
  ]
}
```

---

#### `PUT /battles/{battle_id}`

Update battle record.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `battle_id` | integer | Battle ID |

**Request Body:**

```json
{
  "result": "LOSS",
  "notes": "Updated notes after review"
}
```

**Response:** `Battle`

```json
{
  "id": 1,
  "result": "LOSS",
  "notes": "Updated notes after review",
  "updated_at": "2026-02-15T10:00:00Z"
}
```

---

#### `DELETE /battles/{battle_id}`

Delete a battle record.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `battle_id` | integer | Battle ID |

**Response:** 204 No Content

---

#### `POST /battles/{battle_id}/analyze`

Get AI analysis of battle performance.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `battle_id` | integer | Battle ID |

**Response:**

```json
{
  "analysis": "Your opening hand was strong with both Professor's Research and Ultra Ball. The Turn 2 Pidgeot ex evolution was optimal and gave you card advantage. Consider adding more switching cards to improve mobility in future games."
}
```

---

### Chat (`/chat`)

#### `POST /chat/message`

Send a message to the AI assistant and receive a complete response.

**Request Body:**

```json
{
  "message": "What's the best counter to Charizard ex?",
  "history": [
    {
      "role": "user",
      "content": "Tell me about rotation"
    },
    {
      "role": "assistant",
      "content": "Rotation happens in March 2026..."
    }
  ],
  "deck_id": 1
}
```

**Response:**

```json
{
  "response": "The best counters to Charizard ex are Water-type decks like Greninja ex and Blastoise ex. These decks exploit Charizard's 2x Water weakness, allowing them to OHKO with lower damage requirements. Additionally, decks with strong early-game pressure can prevent Charizard from setting up its evolution line."
}
```

---

#### `POST /chat/stream`

Send a message and receive a streaming response via Server-Sent Events (SSE).

**Request Body:**

```json
{
  "message": "What's the best counter to Charizard ex?",
  "history": [],
  "deck_id": 1
}
```

**Response Headers:**

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Response Format (SSE Stream):**

```
data: The

data:  best

data:  counters

data:  to

data:  Charizard

data:  ex

data:  are

data:  Water

data: -type

data:  decks

data: ...

data: [DONE]
```

**Client Example (JavaScript):**

```javascript
const eventSource = new EventSource('/api/v1/chat/stream', {
  method: 'POST',
  body: JSON.stringify({
    message: "What's the best counter to Charizard ex?",
    deck_id: 1
  })
});

eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
  } else {
    console.log('Chunk:', event.data);
  }
};
```

---

### Stats (`/stats`)

#### `GET /stats/cards`

Get card usage statistics across competitive play.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Format filter (e.g., `Standard`, `Expanded`) |
| `limit` | integer | Max results (default: 50) |

**Response:** `CardUsageStat[]`

```json
[
  {
    "card_id": 20,
    "card_name": "Professor's Research",
    "deck_count": 45,
    "total_copies": 165,
    "avg_copies": 3.67,
    "format": "Standard",
    "usage_percentage": 0.85
  }
]
```

---

#### `GET /stats/decks`

Get deck archetype usage statistics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Format filter |
| `limit` | integer | Max results (default: 20) |

**Response:** `DeckUsageStat[]`

```json
[
  {
    "archetype": "Charizard",
    "deck_count": 12,
    "win_rate": 0.58,
    "popularity": 0.15,
    "format": "Standard"
  }
]
```

---

#### `GET /stats/user`

Get current user's statistics.

**Response:** `UserStats`

```json
{
  "user_id": 1,
  "total_decks": 8,
  "total_battles": 45,
  "total_wins": 28,
  "total_losses": 17,
  "win_rate": 0.622,
  "favorite_archetype": "Charizard",
  "most_played_deck_id": 1,
  "collection_size": 234
}
```

---

#### `GET /stats/battles`

Get battle statistics for current user.

**Response:** `BattleStats`

```json
{
  "total_battles": 45,
  "wins": 28,
  "losses": 17,
  "win_rate": 0.622,
  "avg_turns": 10.5,
  "first_turn_win_rate": 0.65,
  "by_opponent": [
    {
      "opponent_deck_name": "Lugia VSTAR",
      "battles": 8,
      "wins": 5,
      "losses": 3,
      "win_rate": 0.625
    }
  ],
  "by_deck": [
    {
      "deck_id": 1,
      "deck_name": "Charizard ex / Pidgeot ex",
      "battles": 20,
      "wins": 14,
      "losses": 6,
      "win_rate": 0.70
    }
  ]
}
```

---

### Collection (`/collection`)

#### `GET /collection/`

List user's card collection.

**Response:** `CollectionEntry[]`

```json
[
  {
    "card_id": 1,
    "user_id": 1,
    "quantity_owned": 2,
    "card": {
      "id": 1,
      "name": "Charizard ex",
      "set_code": "sv3.5",
      "rarity": "Double Rare"
    }
  }
]
```

---

#### `PUT /collection/{card_id}`

Update quantity owned for a card.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `card_id` | integer | Card ID |

**Request Body:**

```json
{
  "quantity_owned": 3
}
```

**Response:** `CollectionEntry`

```json
{
  "card_id": 1,
  "user_id": 1,
  "quantity_owned": 3,
  "updated_at": "2026-02-15T11:00:00Z"
}
```

---

#### `GET /collection/missing/{deck_id}`

Get cards missing from collection for a specific deck.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID |

**Response:** `MissingCard[]`

```json
[
  {
    "card_id": 2,
    "card_name": "Pidgeot ex",
    "quantity_needed": 2,
    "quantity_owned": 1,
    "quantity_missing": 1,
    "set_code": "sv3.5",
    "rarity": "Double Rare"
  }
]
```

---

### Suggestions (`/suggestions`)

#### `POST /suggestions/swaps`

Get AI-powered card swap suggestions for deck improvement.

**Request Body:**

```json
{
  "deck_id": 1,
  "goals": ["rotation-proof", "faster setup"]
}
```

**Response:**

```json
{
  "suggestions": [
    {
      "remove_card_id": 15,
      "remove_card_name": "Rare Candy",
      "remove_quantity": 2,
      "add_card_id": 89,
      "add_card_name": "Rare Candy",
      "add_quantity": 2,
      "add_set_code": "sv7",
      "reason": "Replace rotating Rare Candy with rotation-legal reprint",
      "impact": "Maintains deck strategy while ensuring rotation compliance",
      "priority": "HIGH"
    },
    {
      "remove_card_id": 30,
      "remove_card_name": "Arven",
      "remove_quantity": 1,
      "add_card_id": 45,
      "add_card_name": "Boss's Orders",
      "add_quantity": 1,
      "add_set_code": "sv6",
      "reason": "Improve matchup against bench-sitting strategies",
      "impact": "Better late-game control",
      "priority": "MEDIUM"
    }
  ]
}
```

---

### Simulation (`/simulation`)

#### `POST /simulation/play-sequence`

Simulate opening turns and play sequences for deck testing.

**Request Body:**

```json
{
  "deck_id": 1,
  "turns": 5,
  "opponent_deck_id": 2
}
```

**Response:** `SimulationResult`

```json
{
  "deck_id": 1,
  "turns_simulated": 5,
  "opening_hand": [
    {
      "card_id": 20,
      "card_name": "Professor's Research"
    },
    {
      "card_id": 10,
      "card_name": "Ultra Ball"
    }
  ],
  "turn_sequence": [
    {
      "turn": 1,
      "actions": [
        "Drew Ultra Ball",
        "Played Ultra Ball, searched for Charmander",
        "Benched Charmander"
      ],
      "board_state": {
        "active": null,
        "bench": ["Charmander"],
        "hand_size": 6
      }
    }
  ],
  "mulligan_count": 0,
  "avg_turn_1_evolution": false,
  "avg_turn_2_evolution": true,
  "consistency_score": 0.75
}
```

---

### Tournaments (`/tournaments`)

#### `GET /tournaments/`

List recent tournament results.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Format filter |
| `limit` | integer | Max results (default: 20) |

**Response:** `Tournament[]`

```json
[
  {
    "id": 1,
    "name": "Regional Championship - São Paulo",
    "date": "2026-02-10",
    "format": "Standard",
    "location": "São Paulo, Brazil",
    "player_count": 256,
    "winning_deck": "Charizard ex / Pidgeot ex",
    "top_8_decks": [
      {
        "placement": 1,
        "archetype": "Charizard",
        "player_name": "John Silva"
      }
    ]
  }
]
```

---

#### `GET /tournaments/news`

Get recent Pokemon TCG news articles.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max results (default: 10) |

**Response:** `NewsArticle[]`

```json
[
  {
    "id": 1,
    "title": "New Set Announced: Journey Together",
    "summary": "The newest expansion features Eeveelutions and...",
    "url": "https://pokebeach.com/...",
    "published_at": "2026-02-14T10:00:00Z",
    "source": "PokeBeach"
  }
]
```

---

### Health (`/health`)

#### `GET /health`

Health check endpoint for monitoring.

**Response:**

```json
{
  "status": "ok",
  "version": "3.0.0",
  "timestamp": "2026-02-15T12:00:00Z"
}
```

---

## Data Models

### Common Enums

**CardType:**
- `POKEMON`
- `TRAINER`
- `ENERGY`

**BattleResult:**
- `WIN`
- `LOSS`
- `TIE`

**RotationSeverity:**
- `NONE` (0%)
- `LOW` (1-20%)
- `MODERATE` (21-40%)
- `HIGH` (41-60%)
- `CRITICAL` (61%+)

**MatchupType:**
- `FAVORED` (55%+ win rate)
- `EVEN` (45-54%)
- `UNFAVORED` (<45%)

---

## Rate Limiting

**Current Status:** No rate limiting implemented.

**Planned:** Rate limiting will be added in future releases with the following limits:
- 100 requests per minute per user
- 1000 requests per hour per user
- Chat endpoints: 20 requests per minute per user

---

## Pagination

List endpoints support pagination via `skip` and `limit` query parameters:

```
GET /api/v1/cards?skip=0&limit=50
```

**Default limit:** 100
**Max limit:** 500

---

## Versioning

The API uses URL-based versioning (`/api/v1`). Breaking changes will increment the version number.

---

## Support

For issues or questions, contact: strumendo@gmail.com

---

**Last Updated:** 2026-02-15
**API Version:** 3.0.0
