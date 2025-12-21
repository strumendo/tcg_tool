# TCG Rotation Checker

Ferramenta CLI para analisar decks de Pokemon TCG e verificar o impacto da rotação de março de 2026.

## O que faz

1. **Analisa seu deck** - Cole seu deck no formato PTCGO
2. **Verifica rotação** - Identifica cartas com regulation mark "G" que rotacionam
3. **Busca substituições** - Procura cartas equivalentes na coleção Ascended Heroes (ASC)
4. **Sugere deck atualizado** - Gera deck pós-rotação com substituições

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

### Modo interativo
```bash
python main.py
```

Cole seu deck no formato PTCGO e pressione Enter duas vezes.

### Arquivo
```bash
python main.py meu_deck.txt
```

## Formato de Deck (PTCGO)

```
4 Charizard ex OBF 125
4 Charmander OBF 26
3 Charmeleon OBF 27
4 Arven OBF 186
4 Rare Candy SVI 191
...
```

## Regulation Marks

- **G** - Rotaciona em março 2026 (SVI, PAL, OBF, MEW, PAR, PAF)
- **H** - Seguro (TEF, TWM, SFA, SCR, SSP)
- **I** - Novo (PRE, JTG, ASC)

## Critérios de Substituição

As substituições são calculadas com base em:

| Critério | Peso |
|----------|------|
| Tipo/Subtipo | 40% |
| Função | 40% |
| Arquétipo | 20% |

### Funções detectadas
- Draw, Search, Recovery
- Switching, Energy Acceleration
- Damage, Healing, Disruption
- Setup, Protection
