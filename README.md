# TCG Rotation Checker

Ferramenta CLI para analisar decks de Pokemon TCG, verificar o impacto da rotação de março de 2026, comparar matchups contra outros decks e consultar o meta competitivo com suporte bilíngue (Português/Inglês).

---

## Funcionalidades

### 1. Análise de Rotação
- Identifica cartas com **Regulation Mark G** que rotacionam em março 2026
- Detecta cartas já ilegais (Regulation Mark F ou anterior)
- Busca substituições na coleção Ascended Heroes (ASC)
- Calcula o impacto percentual no deck

### 2. Comparação de Decks
- Compara seu deck contra decks do meta/oponentes
- Identifica cartas em comum e únicas
- Analisa vantagens de matchup (tipos, consistência, velocidade)
- Suporta comparação contra múltiplos decks
- Gera resumo de matchups

### 3. Sugestão de Deck por Pokemon
- Busca um Pokemon pelo nome
- Identifica em quais coleções/sets o Pokemon aparece
- Mostra status de legalidade (Legal, Rotacionando, Ilegal)
- **NOVO**: Integração com base de dados do meta competitivo
- Sugere arquétipos de deck baseados no tipo do Pokemon
- Inclui lista de cartas-chave, estratégia, forças e fraquezas

### 4. Base de Dados do Meta (NOVO)
- **Top 8 decks competitivos** com listas completas (60 cartas)
- **Taxas de vitória (win rates)** entre todos os matchups
- **Suporte bilíngue**: Português e Inglês
- Informações detalhadas: estratégia, pontos fortes/fracos, dificuldade
- Encontrar **counter decks** para qualquer deck do meta

### 5. Tabela de Matchups (NOVO)
- Matriz visual de win rates entre todos os decks
- Indicadores de favorecido/desfavorecido/equilibrado
- Notas explicativas para cada matchup

### 6. Deck Builder com Matchups em Tempo Real (NOVO)
- **Construa seu deck** com filtros por habilidade
- **Filtros de Pokemon**: Safeguard, Bench Barrier, Energy Accel, Draw Power, etc.
- **Análise de matchups em tempo real** contra todos os decks do meta
- **Guias de gameplay** detalhados para cada matchup
- **Sugestões de cartas** baseadas nas necessidades do deck
- **Importar de decks do meta** como ponto de partida

### 7. Aplicativo Android
- **Navegue decks do meta** diretamente no celular
- **Interface touch-friendly** com cards e botões grandes
- **Funciona 100% offline** - dados embutidos no app
- **Suporte bilíngue** - alternar entre Português e Inglês
- **5 telas**: Home, Meta Decks, Detalhes, Matchups, Busca
- Desenvolvido com **Kivy** para multiplataforma

---

## Instalação

### Com ambiente virtual (recomendado)

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Instalação rápida (se permitido)

```bash
pip install -r requirements.txt
```

### Dependências
- `httpx` - Cliente HTTP para APIs
- `rich` - Interface CLI com formatação

---

## Uso

### Modo Interativo
```bash
python main.py
```

Exibe um menu com opções:
1. Análise de rotação
2. Comparação de decks
3. Ambos
4. Sugestão de deck por Pokemon
5. Navegar Decks do Meta (Top 9)
6. Ver Tabela de Matchups
7. **Deck Builder** *(NOVO)* - Construa decks com filtros e matchups
L. Alternar Idioma (EN/PT)
q. Sair

### Com Arquivo
```bash
python main.py meu_deck.txt
```

### Opções de Linha de Comando

| Opção | Descrição |
|-------|-----------|
| `-r`, `--rotation` | Apenas análise de rotação |
| `-c`, `--compare` | Apenas comparação de decks |
| `-s`, `--suggest [nome]` | Sugestão de deck para um Pokemon |
| `-m`, `--meta` | Navegar decks do meta *(NOVO)* |
| `--matchups` | Ver tabela de matchups *(NOVO)* |
| `--lang [en\|pt]` | Definir idioma (English/Português) *(NOVO)* |
| `--vs <arquivo>` | Comparar contra deck específico |
| `-h`, `--help` | Exibir ajuda |

### Exemplos

```bash
# Modo interativo
python main.py

# Analisar deck de arquivo
python main.py meu_deck.txt

# Apenas rotação
python main.py meu_deck.txt -r

# Apenas comparação
python main.py meu_deck.txt -c

# Comparar contra deck específico
python main.py meu_deck.txt --vs oponente.txt

# Comparar contra múltiplos decks
python main.py meu_deck.txt --vs lugia.txt --vs charizard.txt

# Sugerir deck para um Pokemon
python main.py -s Charizard

# Sugerir deck com nome composto
python main.py --suggest "Pikachu ex"

# Navegar decks do meta (NOVO)
python main.py -m

# Ver tabela de matchups (NOVO)
python main.py --matchups

# Decks do meta em português (NOVO)
python main.py -m --lang pt

# Sugestão em português (NOVO)
python main.py -s Gardevoir --lang pt
```

---

## Base de Dados do Meta - Janeiro 2026

