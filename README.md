# TCG Rotation Checker

Ferramenta CLI para analisar decks de Pokemon TCG, verificar o impacto da rotação de março de 2026 e comparar matchups contra outros decks.

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
- Sugere arquétipos de deck baseados no tipo do Pokemon
- Inclui lista de cartas-chave, estratégia, forças e fraquezas

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

## Uso

### Modo Interativo
```bash
python main.py
```

Exibe um menu com 4 opções:
1. Análise de rotação
2. Comparação de decks
3. Ambos
4. Sugestão de deck por Pokemon

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
python main.py meu_deck.txt --vs lugia.txt --vs charizard.txt --vs regidrago.txt

# Sugerir deck para um Pokemon
python main.py -s Charizard

# Sugerir deck para Pokemon com nome composto
python main.py --suggest "Pikachu ex"
```

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

### Exemplo de Análise de Rotação

```
╭───────────────────────────── Rotation Analysis ─────────────────────────────╮
│ Impact: 89.8% (CRITICAL)                                                    │
│ Rotating (March 2026): 49 cards                                             │
│ Already Illegal: 4 cards                                                    │
│ Safe: 6 cards                                                               │
╰─────────────────────────────────────────────────────────────────────────────╯

 Already Illegal (Regulation F or earlier)
╭─────┬───────────────────┬─────────┬─────╮
│ Qty │ Card Name         │ Set     │ Reg │
├─────┼───────────────────┼─────────┼─────┤
│   1 │ Rotom V           │ LOR 177 │ F   │
│   1 │ Manaphy           │ BRS 41  │ F   │
│   2 │ Forest Seal Stone │ SIT 156 │ F   │
╰─────┴───────────────────┴─────────┴─────╯

 Rotating March 2026 (Regulation G)
╭─────┬─────────────────┬─────────┬─────────────────────╮
│ Qty │ Card Name       │ Set     │ Type                │
├─────┼─────────────────┼─────────┼─────────────────────┤
│   4 │ Charizard ex    │ OBF 125 │ Pokemon             │
│   4 │ Iono            │ PAL 185 │ Trainer (supporter) │
│   4 │ Ultra Ball      │ SVI 196 │ Trainer (item)      │
╰─────┴─────────────────┴─────────┴─────────────────────╯

 Safe (Regulation H, I or later)
╭─────┬───────────────────┬───────┬─────╮
│ Qty │ Card Name         │ Set   │ Reg │
├─────┼───────────────────┼───────┼─────┤
│   6 │ Basic Fire Energy │ SVE 2 │ H   │
╰─────┴───────────────────┴───────┴─────╯
```

## Comparação de Decks

A análise de matchup considera múltiplos fatores:

### Cartas em Comum
Identifica cartas compartilhadas entre os decks e suas quantidades.

### Vantagens de Tipo
Analisa fraquezas de tipos de Pokemon:

| Atacante | Tem Vantagem Sobre |
|----------|-------------------|
| Fire | Grass, Metal |
| Water | Fire |
| Lightning | Water |
| Fighting | Lightning, Darkness, Colorless |
| Psychic | Fighting |
| Darkness | Psychic |
| Metal | Fairy |
| Dragon | Dragon |

### Métricas de Análise

| Métrica | Descrição |
|---------|-----------|
| **Similaridade** | Porcentagem de cartas em comum |
| **Velocidade** | Baseado em cartas de busca/setup |
| **Consistência** | Baseado em draw supporters |
| **Opções de Ataque** | Quantidade de atacantes principais (ex, V, VSTAR) |

### Exemplo de Comparação

```
╭──────────────────╮
│ Deck Comparison  │
│ Similarity: 8.3% │
╰──────────────────╯

                 Shared Cards (3)
╭───────────────┬──────────────┬──────────────────╮
│ Card Name     │ Your Deck    │ Opponent         │
├───────────────┼──────────────┼──────────────────┤
│ Boss's Orders │            2 │                2 │
│ Iono          │            4 │                4 │
│ Ultra Ball   │            4 │                4 │
╰───────────────┴──────────────┴──────────────────╯

                     Unique Cards
