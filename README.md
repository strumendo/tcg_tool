# TCG Rotation Checker

Ferramenta CLI para analisar decks de Pokemon TCG, verificar o impacto da rotação de março de 2026 e comparar matchups contra outros decks.

## Funcionalidades

### 1. Análise de Rotação
- Identifica cartas com **Regulation Mark G** que rotacionam em março 2026
- Detecta cartas já ilegais (Regulation Mark F ou anterior)
- Busca substituições na coleção Ascended Heroes (ASC)

### 2. Comparação de Decks
- Compara seu deck contra decks do meta/oponentes
- Identifica cartas em comum e únicas
- Analisa vantagens de matchup (tipos, consistência, velocidade)
- Suporta comparação contra múltiplos decks

## Instalação

```bash
pip install -r requirements.txt
```

Dependências:
- `httpx` - Cliente HTTP para APIs
- `rich` - Interface CLI com formatação

## Uso

### Modo Interativo
```bash
python main.py
```

Exibe um menu com 3 opções:
1. Análise de rotação
2. Comparação de decks
3. Ambos

### Com Arquivo
```bash
python main.py meu_deck.txt
```

### Opções de Linha de Comando

```bash
# Apenas análise de rotação
python main.py meu_deck.txt -r

# Apenas comparação de decks
python main.py meu_deck.txt -c

# Comparar contra deck específico
python main.py meu_deck.txt --vs oponente.txt

# Comparar contra múltiplos decks
python main.py meu_deck.txt --vs lugia.txt --vs charizard.txt

# Ajuda
python main.py -h
```

## Formato de Deck (PTCGO)

O formato aceito é o mesmo exportado pelo Pokemon TCG Live:

```
Pokemon: 18
4 Charizard ex OBF 125
4 Charmander MEW 4
3 Charmeleon OBF 27
2 Pidgeot ex OBF 164

Trainer: 31
4 Arven OBF 186
4 Iono PAL 185
4 Rare Candy SVI 191
4 Ultra Ball SVI 196

Energy: 10
6 Basic Fire Energy SVE 2
4 Reversal Energy PAL 192
```

## Sobre a Rotação

Em **março de 2026**, todas as cartas com **Regulation Mark G** sairão do formato Standard:
- Scarlet & Violet (SVI)
- Paldea Evolved (PAL)
- Obsidian Flames (OBF)
- Pokemon 151 (MEW)
- Paradox Rift (PAR)
- Paldean Fates (PAF)

### Regulation Marks

| Mark | Status | Sets |
|------|--------|------|
| **D, E** | Já rotacionou | Sword & Shield 2020-2021 |
| **F** | Já rotacionou | Sword & Shield 2022-2023 |
| **G** | Rotaciona Mar/2026 | SVI, PAL, OBF, MEW, PAR, PAF |
| **H** | Seguro | TEF, TWM, SFA, SCR, SSP |
| **I** | Novo | PRE, JTG, ASC |

## Comparação de Decks

A análise de matchup considera:

### Cartas em Comum
Identifica cartas compartilhadas entre os decks e suas quantidades.

### Vantagens de Tipo
Analisa fraquezas de tipos de Pokemon:
- Fire > Grass
- Water > Fire
- Lightning > Water
- Fighting > Lightning, Darkness
- Psychic > Fighting
- etc.

### Métricas de Análise

| Métrica | Descrição |
|---------|-----------|
| **Similaridade** | Porcentagem de cartas em comum |
| **Velocidade** | Baseado em cartas de busca/setup |
| **Consistência** | Baseado em draw supporters |
| **Opções de Ataque** | Quantidade de atacantes principais |

### Exemplo de Comparação

```
╭──────────────────╮
│ Deck Comparison  │
│ Similarity: 8.3% │
╰──────────────────╯

     Shared Cards (3)
╭───────────────┬────┬────╮
│ Card Name     │ A  │ B  │
├───────────────┼────┼────┤
│ Boss's Orders │  2 │  2 │
│ Iono          │  4 │  4 │
│ Ultra Ball   │  4 │  4 │
╰───────────────┴────┴────╯

╭─────────────────────────────╮
│ Matchup Analysis            │
│ Example Opponent is favored │
╰─────────────────────────────╯
```

## Critérios de Substituição

Para rotação, as substituições são calculadas com:

| Critério | Peso | Descrição |
|----------|------|-----------|
| **Tipo/Subtipo** | 40% | Pokemon→Pokemon, Supporter→Supporter |
| **Função** | 40% | Draw, Search, Recovery, Switching |
| **Arquétipo** | 20% | Compatibilidade de tipo de energia |

### Funções Detectadas

| Categoria | Exemplos |
|-----------|----------|
| Draw | Professor's Research, Iono |
| Search | Ultra Ball, Nest Ball |
| Recovery | Super Rod, Night Stretcher |
| Switching | Switch, Escape Rope |
| Energy Accel | Attachar energia do deck/descarte |
| Disruption | Iono, Boss's Orders |
| Setup | Rare Candy, evolução |

## Códigos de Sets

| Código | Set | Regulation |
|--------|-----|------------|
| SVI | Scarlet & Violet | G |
| PAL | Paldea Evolved | G |
| OBF | Obsidian Flames | G |
| MEW | Pokemon 151 | G |
| PAR | Paradox Rift | G |
| PAF | Paldean Fates | G |
| TEF | Temporal Forces | H |
| TWM | Twilight Masquerade | H |
| SFA | Shrouded Fable | H |
| SCR | Stellar Crown | H |
| SSP | Surging Sparks | H |
| PRE | Prismatic Evolutions | I |
| JTG | Journey Together | I |
| ASC | Ascended Heroes | I |
| SVE | Basic Energy | Sempre legal |

## Estrutura do Projeto

```
tcg_tool/
├── main.py              # CLI principal
├── deck_parser.py       # Parser formato PTCGO
├── rotation_checker.py  # Análise de rotação
├── deck_compare.py      # Comparação de decks
├── substitution.py      # Lógica de substituição
├── card_api.py          # Integração com APIs
├── models.py            # Dataclasses
├── database.py          # SQLite para cache
├── requirements.txt     # Dependências
├── example_deck.txt     # Deck de exemplo
└── example_opponent.txt # Oponente de exemplo
```

## APIs Utilizadas

- **TCGdex** (principal): https://tcgdex.dev
- **Pokemon TCG API** (fallback): https://pokemontcg.io

## Limitações

- A busca de substituições depende da disponibilidade das cartas na API
- Sets futuros (como ASC) podem não estar disponíveis até o lançamento
- A análise de função é baseada em palavras-chave e pode não ser 100% precisa
- A análise de matchup é simplificada e não considera combos específicos

## Licença

MIT