### Top 9 Decks Competitivos (Atualizado com Ascended Heroes)

| # | Deck | Meta Share | Tier | Dificuldade |
|---|------|------------|------|-------------|
| 1 | **Gholdengo ex** | 26.49% | 1 | Intermediário |
| 2 | **Dragapult ex** | 19.95% | 1 | Intermediário |
| 3 | **Gardevoir ex / Mega Gardevoir ex** | 15.80% | 1 | Avançado |
| 4 | **Charizard ex / Mega Charizard Y ex** | 14.50% | 1 | Iniciante |
| 5 | **Raging Bolt ex / Ogerpon ex** | 8.50% | 1 | Iniciante |
| 6 | **Marnie's Grimmsnarl ex / Mega Froslass ex** | 7.20% | 1 | Avançado |
| 7 | **Mega Dragonite ex** *(NOVO - ASC)* | 5.50% | 1 | Intermediário |
| 8 | **Joltik Box** | 4.80% | 2 | Intermediário |
| 9 | **Flareon ex** | 3.20% | 2 | Iniciante |

### Matriz de Matchups (Win Rates)

|              | Gholdengo | Dragapult | Gardevoir | Charizard | Raging Bolt | Grimmsnarl | Joltik | Flareon |
|--------------|-----------|-----------|-----------|-----------|-------------|------------|--------|---------|
| **Gholdengo**    | - | 55% | 48% | 60% | 50% | 55% | 52% | 25% |
| **Dragapult**    | 45% | - | 40% | 55% | 45% | 50% | 48% | 55% |
| **Gardevoir**    | 52% | 60% | - | 45% | 60% | 35% | 52% | 50% |
| **Charizard**    | 40% | 45% | 55% | - | 45% | 55% | 50% | 65% |
| **Raging Bolt**  | 50% | 55% | 40% | 55% | - | 60% | 52% | 55% |
| **Grimmsnarl**   | 45% | 50% | 65% | 45% | 40% | - | 48% | 60% |
| **Joltik**       | 48% | 52% | 48% | 50% | 48% | 52% | - | 55% |
| **Flareon**      | 75% | 45% | 50% | 35% | 45% | 40% | 45% | - |

**Legenda**: Verde (55%+) = Favorecido | Amarelo (46-54%) = Equilibrado | Vermelho (45%-) = Desfavorecido

### Exemplo de Navegação do Meta

```
╭──────────────────────────────────────────╮
│ Top 8 Meta Decks - January 2026          │
╰──────────────────────────────────────────╯

                    Meta Tier List
╭───┬──────────────────────────────┬──────┬────────────┬───────────────╮
│ # │ Deck                         │ Tier │ Meta Share │ Difficulty    │
├───┼──────────────────────────────┼──────┼────────────┼───────────────┤
│ 1 │ Gholdengo ex                 │  1   │     26.5%  │ Intermediate  │
│ 2 │ Dragapult ex                 │  1   │     20.0%  │ Intermediate  │
│ 3 │ Gardevoir ex                 │  1   │     16.6%  │ Advanced      │
│ 4 │ Charizard ex / Pidgeot ex    │  1   │     13.9%  │ Beginner      │
│ 5 │ Raging Bolt ex / Ogerpon ex  │  1   │      8.5%  │ Beginner      │
│ 6 │ Marnie's Grimmsnarl ex       │  1   │      6.5%  │ Advanced      │
│ 7 │ Joltik Box                   │  2   │      4.8%  │ Intermediate  │
│ 8 │ Flareon ex                   │  2   │      3.2%  │ Beginner      │
╰───┴──────────────────────────────┴──────┴────────────┴───────────────╯

Enter deck number to view details (or 'q' to go back): 1
```

### Exemplo de Detalhes do Deck

```
╭─────────────────────────────────────────────────────────────────────────────╮
│ Gholdengo ex                                                                │
│ The #1 deck in the meta with incredible draw power and infinite damage      │
│                                                                             │
│ Tier: 1  |  Meta Share: 26.5%  |  Difficulty: Intermediate                  │
╰─────────────────────────────────────────────────────────────────────────────╯

Strategy:
  Use Gholdengo ex's Coin Bonus ability to draw cards each turn...

Key Pokemon: Gholdengo ex, Genesect ex, Gimmighoul
Energy: Metal, Basic

╭──────────────────────────────────────┬──────────────────────────────────────╮
│ Strengths                            │ Weaknesses                           │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Highest damage ceiling in format     │ Weak to Fire (Flareon ex)            │
│ Excellent draw power with Coin Bonus │ Needs many energy in hand            │
│ Can OHKO any Pokemon                 │ Struggles against disruption         │
╰──────────────────────────────────────┴──────────────────────────────────────╯

Matchups:
╭──────────────────────┬──────────┬────────────┬─────────────────────────────╮
│ vs                   │ Win Rate │            │ Notes                       │
├──────────────────────┼──────────┼────────────┼─────────────────────────────┤
│ Charizard ex         │    60%   │ Favored    │ Can OHKO before setup       │
│ Dragapult ex         │    55%   │ Favored    │ OHKO potential advantage    │
│ Grimmsnarl ex        │    55%   │ Favored    │ Grimmsnarl lacks OHKOs      │
│ Joltik Box           │    52%   │ Even       │ Higher damage ceiling       │
│ Raging Bolt ex       │    50%   │ Even       │ Depends on who goes first   │
│ Gardevoir ex         │    48%   │ Even       │ Playable with good exec     │
│ Flareon ex           │    25%   │ Unfavored  │ Flareon deals double damage │
╰──────────────────────┴──────────┴────────────┴─────────────────────────────╯
```

