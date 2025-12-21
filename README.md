# TCG Rotation Checker

Ferramenta CLI para analisar decks de Pokemon TCG e verificar o impacto da rotação de março de 2026.

## Sobre a Rotação

Em **março de 2026**, todas as cartas com **Regulation Mark G** sairão do formato Standard. Isso inclui os sets:
- Scarlet & Violet (SVI)
- Paldea Evolved (PAL)
- Obsidian Flames (OBF)
- Pokemon 151 (MEW)
- Paradox Rift (PAR)
- Paldean Fates (PAF)

## O que a ferramenta faz

1. **Analisa seu deck** - Cole seu deck no formato PTCGO
2. **Categoriza as cartas**:
   - 🔴 **Rotacionando** - Regulation Mark G (sai em março 2026)
   - 🟣 **Já Ilegal** - Regulation Mark F ou anterior (já rotacionou)
   - 🟢 **Seguro** - Regulation Mark H, I ou posterior
3. **Busca substituições** - Procura cartas equivalentes na coleção Ascended Heroes (ASC)
4. **Calcula compatibilidade** - Análise percentual baseada em tipo, função e arquétipo

## Instalação

```bash
pip install -r requirements.txt
```

Dependências:
- `httpx` - Cliente HTTP para APIs
- `rich` - Interface CLI com formatação

## Uso

### Modo interativo
```bash
python main.py
```

Cole seu deck no formato PTCGO e pressione Enter duas vezes.

### Com arquivo
```bash
python main.py meu_deck.txt
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

Trainer: 31
4 Arven OBF 186
4 Iono PAL 185
4 Rare Candy SVI 191
4 Ultra Ball SVI 196
4 Nest Ball SVI 181

Energy: 10
6 Basic Fire Energy SVE 2
4 Reversal Energy PAL 192
```

## Regulation Marks

| Mark | Status | Sets |
|------|--------|------|
| **D, E** | Já rotacionou | Sword & Shield 2020-2021 |
| **F** | Já rotacionou | Sword & Shield 2022-2023 |
| **G** | Rotaciona Mar/2026 | SVI, PAL, OBF, MEW, PAR, PAF |
| **H** | Seguro | TEF, TWM, SFA, SCR, SSP |
| **I** | Novo | PRE, JTG, ASC |

## Códigos de Sets Suportados

### Scarlet & Violet Era
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

## Critérios de Substituição

As substituições são calculadas com base em três critérios:

| Critério | Peso | Descrição |
|----------|------|-----------|
| **Tipo/Subtipo** | 40% | Pokemon→Pokemon, Supporter→Supporter, etc. |
| **Função** | 40% | Draw, Search, Recovery, Switching, etc. |
| **Arquétipo** | 20% | Compatibilidade de tipo de energia |

### Funções Detectadas

| Categoria | Exemplos |
|-----------|----------|
| Draw | Professor's Research, Iono |
| Search | Ultra Ball, Nest Ball |
| Recovery | Super Rod, Night Stretcher |
| Switching | Switch, Escape Rope |
| Energy Accel | Attachar energia do deck/descarte |
| Damage | Ataques que causam dano |
| Disruption | Iono, Boss's Orders |
| Setup | Rare Candy, evolução |
| Protection | Prevenir dano/efeitos |

## Exemplo de Saída

```
╭───────────────────── Rotation Analysis ─────────────────────╮
│ Impact: 89.8% (CRITICAL)                                    │
│ Rotating (March 2026): 49 cards                             │
│ Already Illegal: 4 cards                                    │
│ Safe: 6 cards                                               │
╰─────────────────────────────────────────────────────────────╯

 Already Illegal (Regulation F or earlier)
╭─────┬───────────────────┬─────────┬─────╮
│ Qty │ Card Name         │ Set     │ Reg │
├─────┼───────────────────┼─────────┼─────┤
│   1 │ Rotom V           │ LOR 177 │ F   │
│   1 │ Manaphy           │ BRS 41  │ F   │
╰─────┴───────────────────┴─────────┴─────╯

 Rotating March 2026 (Regulation G)
╭─────┬─────────────────┬─────────┬─────────────────────╮
│ Qty │ Card Name       │ Set     │ Type                │
├─────┼─────────────────┼─────────┼─────────────────────┤
│   4 │ Charizard ex    │ OBF 125 │ Pokemon             │
│   4 │ Iono            │ PAL 185 │ Trainer (supporter) │
╰─────┴─────────────────┴─────────┴─────────────────────╯
```

## Estrutura do Projeto

```
tcg_tool/
├── main.py              # CLI principal
├── deck_parser.py       # Parser formato PTCGO
├── rotation_checker.py  # Análise de rotação
├── substitution.py      # Lógica de substituição
├── card_api.py          # Integração TCGdex/Pokemon TCG API
├── models.py            # Dataclasses (Card, Deck, Substitution)
├── database.py          # SQLite para cache de cartas
├── requirements.txt     # Dependências Python
└── example_deck.txt     # Deck de exemplo
```

## APIs Utilizadas

- **TCGdex** (principal): https://tcgdex.dev
- **Pokemon TCG API** (fallback): https://pokemontcg.io

## Limitações

- A busca de substituições depende da disponibilidade das cartas na API
- Sets futuros (como ASC) podem não estar disponíveis até o lançamento
- A análise de função é baseada em palavras-chave e pode não ser 100% precisa

## Licença

MIT