╭──────────────────────┬──────────────────────────────╮
│ Your Deck Only       │ Opponent Only                │
├──────────────────────┼──────────────────────────────┤
│ 4x Charizard ex      │ 3x Lugia VSTAR               │
│ 4x Arven             │ 4x Archeops                  │
│ 4x Rare Candy        │ 4x Double Turbo Energy       │
╰──────────────────────┴──────────────────────────────╯

╭─────────────────────────────╮
│ Matchup Analysis            │
│ Opponent is favored         │
╰─────────────────────────────╯

                  Advantages
╭──────────────┬──────────────────────────────╮
│ Your Deck    │ Opponent                     │
├──────────────┼──────────────────────────────┤
│              │ More attack options (4 vs 3) │
╰──────────────┴──────────────────────────────╯

Key Differences:
  • Opponent runs more Pokemon (24 vs 18)
  • Your Deck runs more Trainers (31 vs 19)
```

### Resumo de Múltiplos Matchups

Quando você compara contra vários decks:

```
╭───────────────────╮
│ Matchup Summary   │
╰───────────────────╯
╭────────────────────┬────────────┬───────────╮
│ Opponent           │ Similarity │ Result    │
├────────────────────┼────────────┼───────────┤
│ Lugia VSTAR        │        8%  │ Unfavored │
│ Charizard ex       │       45%  │ Even      │
│ Regidrago VSTAR    │       12%  │ Favored   │
╰────────────────────┴────────────┴───────────╯
```

## Sugestão de Deck

A funcionalidade de sugestão de deck permite buscar um Pokemon e receber sugestões de decks competitivos.

### Como Funciona

1. **Busca do Pokemon**: O sistema busca o Pokemon nas APIs (TCGdex e Pokemon TCG API)
2. **Identificação de Coleções**: Mostra em quais sets o Pokemon aparece
3. **Análise de Legalidade**: Indica se o Pokemon está legal, rotacionando ou já rotacionou
4. **Sugestões de Deck**: Gera arquétipos de deck baseados nas características do Pokemon

### Exemplo de Saída

```
╭─────────────────────────────╮
│ Collections for Charizard   │
╰─────────────────────────────╯

              Available Sets
╭──────────┬────────────────────┬───────┬────────────┬─────────────────────╮
│ Set Code │ Set Name           │ Cards │ Regulation │ Status              │
├──────────┼────────────────────┼───────┼────────────┼─────────────────────┤
│ OBF      │ Obsidian Flames    │     3 │ G          │ Rotating March 2026 │
│ MEW      │ Pokemon 151        │     2 │ G          │ Rotating March 2026 │
│ PAF      │ Paldean Fates      │     1 │ G          │ Rotating March 2026 │
╰──────────┴────────────────────┴───────┴────────────┴─────────────────────╯

Card Variants:
  • Charizard ex (OBF 125) ex Fire HP 330
  • Charizard (OBF 26) Fire HP 170
  • Charizard ex (MEW 6) ex Fire HP 330

╭─────────────────────────────────────╮
│ Deck Suggestions for Charizard      │
╰─────────────────────────────────────╯

╭─────────────── Suggestion #1 ────────────────╮
│ Charizard ex / Arcanine                      │
│ A Fire-type deck featuring Charizard ex      │
│                                              │
│ Difficulty: Beginner                         │
╰──────────────────────────────────────────────╯

Main Attacker: Charizard ex
  Set: OBF 125
  Regulation: G (Rotating March 2026)
  HP: 330
  Type: Fire

Strategy: Aggressive damage with Fire-type acceleration

         Key Cards
╭───────────────────────╮
│ 4 Charizard ex        │
│ 4 Charizard (Basic)   │
│ 4 Rare Candy          │
│ 4 Ultra Ball          │
│ 4 Nest Ball           │
│ 4 Iono                │
│ 4 Arven               │
│ 2 Boss's Orders       │
│ 2-4 Magma Basin       │
╰───────────────────────╯

Energy:
  • Basic Fire Energy