### Exemplo de Lista Completa (Bilíngue)

**Inglês:**
```
Pokemon (16):
  4 Gimmighoul PRE 86
  3 Gholdengo ex PRE 164
  2 Genesect ex JTG 51
  ...

Trainer (29):
  4 Iono PAL 185
  4 Arven OBF 186
  ...

Energy (15):
  4 Basic Metal Energy SVE 8
  ...

Total: 60
```

**Português:**
```
Pokemon (16):
  4 Gimmighoul PRE 86
  3 Gholdengo ex PRE 164
  2 Genesect ex JTG 51
  ...

Treinador (29):
  4 Iono PAL 185
  4 Arven OBF 186
  2 Ordens do Chefe PAL 172
  ...

Energia (15):
  4 Energia Metal Basica SVE 8
  ...

Total: 60
```

---

## Formato de Deck (PTCGO)

O formato aceito é o mesmo exportado pelo Pokemon TCG Live:

```
Pokemon: 18
4 Charizard ex OBF 125
4 Charmander MEW 4
3 Charmeleon OBF 27
2 Pidgeot ex OBF 164
2 Pidgey OBF 162
1 Pidgeotto OBF 163
1 Manaphy BRS 41

Trainer: 31
4 Arven OBF 186
4 Iono PAL 185
2 Boss's Orders PAL 172
4 Rare Candy SVI 191
4 Ultra Ball SVI 196
4 Nest Ball SVI 181
2 Super Rod PAL 188
2 Switch SVI 194

Energy: 10
6 Basic Fire Energy SVE 2
4 Reversal Energy PAL 192
```

---

## Sobre a Rotação

Em **março de 2026**, todas as cartas com **Regulation Mark G** sairão do formato Standard:

| Set | Código | Status |
|-----|--------|--------|
| Scarlet & Violet | SVI | Rotaciona |
| Paldea Evolved | PAL | Rotaciona |
| Obsidian Flames | OBF | Rotaciona |
| Pokemon 151 | MEW | Rotaciona |
| Paradox Rift | PAR | Rotaciona |
| Paldean Fates | PAF | Rotaciona |

### Regulation Marks

| Mark | Status | Período |
|------|--------|---------|
| **A, B, C** | Ilegal | Sun & Moon (2017-2019) |
| **D, E** | Ilegal | Sword & Shield (2020-2021) |
| **F** | Ilegal | Sword & Shield (2022-2023) |
| **G** | Rotaciona Mar/2026 | Scarlet & Violet (2023-2024) |
| **H** | Legal | Scarlet & Violet (2024-2025) |
| **I** | Legal | Scarlet & Violet (2025-2026) |

---

## Estrutura do Projeto

```
tcg_tool/
├── main.py              # CLI principal com menu interativo
├── meta_database.py     # Base de dados do meta (9 decks)
├── abilities_database.py # Banco de habilidades de Pokemon (NOVO)
├── deck_builder.py      # Construtor de deck com matchups (NOVO)
├── deck_suggest.py      # Sugestão de deck por Pokemon
├── deck_parser.py       # Parser formato PTCGO
├── rotation_checker.py  # Análise de rotação
├── deck_compare.py      # Comparação de decks e matchups
├── substitution.py      # Lógica de substituição
├── card_api.py          # Integração TCGdex/Pokemon TCG API
├── models.py            # Dataclasses (Card, Deck, Substitution)
├── database.py          # SQLite para cache de cartas
├── requirements.txt     # Dependências Python
├── claude.md            # Configurações para Claude Code (NOVO)
├── example_deck.txt     # Deck Charizard ex de exemplo
├── example_opponent.txt # Deck Lugia VSTAR de exemplo
└── android_app/         # Aplicativo Android
    ├── main.py          # App Kivy principal
    ├── meta_data.py     # Dados offline do meta
    ├── buildozer.spec   # Configuração de build
    └── README.md        # Instruções de build
```

---

## Documentação dos Módulos Python

### `main.py` - Interface Principal

**Descrição**: Ponto de entrada da aplicação CLI. Gerencia o menu interativo, parsing de argumentos de linha de comando e orquestra todas as funcionalidades.

