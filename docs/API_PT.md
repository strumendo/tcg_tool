# Referência da API - TCG Tool v3.0

**Autor:** Bruno Strumendo
**Versão:** 3.0.0
**URL Base:** `http://localhost:8000/api/v1`

## Índice

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Formatos de Resposta](#formatos-de-resposta)
- [Tratamento de Erros](#tratamento-de-erros)
- [Endpoints](#endpoints)
  - [Cartas](#cartas-cards)
  - [Decks](#decks-decks)
  - [Meta](#meta-meta)
  - [Análise](#análise-analysis)
  - [Batalhas](#batalhas-battles)
  - [Chat](#chat-chat)
  - [Estatísticas](#estatísticas-stats)
  - [Coleção](#coleção-collection)
  - [Sugestões](#sugestões-suggestions)
  - [Simulação](#simulação-simulation)
  - [Torneios](#torneios-tournaments)
  - [Saúde](#saúde-health)

---

## Visão Geral

A API TCG Tool fornece endpoints abrangentes para gerenciamento de decks Pokemon TCG, análise e insights competitivos. Todos os endpoints retornam JSON salvo indicação contrária.

**Versionamento da API:** Todos os endpoints são prefixados com `/api/v1`

---

## Autenticação

**Status Atual:** A autenticação é atualmente tratada via `user_id=1` fixo.

**Planejado:** Autenticação baseada em JWT será implementada em uma versão futura. Quando implementado, todos os endpoints protegidos exigirão um header `Authorization: Bearer <token>`.

---

## Formatos de Resposta

### Resposta de Sucesso (200 OK)

```json
{
  "id": 1,
  "name": "Charizard ex",
  "card_type": "POKEMON"
}
```

### Resposta de Lista (200 OK)

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

### Resposta de Criação (201 Created)

```json
{
  "id": 5,
  "name": "My New Deck",
  "created_at": "2026-02-15T10:30:00Z"
}
```

### Resposta Sem Conteúdo (204 No Content)

Sem corpo de resposta. Usado para deleções bem-sucedidas.

---

## Tratamento de Erros

### 400 Bad Request

Dados de requisição inválidos ou JSON malformado.

```json
{
  "detail": "Invalid deck format"
}
```

### 404 Not Found

Recurso não existe.

```json
{
  "detail": "Deck not found"
}
```

### 422 Unprocessable Entity

Erro de validação com informações detalhadas de campos.

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

Erro do servidor.

```json
{
  "detail": "Internal server error"
}
```

---

## Endpoints

### Cartas (`/cards`)

#### `GET /cards/`

Buscar e listar cartas com filtros opcionais.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `name` | string | Filtrar por nome da carta (correspondência parcial) |
| `card_type` | string | Filtrar por tipo: `POKEMON`, `TRAINER`, `ENERGY` |
| `ability` | string | Filtrar por categoria de habilidade |
| `energy` | string | Filtrar por tipo de energia (ex: `Fire`, `Water`) |
| `regulation_mark` | string | Filtrar por marca de regulação (ex: `G`, `H`, `I`) |
| `set_code` | string | Filtrar por código do set (ex: `sv1`, `sv7`) |
| `is_ex` | boolean | Filtrar cartas ex/V/VSTAR |
| `skip` | integer | Offset de paginação (padrão: 0) |
| `limit` | integer | Resultados por página (padrão: 100, máx: 500) |

**Resposta:** `Card[]`

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

Listar todas as categorias de habilidades distintas.

**Resposta:** `string[]`

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

Obter informações detalhadas da carta por ID.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `card_id` | integer | ID da Carta |

**Resposta:** `Card`

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

Obter cartas alternativas (reprints, versões diferentes).

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `card_id` | integer | ID da Carta |

**Resposta:** `Card[]`

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

Obter estatísticas de uso de uma carta em decks meta.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `card_id` | integer | ID da Carta |

**Resposta:** `CardUsageStat[]`

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

Listar todos os decks do usuário.

**Resposta:** `Deck[]`

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

Criar um novo deck vazio.

**Corpo da Requisição:**

```json
{
  "name": "My New Deck",
  "archetype": "Charizard",
  "notes": "Testing rotation-proof build"
}
```

**Resposta:** `Deck` (201 Created)

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

Importar um deck do formato de texto PTCGO/TCG Live.

**Corpo da Requisição:**

```json
{
  "deck_text": "Pokémon: 12\n3 Charmander MEW 4\n2 Charmeleon OBF 26\n...",
  "name": "Imported Charizard Deck",
  "archetype": "Charizard"
}
```

**Resposta:** `Deck` (201 Created)

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

Obter detalhes do deck com todas as cartas.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `deck_id` | integer | ID do Deck |

**Resposta:** `Deck`

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

Atualizar informações do deck e lista de cartas.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `deck_id` | integer | ID do Deck |

**Corpo da Requisição:**

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

**Resposta:** `Deck`

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

Deletar um deck.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `deck_id` | integer | ID do Deck |

**Resposta:** 204 No Content

---

#### `GET /decks/{deck_id}/export`

Exportar deck para formato de texto PTCGO/TCG Live.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `deck_id` | integer | ID do Deck |

**Resposta:**

```json
{
  "text": "Pokémon: 12\n3 Charmander MEW 4\n2 Charmeleon OBF 26\n2 Charizard ex MEW 6\n...\n\nTotal Cards: 60"
}
```

---

#### `GET /decks/{deck_id}/missing`

Obter cartas faltantes da coleção do usuário para este deck.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `deck_id` | integer | ID do Deck |

**Resposta:** `MissingCard[]`

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

Listar todos os decks meta.

**Resposta:** `MetaDeck[]`

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

Obter detalhes do deck meta com lista completa de cartas.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `deck_id` | integer | ID do Deck Meta |

**Resposta:** `MetaDeck`

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

Listar todos os dados de matchup meta.

**Resposta:** `MetaMatchup[]`

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

Obter decks meta agrupados por tier.

**Resposta:**

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

### Análise (`/analysis`)

#### `POST /analysis/rotation`

Analisar impacto de rotação do deck.

**Corpo da Requisição:**

```json
{
  "deck_id": 1
}
```

**Resposta:** `RotationReport`

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

Comparar dois decks (composição, estratégia, sobreposição de cartas).

**Corpo da Requisição:**

```json
{
  "deck_a_id": 1,
  "deck_b_id": 2
}
```

**Resposta:** `ComparisonResult`

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

Analisar matchup entre dois decks.

**Corpo da Requisição:**

```json
{
  "deck_a_id": 1,
  "deck_b_id": 2
}
```

**Resposta:** `MatchupResult`

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

Encontrar substituições de cartas para cartas rotacionando.

**Corpo da Requisição:**

```json
{
  "deck_id": 1
}
```

**Resposta:** `SubstitutionResult`

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

### Batalhas (`/battles`)

#### `GET /battles/`

Listar histórico de batalhas do usuário.

**Resposta:** `Battle[]`

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

Criar um novo registro de batalha.

**Corpo da Requisição:**

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

**Resposta:** `Battle` (201 Created)

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

Obter detalhes da batalha com ações.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `battle_id` | integer | ID da Batalha |

**Resposta:** `Battle`

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

Atualizar registro de batalha.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `battle_id` | integer | ID da Batalha |

**Corpo da Requisição:**

```json
{
  "result": "LOSS",
  "notes": "Updated notes after review"
}
```

**Resposta:** `Battle`

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

Deletar um registro de batalha.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `battle_id` | integer | ID da Batalha |

**Resposta:** 204 No Content

---

#### `POST /battles/{battle_id}/analyze`

Obter análise de IA do desempenho da batalha.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `battle_id` | integer | ID da Batalha |

**Resposta:**

```json
{
  "analysis": "Your opening hand was strong with both Professor's Research and Ultra Ball. The Turn 2 Pidgeot ex evolution was optimal and gave you card advantage. Consider adding more switching cards to improve mobility in future games."
}
```

---

### Chat (`/chat`)

#### `POST /chat/message`

Enviar uma mensagem para o assistente de IA e receber uma resposta completa.

**Corpo da Requisição:**

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

**Resposta:**

```json
{
  "response": "The best counters to Charizard ex are Water-type decks like Greninja ex and Blastoise ex. These decks exploit Charizard's 2x Water weakness, allowing them to OHKO with lower damage requirements. Additionally, decks with strong early-game pressure can prevent Charizard from setting up its evolution line."
}
```

---

#### `POST /chat/stream`

Enviar uma mensagem e receber uma resposta em streaming via Server-Sent Events (SSE).

**Corpo da Requisição:**

```json
{
  "message": "What's the best counter to Charizard ex?",
  "history": [],
  "deck_id": 1
}
```

**Headers de Resposta:**

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Formato de Resposta (Stream SSE):**

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

**Exemplo de Cliente (JavaScript):**

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

### Estatísticas (`/stats`)

#### `GET /stats/cards`

Obter estatísticas de uso de cartas no jogo competitivo.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `format` | string | Filtro de formato (ex: `Standard`, `Expanded`) |
| `limit` | integer | Máx resultados (padrão: 50) |

**Resposta:** `CardUsageStat[]`

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

Obter estatísticas de uso de arquétipos de deck.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `format` | string | Filtro de formato |
| `limit` | integer | Máx resultados (padrão: 20) |

**Resposta:** `DeckUsageStat[]`

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

Obter estatísticas do usuário atual.

**Resposta:** `UserStats`

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

Obter estatísticas de batalha para o usuário atual.

**Resposta:** `BattleStats`

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

### Coleção (`/collection`)

#### `GET /collection/`

Listar coleção de cartas do usuário.

**Resposta:** `CollectionEntry[]`

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

Atualizar quantidade possuída de uma carta.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `card_id` | integer | ID da Carta |

**Corpo da Requisição:**

```json
{
  "quantity_owned": 3
}
```

**Resposta:** `CollectionEntry`

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

Obter cartas faltantes da coleção para um deck específico.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `deck_id` | integer | ID do Deck |

**Resposta:** `MissingCard[]`

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

### Sugestões (`/suggestions`)

#### `POST /suggestions/swaps`

Obter sugestões de troca de cartas com IA para melhoria do deck.

**Corpo da Requisição:**

```json
{
  "deck_id": 1,
  "goals": ["rotation-proof", "faster setup"]
}
```

**Resposta:**

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

### Simulação (`/simulation`)

#### `POST /simulation/play-sequence`

Simular turnos iniciais e sequências de jogo para teste de deck.

**Corpo da Requisição:**

```json
{
  "deck_id": 1,
  "turns": 5,
  "opponent_deck_id": 2
}
```

**Resposta:** `SimulationResult`

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

### Torneios (`/tournaments`)

#### `GET /tournaments/`

Listar resultados recentes de torneios.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `format` | string | Filtro de formato |
| `limit` | integer | Máx resultados (padrão: 20) |

**Resposta:** `Tournament[]`

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

Obter artigos recentes de notícias Pokemon TCG.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `limit` | integer | Máx resultados (padrão: 10) |

**Resposta:** `NewsArticle[]`

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

### Saúde (`/health`)

#### `GET /health`

Endpoint de verificação de saúde para monitoramento.

**Resposta:**

```json
{
  "status": "ok",
  "version": "3.0.0",
  "timestamp": "2026-02-15T12:00:00Z"
}
```

---

## Modelos de Dados

### Enums Comuns

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

**Status Atual:** Nenhum rate limiting implementado.

**Planejado:** Rate limiting será adicionado em versões futuras com os seguintes limites:
- 100 requisições por minuto por usuário
- 1000 requisições por hora por usuário
- Endpoints de chat: 20 requisições por minuto por usuário

---

## Paginação

Endpoints de lista suportam paginação via parâmetros de consulta `skip` e `limit`:

```
GET /api/v1/cards?skip=0&limit=50
```

**Limite padrão:** 100
**Limite máximo:** 500

---

## Versionamento

A API usa versionamento baseado em URL (`/api/v1`). Mudanças que quebram compatibilidade incrementarão o número da versão.

---

## Suporte

Para problemas ou questões, contate: strumendo@gmail.com

---

**Última Atualização:** 2026-02-15
**Versão da API:** 3.0.0
