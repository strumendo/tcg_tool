# Claude Code Configuration - TCG Tool

Este arquivo contém as configurações e diretrizes para o Claude Code ao trabalhar neste projeto.

---

## Configuração de Commit

**IMPORTANTE**: Todos os commits devem ser feitos com as seguintes credenciais:

```
Nome: Bruno Strumendo
Email: strumendo@gmail.com
```

Para configurar antes de commits:
```bash
git config user.name "Bruno Strumendo"
git config user.email "strumendo@gmail.com"
```

---

## Linting e Qualidade de Código

### Pylint
O projeto usa pylint para análise estática. Configuração em `.pylintrc`.

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar pylint
pylint *.py

# Verificar arquivo específico
pylint main.py
```

### Regras Desabilitadas (ver .pylintrc)
- `C0114`: missing-module-docstring (opcional para scripts)
- `C0116`: missing-function-docstring (opcional para funções internas)
- `R0903`: too-few-public-methods (dataclasses são ok)
- `R0913`: too-many-arguments (algumas funções precisam)
- `C0301`: line-too-long (120 chars permitido)

### Antes de Commit
```bash
# Verificar sintaxe
python -m py_compile *.py

# Executar pylint (opcional mas recomendado)
pylint *.py --exit-zero
```

---

## Estrutura do Projeto

```
tcg_tool/
├── main.py                 # CLI principal com menu interativo
├── meta_database.py        # Base de dados do meta (9 decks)
├── abilities_database.py   # Banco de habilidades de Pokemon (NOVO)
├── deck_builder.py         # Construtor de deck com matchups (NOVO)
├── deck_suggest.py         # Sugestão de deck por Pokemon
├── deck_parser.py          # Parser formato PTCGO
├── rotation_checker.py     # Análise de rotação
├── deck_compare.py         # Comparação de decks e matchups
├── substitution.py         # Lógica de substituição
├── card_api.py             # Integração TCGdex/Pokemon TCG API
├── models.py               # Dataclasses (Card, Deck, Substitution)
├── database.py             # SQLite para cache de cartas
├── requirements.txt        # Dependências Python
├── README.md               # Documentação principal
├── claude.md               # Este arquivo - configurações Claude
└── android_app/            # Aplicativo Android
    ├── main.py
    ├── meta_data.py
    └── buildozer.spec
```

---

## Padrões de Código

### Python
- Usar type hints em todas as funções
- Docstrings em formato Google
- Dataclasses para estruturas de dados
- Suporte bilíngue (EN/PT) em todas as strings de UI
- Rich library para interface CLI

### Nomenclatura
- Classes: PascalCase (ex: `DeckBuilderState`)
- Funções: snake_case (ex: `analyze_matchups`)
- Constantes: UPPER_SNAKE_CASE (ex: `META_DECKS`)
- Arquivos: snake_case (ex: `deck_builder.py`)

### Idiomas
- Código e comentários: Inglês
- Strings de UI: Bilíngue (EN/PT)
- Documentação: Português (README) ou Inglês (código)

---

## Módulos Principais

### abilities_database.py
Banco de dados de habilidades de Pokemon organizadas por categoria:
- `AbilityCategory`: Enum com 20+ categorias (SAFEGUARD, BENCH_BARRIER, ENERGY_ACCEL, etc)
- `PokemonCard`: Dataclass com Pokemon e suas habilidades
- `POKEMON_DATABASE`: Dict com todos os Pokemon cadastrados
- Funções de busca: `search_pokemon()`, `get_pokemon_by_ability()`

### deck_builder.py
Construtor de deck interativo com análise de matchups:
- `DeckBuilderState`: Estado atual do deck em construção
- `MatchupResult`: Resultado de análise de matchup
- `GameplayGuide`: Guia de jogo contra deck específico
- Funções: `analyze_all_matchups()`, `generate_all_guides()`

### meta_database.py
Base de dados do meta competitivo:
- 9 decks completos (60 cartas cada)
- Matchups com win rates
- Suporte bilíngue completo
- Funções: `get_matchup()`, `calculate_meta_score()`

---

## Fluxo de Desenvolvimento

1. **Antes de alterações**: Verificar git config
2. **Durante desenvolvimento**: Manter suporte bilíngue
3. **Após alterações**:
   - Atualizar README.md se houver nova funcionalidade
   - Atualizar este arquivo se houver nova configuração
   - Verificar syntax com `python -m py_compile`
4. **Commit**: Usar credenciais Bruno Strumendo

---

## APIs Externas

| API | Uso | Rate Limit |
|-----|-----|------------|
| TCGdex | Principal | Sem limite |
| Pokemon TCG API | Fallback | 1000/dia |

---

## Sets Relevantes (2025-2026)

| Código | Set | Regulation |
|--------|-----|------------|
| PRE | Prismatic Evolutions | I |
| JTG | Journey Together | I |
| ASC | Ascended Heroes | I |
| DRI | Destined Rivals | I |
| MEV | Mega Evolution | I |

---

## Checklist de Alterações

- [ ] Código compilável (`python -m py_compile`)
- [ ] Suporte bilíngue mantido
- [ ] Documentação atualizada (README.md)
- [ ] Git config correto (Bruno Strumendo)
- [ ] Commit message descritivo