**Funcionalidades principais**:
- Menu interativo com 7 opções (rotação, comparação, sugestão, meta, matchups, idioma)
- Parsing de argumentos CLI (-r, -c, -s, -m, --matchups, --lang)
- Funções de exibição formatada com Rich (tabelas, painéis, cores)
- Gerenciamento de idioma global (CURRENT_LANGUAGE)

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `main()` | Ponto de entrada, processa args e inicia modo apropriado |
| `print_menu()` | Exibe menu principal com opções |
| `run_browse_meta_decks()` | Navega pelos top 8 decks do meta |
| `run_view_matchups()` | Exibe matriz de matchups |
| `run_deck_suggestion()` | Fluxo de sugestão de deck |
| `print_meta_deck_detail()` | Exibe detalhes de um deck do meta |
| `print_meta_deck_list()` | Exibe lista completa de 60 cartas |
| `run_rotation_analysis()` | Executa análise de rotação |
| `run_deck_comparison()` | Executa comparação entre decks |

---

### `meta_database.py` - Base de Dados do Meta (NOVO)

**Descrição**: Contém dados completos dos 8 melhores decks competitivos com suporte bilíngue, incluindo listas de 60 cartas, matchups e estatísticas.

**Classes principais**:

```python
class Language(Enum):
    EN = "en"  # Inglês
    PT = "pt"  # Português

@dataclass
class CardEntry:
    quantity: int          # Quantidade (1-4)
    name_en: str           # Nome em inglês
    name_pt: str           # Nome em português
    set_code: str          # Código do set (OBF, PAL, etc.)
    set_number: str        # Número da carta
    card_type: str         # "pokemon", "trainer", "energy"

@dataclass
class MetaDeck:
    id: str                # Identificador único
    name_en: str           # Nome em inglês
    name_pt: str           # Nome em português
    tier: int              # Tier (1, 2 ou 3)
    description_en/pt: str # Descrição do deck
    strategy_en/pt: str    # Estratégia detalhada
    difficulty: str        # Beginner/Intermediate/Advanced
    cards: list[CardEntry] # Lista completa de 60 cartas
    strengths_en/pt: list  # Pontos fortes
    weaknesses_en/pt: list # Pontos fracos
    key_pokemon: list[str] # Pokemon principais
    energy_types: list[str]# Tipos de energia
    meta_share: float      # % do meta

@dataclass
class MatchupData:
    deck_a_id: str         # ID do deck A
    deck_b_id: str         # ID do deck B
    win_rate_a: float      # Win rate do deck A (0-100)
    notes_en/pt: str       # Notas explicativas
```

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `get_matchup(deck_a, deck_b)` | Retorna dados de matchup entre dois decks |
| `get_deck_matchups(deck_id)` | Retorna todos os matchups de um deck |
| `calculate_meta_score(deck_id)` | Calcula pontuação ponderada pelo meta |
| `get_best_deck_against(opponents)` | Encontra melhor deck contra lista de oponentes |
| `get_tier_list(lang)` | Retorna decks organizados por tier |
| `search_deck_by_pokemon(name)` | Busca decks que contêm um Pokemon |
| `get_translation(key, lang)` | Retorna tradução de elemento UI |

**Dados incluídos**:
- 9 decks completos com 60 cartas cada (atualizado com Ascended Heroes)
- 36+ matchups com win rates e notas
- Traduções para todas as strings de UI

---

### `abilities_database.py` - Banco de Habilidades (NOVO)

**Descrição**: Base de dados de Pokemon organizados por categoria de habilidade, permitindo filtros avançados na construção de decks.

**Classes principais**:

```python
class AbilityCategory(Enum):
    SAFEGUARD = "safeguard"           # Previne dano de ex/V
    BENCH_BARRIER = "bench_barrier"    # Protege banco
    DAMAGE_REDUCTION = "damage_reduction"
    ENERGY_ACCEL = "energy_accel"
    DRAW_POWER = "draw_power"
    SEARCH = "search"
    SPREAD_DAMAGE = "spread_damage"
    SNIPE = "snipe"
    SWITCHING = "switching"
    MEGA = "mega"
    TERA = "tera"
    # ... 20+ categorias

@dataclass
class PokemonAbility:
    name: str              # Nome da habilidade
    name_pt: str           # Nome em português
    effect_en: str         # Efeito em inglês
    effect_pt: str         # Efeito em português
    category: AbilityCategory

@dataclass
class PokemonCard:
    name_en: str           # Nome em inglês
    name_pt: str           # Nome em português
    set_code: str          # Código do set
    set_number: str        # Número da carta
    hp: int                # Pontos de vida
    energy_type: str       # Tipo de energia
    stage: str             # Basic, Stage 1, Stage 2, ex, Mega
    abilities: list[PokemonAbility]
    attack_categories: list[AbilityCategory]
    is_ex: bool
    is_mega: bool
    is_tera: bool
```

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `search_pokemon(name, type, ability, ...)` | Busca com múltiplos filtros |
| `get_pokemon_by_ability(category)` | Pokemon por categoria de habilidade |
| `get_pokemon_by_type(energy_type)` | Pokemon por tipo de energia |
| `get_ex_pokemon()` | Todos os Pokemon ex |
| `get_mega_pokemon()` | Todos os Mega Pokemon |
| `get_counters_for_ability(ability)` | Counters para uma habilidade |