╭───────────────────────────────┬─────────────────────────────────╮
│ Strengths                     │ Weaknesses                      │
├───────────────────────────────┼─────────────────────────────────┤
│ Strong against Grass/Metal    │ Weak to Water                   │
│ Good energy acceleration      │ Energy intensive                │
│ High HP (330)                 │ Gives 2 prize cards when KO'd   │
╰───────────────────────────────┴─────────────────────────────────╯
```

### Tipos de Pokemon Suportados

| Tipo | Parceiros Comuns | Estratégia |
|------|------------------|------------|
| Fire | Arcanine, Entei, Magcargo | Aceleração de energia agressiva |
| Water | Palkia, Kyogre, Greninja | Controle e sinergias Water |
| Lightning | Pikachu, Miraidon, Regieleki | Aceleração rápida de energia |
| Psychic | Gardevoir, Mewtwo, Mew | Manipulação de energia Psychic |
| Fighting | Lucario, Machamp, Buzzwole | Dano alto com bônus Fighting |
| Darkness | Darkrai, Zoroark, Umbreon | Aceleração Dark e controle |
| Metal | Dialga, Metagross, Archaludon | Pokemon tanques com recuperação |
| Dragon | Rayquaza, Dragonite, Regidrago | Dano alto com energia multi-tipo |
| Grass | Sceptile, Venusaur, Decidueye | Cura e eficiência de energia |
| Colorless | Lugia, Pidgeot, Archeops | Flexível com qualquer energia |

### Níveis de Dificuldade

| Nível | Descrição |
|-------|-----------|
| **Beginner** | Decks ex/V simples, fáceis de jogar |
| **Intermediate** | Decks VSTAR/VMAX com VSTAR Powers |
| **Advanced** | Decks Stage 2, combos complexos |

## Critérios de Substituição

Para rotação, as substituições são calculadas com três critérios:

| Critério | Peso | Descrição |
|----------|------|-----------|
| **Tipo/Subtipo** | 40% | Pokemon→Pokemon, Supporter→Supporter, Item→Item |
| **Função** | 40% | Draw, Search, Recovery, Switching, etc. |
| **Arquétipo** | 20% | Compatibilidade de tipo de energia |

### Funções Detectadas

| Função | Palavras-chave | Exemplos |
|--------|----------------|----------|
| Draw | draw, draws | Professor's Research, Iono |
| Search | search, look at, find | Ultra Ball, Nest Ball |
| Recovery | discard pile, put back | Super Rod, Night Stretcher |
| Switching | switch, retreat | Switch, Escape Rope |
| Energy Accel | attach, energy to | Magma Basin, Earthen Vessel |
| Disruption | opponent's hand | Iono, Roxanne |
| Setup | evolve, put onto | Rare Candy, Buddy-Buddy Poffin |
| Protection | prevent, can't be | Manaphy (ability) |

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
| SVE | Basic Energy | - | Sempre legal |

### Sword & Shield Era (Referência)

| Código | Set | Regulation |
|--------|-----|------------|
| BRS | Brilliant Stars | F |
| ASR | Astral Radiance | F |
| LOR | Lost Origin | F |
| SIT | Silver Tempest | F |
| CRZ | Crown Zenith | F |

## Estrutura do Projeto

```
tcg_tool/
├── main.py              # CLI principal com menu
├── deck_parser.py       # Parser formato PTCGO
├── rotation_checker.py  # Análise de rotação
├── deck_compare.py      # Comparação de decks e matchups
├── deck_suggest.py      # Sugestão de deck por Pokemon
├── substitution.py      # Lógica de substituição
├── card_api.py          # Integração TCGdex/Pokemon TCG API
├── models.py            # Dataclasses (Card, Deck, Substitution)
├── database.py          # SQLite para cache de cartas
├── requirements.txt     # Dependências Python
├── example_deck.txt     # Deck Charizard ex de exemplo
└── example_opponent.txt # Deck Lugia VSTAR de exemplo
```

## APIs Utilizadas

| API | Uso | URL |
|-----|-----|-----|
| **TCGdex** | Principal (10+ idiomas) | https://tcgdex.dev |
| **Pokemon TCG API** | Fallback (inglês) | https://pokemontcg.io |

## Limitações

- A busca de substituições depende da disponibilidade das cartas na API
- Sets futuros (como ASC - Ascended Heroes) podem não estar disponíveis até o lançamento
- A análise de função é baseada em palavras-chave e pode não ser 100% precisa
- A análise de matchup é simplificada e não considera combos específicos ou meta-game
- Energias básicas são sempre consideradas legais

## Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

MIT