**Pokemon cadastrados**:
- Safeguard: Mimikyu, Miltank
- Bench Barrier: Manaphy, Jirachi
- Energy Accel: Gardevoir ex, Charizard ex, Ogerpon ex
- Draw Power: Kirlia, Bibarel, Gholdengo ex
- Spread: Froslass, Munkidori, Mega Froslass ex
- Mega (ASC): Dragonite, Charizard Y, Gardevoir, Froslass, Lucario, Hawlucha

---

### `deck_builder.py` - Construtor de Deck (NOVO)

**Descrição**: Módulo interativo para construção de decks com análise de matchups em tempo real e geração de guias de gameplay.

**Classes principais**:

```python
@dataclass
class DeckBuilderCard:
    name_en: str
    name_pt: str
    set_code: str
    set_number: str
    quantity: int
    card_type: str         # "pokemon", "trainer", "energy"
    hp: int
    energy_type: str
    abilities: list[AbilityCategory]
    is_ex: bool
    is_mega: bool

@dataclass
class DeckBuilderState:
    cards: list[DeckBuilderCard]
    deck_name: str

    # Properties
    total_cards -> int
    pokemon_count -> int
    trainer_count -> int
    energy_count -> int
    is_valid -> bool       # 60 cards
    main_attackers -> list
    deck_abilities -> list[AbilityCategory]

@dataclass
class MatchupResult:
    opponent_name: str
    opponent_id: str
    win_rate: float        # 0-100
    confidence: str        # "High", "Medium", "Low"
    key_factors: list[str]
    tips_en: list[str]
    tips_pt: list[str]

@dataclass
class GameplayGuide:
    opponent_name: str
    win_rate: float
    difficulty: str        # "Easy", "Medium", "Hard"
    early_game_priority_en: list[str]
    mid_game_strategy_en: list[str]
    late_game_focus_en: list[str]
    key_threats_en: list[str]
    priority_targets_en: list[str]
```

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `analyze_all_matchups(deck)` | Análise contra todos os decks do meta |
| `generate_all_guides(deck, matchups)` | Gera guias para todos os matchups |
| `calculate_matchup_vs_meta_deck()` | Calcula matchup específico |
| `calculate_overall_meta_score()` | Pontuação geral no meta |
| `suggest_cards_for_deck(deck)` | Sugere cartas para melhorar |
| `add_pokemon_to_deck(deck, key, qty)` | Adiciona Pokemon |
| `add_trainer_to_deck(deck, ...)` | Adiciona Trainer |
| `add_energy_to_deck(deck, type, qty)` | Adiciona Energy |

**Fatores de matchup analisados**:
- Vantagem de tipo (fraqueza/resistência)
- Habilidades vs estratégia do oponente
- Safeguard vs decks ex-heavy
- Bench Barrier vs spread damage
- Velocidade e consistência do deck

---

### `deck_suggest.py` - Sugestão de Deck

**Descrição**: Motor de sugestão de deck que integra a base de dados do meta e APIs externas para recomendar decks baseados em Pokemon específicos.

**Classes principais**:

```python
@dataclass
class PokemonInfo:
    name: str              # Nome do Pokemon
    set_code: str          # Código do set
    number: str            # Número da carta
    regulation_mark: str   # Mark de regulação (G, H, I)
    types: list[str]       # Tipos (Fire, Water, etc.)
    hp: int                # Pontos de vida
    is_ex/is_v/is_vstar/is_vmax: bool  # Variantes
    attacks: list[dict]    # Lista de ataques
    abilities: list[dict]  # Lista de habilidades

@dataclass
class DeckSuggestion:
    archetype_name: str    # Nome do arquétipo
    description: str       # Descrição do deck
    pokemon: PokemonInfo   # Pokemon principal
    strategy: str          # Estratégia de jogo
    key_cards: list[str]   # Cartas essenciais
    energy_types: list[str]# Tipos de energia
    strengths: list[str]   # Pontos fortes
    weaknesses: list[str]  # Pontos fracos
    difficulty: str        # Nível de dificuldade

@dataclass
class MetaDeckSuggestion:
    deck: MetaDeck         # Deck do meta
    relevance_score: float # Relevância para busca (0-100)
    meta_score: float      # Viabilidade no meta
    matchups: list[tuple]  # Lista de matchups
```

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `suggest_meta_deck_for_pokemon(name, lang)` | Busca decks do meta com Pokemon |
| `get_top_meta_decks(limit, lang)` | Retorna top decks do meta |
| `get_deck_counter(deck_id, lang)` | Encontra melhor counter |
| `suggest_deck_for_pokemon(name)` | Sugestão genérica por tipo |
| `find_pokemon_cards(name)` | Busca Pokemon nas APIs |
| `get_pokemon_collections(name)` | Agrupa por set/coleção |
| `get_legal_status(reg_mark, lang)` | Status de legalidade |
| `format_deck_suggestion_bilingual()` | Formata para exibição |

**Arquétipos suportados**:
| Tipo | Parceiros | Estratégia |
|------|-----------|------------|
| Fire | Arcanine, Entei | Aceleração agressiva |
| Water | Palkia, Kyogre | Controle e sinergia |
| Lightning | Miraidon, Regieleki | Energia rápida |
| Psychic | Gardevoir, Mew | Manipulação de energia |
| Fighting | Lucario, Machamp | Dano alto |
| Darkness | Darkrai, Zoroark | Controle e aceleração |
| Metal | Dialga, Archaludon | Tanques com recuperação |
| Dragon | Rayquaza, Regidrago | Dano multi-energia |
| Grass | Sceptile, Venusaur | Cura e eficiência |
| Colorless | Lugia, Archeops | Flexibilidade |

---

### `deck_parser.py` - Parser de Deck

**Descrição**: Converte texto no formato PTCGO em estruturas de dados do sistema. Detecta automaticamente tipos de cartas e normaliza códigos de sets.

**Funcionalidades**:
- Parse de formato PTCGO (Pokemon TCG Live export)
- Detecção automática de tipo (Pokemon, Trainer, Energy)
- Detecção de subtipo de Trainer (Supporter, Item, Stadium, Tool)
- Normalização de códigos de set (OBF → sv3)
- Suporte a comentários (# ou //)
- Regex para parsing: `(\d+)\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)`

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `parse_deck(text)` | Converte texto PTCGO em objeto Deck |
| `parse_card_line(line)` | Parse de uma linha de carta |
| `detect_card_type(name)` | Detecta Pokemon/Trainer/Energy |
| `detect_trainer_subtype(name)` | Detecta Supporter/Item/Stadium |
| `normalize_set_code(code)` | Normaliza código do set |

**Keywords para detecção de Trainer**:
```python
SUPPORTER_KEYWORDS = ["professor", "boss", "iono", "arven", "cynthia", ...]
ITEM_KEYWORDS = ["ball", "candy", "catcher", "switch", "rod", ...]
STADIUM_KEYWORDS = ["stadium", "tower", "gym", "basin", "temple", ...]
TOOL_KEYWORDS = ["belt", "cape", "charm", "stone", "board", ...]
```

---

### `rotation_checker.py` - Análise de Rotação

**Descrição**: Analisa decks para identificar cartas afetadas pela rotação de março de 2026 (Regulation Mark G).

**Classes principais**:

```python
@dataclass
class RotationReport:
    rotating_pokemon: list[Card]   # Pokemon rotacionando
    rotating_trainers: list[Card]  # Trainers rotacionando
    rotating_energy: list[Card]    # Energias rotacionando
    safe_pokemon: list[Card]       # Pokemon seguros
    safe_trainers: list[Card]      # Trainers seguros
    safe_energy: list[Card]        # Energias seguras
    illegal_pokemon: list[Card]    # Já ilegais
    illegal_trainers: list[Card]   # Já ilegais
    illegal_energy: list[Card]     # Já ilegais
```

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `analyze_rotation(deck)` | Gera relatório de rotação completo |
| `get_rotation_summary(report)` | Resumo com % e severidade |
| `is_rotating(card)` | Verifica se carta rotaciona (mark G) |
| `is_illegal(card)` | Verifica se já é ilegal (mark ≤ F) |
| `is_safe(card)` | Verifica se é segura (mark ≥ H) |

**Níveis de severidade**:
| Severidade | % de Impacto |
|------------|--------------|
| NONE | 0% |
| LOW | 1-20% |
| MODERATE | 21-40% |
| HIGH | 41-60% |
| CRITICAL | 61%+ |

---

### `deck_compare.py` - Comparação de Decks

**Descrição**: Compara dois decks identificando cartas em comum, diferenças e análise de matchup baseada em tipos e composição.

**Classes principais**:

```python
@dataclass
class DeckComparison:
    deck_a_name: str              # Nome do deck A
    deck_b_name: str              # Nome do deck B
    shared_cards: list[tuple]     # Cartas em comum
    unique_to_a: list[Card]       # Cartas únicas de A
    unique_to_b: list[Card]       # Cartas únicas de B
    similarity_percentage: float  # % de similaridade

@dataclass
class MatchupAnalysis:
    deck_a_name: str              # Nome do deck A
    deck_b_name: str              # Nome do deck B
    matchup_favor: str            # Quem é favorecido
    a_advantages: list[str]       # Vantagens de A
    b_advantages: list[str]       # Vantagens de B
    key_differences: list[str]    # Diferenças principais
```

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `compare_decks(deck_a, deck_b)` | Compara estrutura dos decks |
| `analyze_matchup(deck_a, deck_b)` | Analisa vantagens de matchup |
| `get_main_attackers(deck)` | Identifica atacantes principais |
| `get_type_advantages(attacker, defender)` | Calcula vantagem de tipo |

**Tabela de vantagens de tipo**:
```python
TYPE_WEAKNESSES = {
    "Fire": ["Water"],
    "Water": ["Lightning", "Grass"],
    "Grass": ["Fire"],
    "Lightning": ["Fighting"],
    "Fighting": ["Psychic"],
    "Psychic": ["Darkness"],
    "Darkness": ["Fighting", "Grass"],
    "Metal": ["Fire"],
    "Dragon": ["Dragon", "Fairy"],
    "Colorless": ["Fighting"],
    "Fairy": ["Metal"],
}
```

---

### `substitution.py` - Substituição de Cartas

**Descrição**: Encontra substituições para cartas que rotacionam, usando sistema de pontuação baseado em tipo, função e arquétipo.

**Classes principais**:

```python
@dataclass
class Substitution:
    original_card: Card       # Carta original (rotacionando)
    suggested_card: Card      # Carta substituta sugerida
    match_score: float        # Pontuação de match (0-100)
    reasons: list[str]        # Motivos da sugestão
```

**Sistema de pontuação**:
| Critério | Peso | Descrição |
|----------|------|-----------|
| Tipo/Subtipo | 40% | Pokemon→Pokemon, Supporter→Supporter |
| Função | 40% | Draw, Search, Recovery, etc. |
| Arquétipo | 20% | Compatibilidade de tipo de energia |

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `find_substitutions(cards, new_set)` | Busca substituições em novo set |
| `calculate_match_score(original, candidate)` | Calcula pontuação |
| `generate_updated_deck(cards, subs)` | Gera deck atualizado |
| `get_known_substitutions()` | Mapeamentos conhecidos |

**Funções detectadas**:
```python
class CardFunction(Enum):
    DRAW       # Compra de cartas
    SEARCH     # Busca no deck
    RECOVERY   # Recuperação do descarte
    SWITCHING  # Troca de Pokemon ativo
    ENERGY_ACCEL  # Aceleração de energia
    DISRUPTION # Disrupção do oponente
    SETUP      # Setup/evolução
    PROTECTION # Proteção
    DAMAGE     # Dano
    HEALING    # Cura
```

---

### `card_api.py` - Integração com APIs

**Descrição**: Interface com APIs externas (TCGdex e Pokemon TCG API) para buscar dados de cartas, sets e imagens.

**APIs utilizadas**:
| API | URL Base | Uso | Idiomas |
|-----|----------|-----|---------|
| TCGdex | `https://api.tcgdex.net/v2` | Principal | 10+ |
| Pokemon TCG | `https://api.pokemontcg.io/v2` | Fallback | Inglês |

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `fetch_card_tcgdex(set_code, number)` | Busca carta na TCGdex |
| `fetch_card_pokemontcg(query)` | Busca na Pokemon TCG API |
| `fetch_set_cards_tcgdex(set_code)` | Todas cartas de um set |
| `search_pokemon_by_name(name)` | Busca Pokemon por nome |
| `get_pokemon_details(name, set_code)` | Detalhes completos |
| `parse_tcgdex_card(data)` | Converte JSON para Card |
| `parse_pokemontcg_card(data)` | Converte JSON para Card |
| `detect_functions(card)` | Detecta funções da carta |

**Tratamento de erros**:
- Timeout de 30-60 segundos
- Fallback automático entre APIs
- Cache local via SQLite

---

### `models.py` - Modelos de Dados

**Descrição**: Define todas as estruturas de dados (dataclasses) usadas pelo sistema.

**Classes principais**:

```python
class CardType(Enum):
    POKEMON = "pokemon"
    TRAINER = "trainer"
    ENERGY = "energy"

class CardFunction(Enum):
    DRAW, SEARCH, RECOVERY, SWITCHING,
    ENERGY_ACCEL, DAMAGE, HEALING, DISRUPTION,
    SETUP, PROTECTION, OTHER

@dataclass
class Card:
    name: str               # Nome da carta
    card_type: CardType     # Tipo (Pokemon/Trainer/Energy)
    set_code: str           # Código do set
    set_number: str         # Número no set
    quantity: int = 1       # Quantidade no deck
    regulation_mark: str    # Mark de regulação
    subtype: str            # Subtipo (ex, V, supporter, item)
    hp: int                 # HP (para Pokemon)
    energy_type: str        # Tipo de energia
    abilities: str          # JSON das habilidades
    attacks: str            # JSON dos ataques
    functions: list[CardFunction]  # Funções detectadas

@dataclass
class Deck:
    cards: list[Card]       # Lista de cartas
    name: str = "My Deck"   # Nome do deck

    @property
    def total_cards(self) -> int
    @property
    def pokemon_count(self) -> int
    @property
    def trainer_count(self) -> int
    @property
    def energy_count(self) -> int
    @property
    def rotation_impact(self) -> float
```

---

### `database.py` - Cache SQLite

**Descrição**: Gerencia cache local de cartas usando SQLite para reduzir chamadas às APIs.

**Schema do banco**:
```sql
-- Tabela de sets
CREATE TABLE card_sets (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE,      -- "OBF", "PAL"
    name TEXT,             -- "Obsidian Flames"
    series TEXT,           -- "Scarlet & Violet"
    release_date TEXT,
    regulation_mark TEXT   -- "G", "H", "I"
);

-- Tabela de cartas
CREATE TABLE cards (
    id INTEGER PRIMARY KEY,
    name TEXT,
    card_type TEXT,        -- "pokemon", "trainer", "energy"
    subtype TEXT,          -- "supporter", "item", "stadium"
    set_code TEXT,
    set_number TEXT,
    regulation_mark TEXT,
    hp INTEGER,
    energy_type TEXT,
    abilities TEXT,        -- JSON
    attacks TEXT,          -- JSON
    image_url TEXT,
    UNIQUE(set_code, set_number)
);

-- Índices
CREATE INDEX idx_cards_regulation ON cards(regulation_mark);
CREATE INDEX idx_cards_name ON cards(name);
CREATE INDEX idx_cards_type ON cards(card_type);
```

**Funções principais**:
| Função | Descrição |
|--------|-----------|
| `init_database()` | Inicializa banco se não existir |
| `get_card(set_code, number)` | Busca carta no cache |
| `save_card(card)` | Salva carta no cache |
| `get_cards_by_regulation(mark)` | Cartas por regulation mark |
| `get_cards_by_set(set_code)` | Cartas de um set |
| `clear_cache()` | Limpa todo o cache |

---

## Aplicativo Android

O projeto inclui um aplicativo Android nativo desenvolvido com Kivy para navegar pelos decks do meta diretamente no celular.

### Funcionalidades do App

| Tela | Funcionalidade |
|------|----------------|
| **Home** | Menu principal com navegação e toggle de idioma |
| **Meta Decks** | Lista dos top 8 decks com tier e meta share |
| **Deck Details** | Detalhes completos + lista de 60 cartas |
| **Matchups** | Matriz de win rates entre decks |
| **Search** | Buscar decks por Pokemon |

### Testar no Desktop (sem build)

```bash
# Instalar Kivy
pip install kivy

# Executar (de qualquer diretório)
python android_app/main.py
```

### Gerar APK (Android)

#### Pré-requisitos (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y \
    python3-pip python3-venv git zip unzip \
    openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libncurses-dev libtinfo6 \
    cmake libffi-dev libssl-dev automake
```

#### Build do APK

```bash
cd android_app

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install setuptools kivy buildozer cython

# Gerar APK (primeira build demora ~30 min)
buildozer android debug

# APK gerado em: bin/tcgmeta-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Instalar no Celular

#### Via ADB (USB)

```bash
# Habilite "Depuração USB" no Android
adb install bin/tcgmeta-*.apk
```

#### Via Transferência

1. Copie o arquivo `.apk` para o celular
2. Abra com gerenciador de arquivos
3. Permita instalação de "fontes desconhecidas"

### Estrutura do App

```
android_app/
├── main.py           # App Kivy com 5 telas
├── meta_data.py      # Dados offline (8 decks completos)
├── buildozer.spec    # Configuração Android
└── README.md         # Documentação detalhada
```

### Customização

**Alterar cores** (em `main.py`):
```python
get_color_from_hex('#2196F3')  # Azul (header/botões)
get_color_from_hex('#4CAF50')  # Verde (favorecido)
get_color_from_hex('#F44336')  # Vermelho (desfavorecido)
```

**Adicionar novos decks** (em `meta_data.py`):
```python
META_DECKS["novo_deck"] = MetaDeck(
    id="novo_deck",
    name_en="New Deck",
    name_pt="Novo Deck",
    tier=2,
    # ... campos restantes
)
```

---

## Códigos de Sets Suportados

### Scarlet & Violet Era

| Código | Set | Regulation | Data |
|--------|-----|------------|------|
| SVI | Scarlet & Violet | G | Mar 2023 |
| PAL | Paldea Evolved | G | Jun 2023 |
| OBF | Obsidian Flames | G | Aug 2023 |
| MEW | Pokemon 151 | G | Sep 2023 |
| PAR | Paradox Rift | G | Nov 2023 |
| PAF | Paldean Fates | G | Jan 2024 |
| TEF | Temporal Forces | H | Mar 2024 |
| TWM | Twilight Masquerade | H | May 2024 |
| SFA | Shrouded Fable | H | Aug 2024 |
| SCR | Stellar Crown | H | Sep 2024 |
| SSP | Surging Sparks | H | Nov 2024 |
| PRE | Prismatic Evolutions | I | Jan 2025 |
| JTG | Journey Together | I | Mar 2025 |
| ASC | Ascended Heroes | I | Mai 2025 |
| DRI | Destined Rivals | I | Jul 2025 |
| MEV | Mega Evolution | I | Sep 2025 |
| SVE | Basic Energy | - | Sempre legal |

---

## APIs Utilizadas

| API | Uso | URL |
|-----|-----|-----|
| **TCGdex** | Principal (10+ idiomas) | https://tcgdex.dev |
| **Pokemon TCG API** | Fallback (inglês) | https://pokemontcg.io |

---

## Limitações

- A busca de substituições depende da disponibilidade das cartas na API
- Sets futuros podem não estar disponíveis até o lançamento
- A análise de função é baseada em palavras-chave e pode não ser 100% precisa
- A análise de matchup do meta é baseada em dados da comunidade
- Energias básicas são sempre consideradas legais

---

## Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## Licença

MIT
