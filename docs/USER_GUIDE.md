# USER_GUIDE.md - Guia do Usuário TCG Tool v3.0

**Autor:** Bruno Strumendo
**Última Atualização:** 15 de fevereiro de 2026

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Dashboard](#dashboard)
3. [Gerenciamento de Decks](#gerenciamento-de-decks)
4. [Meta Game](#meta-game)
5. [Análise de Decks](#análise-de-decks)
6. [Busca de Cartas](#busca-de-cartas)
7. [Coleção](#coleção)
8. [Batalhas](#batalhas)
9. [Chat IA](#chat-ia)
10. [Simulação](#simulação)
11. [Torneios e Notícias](#torneios-e-notícias)

---

## Visão Geral

### O que é o TCG Tool?

O **TCG Tool v3.0** é uma plataforma completa para jogadores de **Pokémon Trading Card Game (TCG)**. Ele oferece:

- **Gerenciamento de Decks**: Crie, importe e organize seus decks
- **Análise Competitiva**: Compare decks com o meta atual
- **Assistente de IA**: Receba sugestões estratégicas personalizadas
- **Análise de Rotação**: Verifique o impacto da rotação de março de 2026
- **Coleção Pessoal**: Gerencie suas cartas e identifique cartas faltantes
- **Batalhas**: Registre partidas e receba análise com IA
- **Simulador**: Teste sequências de jogadas
- **Calendário de Torneios**: Acompanhe eventos oficiais
- **Feed de Notícias**: Fique atualizado com PokeBeach

### Para quem é?

- **Jogadores Competitivos**: Análise de meta, matchups e estatísticas de torneios
- **Iniciantes**: Sugestões de decks e chat IA para aprender estratégias
- **Colecionadores**: Gerenciamento de coleção e tracking de cartas faltantes
- **Criadores de Conteúdo**: Análise de vídeos de batalhas com IA

### Acesso à Plataforma

- **Web App**: http://localhost:3000 (desenvolvimento) ou https://tcgtool.example.com (produção)
- **API Docs**: http://localhost:8000/docs

---

## Dashboard

A página inicial exibe um resumo das suas atividades:

### Seções do Dashboard

#### 1. Resumo Rápido

| Card | Informação |
|------|------------|
| **Meus Decks** | Total de decks salvos |
| **Taxa de Vitórias** | Win rate das últimas 20 batalhas |
| **Próximo Torneio** | Evento mais próximo no calendário |
| **Cartas na Coleção** | Total de cartas únicas |

#### 2. Meta Atual

Exibe os **Top 8 Meta Decks** com:
- Nome do deck
- Tier (S, A, B)
- Taxa de uso (% em torneios)
- Win rate geral

**Exemplo:**
```
┌─────────────────────────────────────────┐
│ 1. Charizard ex / Pidgeot ex    [Tier S]│
│    Uso: 18.5% | Win Rate: 54.2%         │
├─────────────────────────────────────────┤
│ 2. Lugia VSTAR / Archeops       [Tier S]│
│    Uso: 15.3% | Win Rate: 52.8%         │
└─────────────────────────────────────────┘
```

#### 3. Atividades Recentes

- Últimos decks criados/editados
- Batalhas registradas (últimas 5)
- Cartas adicionadas à coleção

#### 4. Sugestões Rápidas

O sistema sugere ações baseadas em:
- Decks com cartas rotacionando em março de 2026
- Cartas faltantes para completar decks meta
- Torneios próximos

---

## Gerenciamento de Decks

Acesse: **Menu > Decks** ou `/decks`

### Criar Deck Manualmente

1. Clique em **"Novo Deck"**
2. Preencha:
   - **Nome do Deck**: Ex: "Charizard ex / Pidgeot ex"
   - **Formato**: Standard, Expanded, Limitless
   - **Descrição** (opcional)
3. Adicione cartas:
   - Use a **busca rápida** para encontrar cartas
   - Clique em **"+ Adicionar"**
   - Defina a **quantidade** (1-4 para cartas normais, até 60 para energias básicas)
4. Clique em **"Salvar Deck"**

**Atalhos:**
- `Ctrl + S`: Salvar deck
- `Ctrl + F`: Focar na busca de cartas

### Importar Deck

O TCG Tool aceita o formato **PTCGO/TCG Live**:

#### Passo a Passo

1. No TCG Live, selecione seu deck
2. Clique em **"Exportar"** e copie o texto
3. No TCG Tool, clique em **"Importar Deck"**
4. Cole o texto no campo
5. Clique em **"Importar"**

**Exemplo de formato aceito:**
```
Pokémon: 14
2 Charmander OBF 26
2 Charmeleon OBF 27
3 Charizard ex OBF 125
2 Pidgey OBF 162
2 Pidgeot ex OBF 164

Trainer: 32
4 Professor's Research SVI 189
4 Boss's Orders PAL 172
3 Ultra Ball SVI 196
2 Nest Ball SVI 181
2 Rare Candy SVI 191
...

Energy: 14
10 Fire Energy SVE 2
4 Double Turbo Energy BRS 151
```

#### Detecção Automática

O sistema detecta automaticamente:
- **Tipo de carta** (Pokémon, Trainer, Energy)
- **Subtipo de Trainer** (Supporter, Item, Stadium, Tool)
- **Regulação** (Marca G, H, I)
- **Imagens** das cartas em português e inglês

### Visualizar Deck

Ao abrir um deck, você vê:

#### 1. Informações Gerais
- Nome do deck
- Formato
- Total de cartas (deve ser 60)
- Data de criação/edição

#### 2. Lista de Cartas com Imagens

As cartas são exibidas em **grid visual** com:
- Imagem da carta
- Nome em português
- Quantidade (x2, x3, etc.)
- Código do set (OBF 125)

**Filtros:**
- Por tipo: Pokémon / Trainer / Energy
- Por subtipo: Supporter / Item / Stadium
- Por regulação: G / H / I

#### 3. Estatísticas do Deck

```
┌─────────────────────────────────┐
│ Composição:                     │
│ • Pokémon: 14 cartas (23%)      │
│ • Trainer: 32 cartas (53%)      │
│ • Energy: 14 cartas (23%)       │
├─────────────────────────────────┤
│ Impacto da Rotação:             │
│ • Rotacionando: 18 cartas (30%) │
│ • Severidade: MODERADA          │
└─────────────────────────────────┘
```

### Exportar Deck

1. Abra o deck
2. Clique em **"Exportar"**
3. Escolha o formato:
   - **PTCGO/TCG Live** (texto)
   - **JSON** (backup completo)
   - **Imagem** (visual para compartilhar)

### Verificar Cartas Faltantes

1. Abra o deck
2. Clique em **"Cartas Faltantes"**
3. O sistema compara com sua **Coleção**
4. Exibe lista de cartas que você não possui

**Exemplo:**
```
Cartas Faltantes (8):
✗ Charizard ex OBF 125 (3x)
✗ Pidgeot ex OBF 164 (2x)
✗ Boss's Orders PAL 172 (4x)
...
```

### Editar Deck

1. Abra o deck
2. Clique em **"Editar"**
3. Adicione/remova cartas
4. Altere quantidades
5. Clique em **"Salvar"**

### Excluir Deck

1. Abra o deck
2. Clique em **"⋮"** (menu) > **"Excluir"**
3. Confirme a ação

---

## Meta Game

Acesse: **Menu > Meta** ou `/meta`

### Lista de Tiers

Visualize os decks competitivos organizados por tier:

#### Tier S (Top Tier)
Decks com maior taxa de uso e win rate em torneios.

**Exemplo:**
```
┌──────────────────────────────────────────┐
│ Charizard ex / Pidgeot ex                │
│ Uso: 18.5% | Win Rate: 54.2%             │
│ Favorável contra: Lugia, Mew VMAX        │
│ Desfavorável contra: Miraidon ex         │
└──────────────────────────────────────────┘
```

#### Tier A
Decks competitivos com matchups específicos favoráveis.

#### Tier B
Decks viáveis mas com menos presença no meta.

### Matriz de Matchups

Visualize todos os matchups entre decks meta:

**Exemplo de Matriz:**
```
                Charizard  Lugia  Miraidon  Mew VMAX
Charizard ex       50%     55%     45%       52%
Lugia VSTAR        45%     50%     48%       60%
Miraidon ex        55%     52%     50%       58%
Mew VMAX           48%     40%     42%       50%
```

**Legenda:**
- 🟢 **55%+**: Matchup favorável
- 🟡 **46-54%**: Matchup equilibrado
- 🔴 **45% ou menos**: Matchup desfavorável

### Detalhes do Meta Deck

Ao clicar em um deck meta, você vê:

#### 1. Decklist Completa (60 cartas)

Lista detalhada com imagens de todas as cartas.

#### 2. Estatísticas de Torneios

- **Top 8s**: Número de top 8 nos últimos 3 meses
- **Taxa de Conversão**: % de top 8 que venceram o torneio
- **Jogadores Conhecidos**: Nomes de jogadores que usam o deck

#### 3. Matchups Detalhados

Para cada matchup, veja:
- Win rate
- Estratégia recomendada
- Cartas tech sugeridas

**Exemplo:**
```
vs. Miraidon ex (45% - Desfavorável)
─────────────────────────────────────
Estratégia:
• Priorize Pidgeot ex para buscar Boss's Orders
• Guarde Rare Candy para evolução rápida
• Use Radiant Charizard como atacante alternativo

Tech Cards:
• Hisuian Heavy Ball (buscar Pidgeot ex)
• Counter Catcher (quando está perdendo)
```

#### 4. Variações do Deck

Lista de variações populares (ex: build com Dusknoir, build com Arcanine ex).

---

## Análise de Decks

Acesse: **Abrir um Deck > "Analisar"** ou `/decks/[id]/analysis`

### Análise de Rotação (Marco 2026)

Verifique o impacto da **rotação de março de 2026** (cartas com regulação G saem do formato):

#### Relatório de Rotação

```
┌─────────────────────────────────────────┐
│ ANÁLISE DE ROTAÇÃO - MARÇO 2026         │
├─────────────────────────────────────────┤
│ Impacto: MODERADO (30% do deck)         │
│                                          │
│ Cartas Rotacionando (18):                │
│ ✗ Charizard ex OBF 125 (3x)             │
│ ✗ Pidgeot ex OBF 164 (2x)               │
│ ✗ Professor's Research SVI 189 (4x)     │
│ ✗ Boss's Orders PAL 172 (4x)            │
│ ✗ Ultra Ball SVI 196 (3x)               │
│ ✗ Rare Candy SVI 191 (2x)               │
│                                          │
│ Cartas Legais (42):                      │
│ ✓ Arcanine ex TEF 123 (2x)              │
│ ✓ Canceling Cologne ASC 136 (2x)        │
│ ✓ Earthen Vessel SFA 96 (2x)            │
│ ...                                      │
└─────────────────────────────────────────┘
```

#### Substituições Sugeridas

O sistema sugere automaticamente substituições:

**Exemplo:**
```
Charizard ex OBF 125 → Charizard ex TEF 125
  • Mesma mecânica, nova expansão legal
  • Win rate similar em torneios

Professor's Research SVI 189 → Professor's Research TEF 190
  • Reprint do mesmo card em set legal

Ultra Ball SVI 196 → Nest Ball TEF 181
  • Função similar (buscar Pokémon Básico)
  • Não descarta cartas
```

### Comparação de Decks

Compare seu deck com:
1. **Deck Meta** (ex: Charizard ex padrão)
2. **Outro Deck Seu**
3. **Deck Importado**

#### Relatório de Comparação

```
┌─────────────────────────────────────────┐
│ SEU DECK vs. CHARIZARD EX META          │
├─────────────────────────────────────────┤
│ Similaridade: 78%                        │
│                                          │
│ Cartas em Comum (47):                    │
│ ✓ Charizard ex OBF 125 (3x)             │
│ ✓ Pidgeot ex OBF 164 (2x)               │
│ ...                                      │
│                                          │
│ Diferenças:                              │
│ Você tem:                                │
│ • Arcanine ex TEF 123 (2x)              │
│ • Counter Catcher PAR 160 (2x)          │
│                                          │
│ Deck Meta tem:                           │
│ • Radiant Charizard CRZ 20 (1x)         │
│ • Super Rod PAL 188 (1x)                │
└─────────────────────────────────────────┘
```

#### Matchup Estimado

O sistema estima o matchup baseado em:
- Composição de cartas
- Dados de torneios
- Win rates históricos

**Exemplo:**
```
Matchup Estimado:
🟢 Favorável contra Lugia VSTAR (58%)
🟡 Equilibrado contra Miraidon ex (51%)
🔴 Desfavorável contra Mew VMAX (44%)
```

### Sugestões de Substituição

O sistema analisa seu deck e sugere melhorias:

#### Por Categoria

**1. Consistência:**
```
+ Adicionar Nest Ball TEF 181 (2x)
  • Melhora setup inicial
  • Usado em 95% dos decks Charizard
```

**2. Tech Cards:**
```
+ Adicionar Counter Catcher PAR 160 (1x)
  • Útil quando está perdendo
  • Tech popular contra Lugia
```

**3. Remoções Sugeridas:**
```
- Remover Potion SVI 194 (2x)
  • Baixo impacto competitivo
  • Usado em apenas 5% dos decks meta
```

---

## Busca de Cartas

Acesse: **Menu > Cartas** ou `/cards`

### Pesquisar Cartas

Use a barra de busca com filtros avançados:

#### Filtros Disponíveis

| Filtro | Opções |
|--------|--------|
| **Nome** | Texto livre |
| **Tipo** | Pokémon, Trainer, Energy |
| **Subtipo** | Supporter, Item, Stadium, Tool, Basic, Special |
| **Regulação** | F, G, H, I |
| **Set** | SVI, PAL, OBF, MEW, PAR, TEF, TWM, etc. |
| **Raridade** | Common, Uncommon, Rare, Ultra Rare |
| **HP** | 30-340 HP (Pokémon) |
| **Tipo de Pokémon** | Fire, Water, Grass, Lightning, etc. |

**Exemplo de Busca:**
```
Nome: "Boss's Orders"
Tipo: Trainer
Subtipo: Supporter
Regulação: G, H, I
```

**Resultado:**
```
┌─────────────────────────────────────────┐
│ Boss's Orders (Ghetsis)                  │
│ PAL 172 | Supporter | Regulação G       │
│ [Imagem da carta]                        │
│                                          │
│ Efeito:                                  │
│ "Escolha 1 dos Pokémon de seu oponente  │
│  no Banco e troque-o com o Pokémon      │
│  Ativo."                                 │
│                                          │
│ Estatísticas:                            │
│ • Usado em 85% dos decks competitivos   │
│ • Win rate: 52.3% (quando jogado)       │
└─────────────────────────────────────────┘
```

### Ver Detalhes da Carta

Ao clicar em uma carta, veja:

#### 1. Informações Completas
- Nome em PT e EN
- Imagem frente/verso
- HP, tipo, fraqueza, resistência, custo de recuo (Pokémon)
- Efeito completo (texto em português)
- Artista, número do set

#### 2. Legalidade
- Formato Standard: ✓ Legal / ✗ Rotacionado
- Formato Expanded: ✓ Legal
- Formato Limitless: ✓ Legal

#### 3. Alternativas

Cartas similares ou versões alternativas:

**Exemplo para Boss's Orders:**
```
Versões Alternativas:
• Boss's Orders (Lysandre) PAF 172 (Regulação G)
• Boss's Orders (Ghetsis) TEF 190 (Regulação H)
• Boss's Orders (Cyrus) TWM 172 (Regulação H)
```

#### 4. Estatísticas de Uso

```
Uso em Torneios (últimos 3 meses):
• Top 8: 92% dos decks
• Média de cópias: 3.2x por deck
• Decks principais:
  1. Charizard ex (4x) - 95% dos decks
  2. Lugia VSTAR (4x) - 98% dos decks
  3. Miraidon ex (4x) - 100% dos decks
```

---

## Coleção

Acesse: **Menu > Coleção** ou `/collection`

### Adicionar Cartas à Coleção

#### Método 1: Busca Manual

1. Use a **busca de cartas**
2. Clique em **"+ Adicionar à Coleção"**
3. Defina a **quantidade** que você possui
4. Clique em **"Salvar"**

#### Método 2: Importação em Massa

1. Clique em **"Importar Coleção"**
2. Cole uma lista de cartas (formato PTCGO)
3. O sistema adiciona todas as cartas

#### Método 3: Scan de Cartas (Mobile)

1. Abra o app Android
2. Clique em **"Scan"**
3. Tire uma foto da carta
4. Confirme a detecção
5. Defina a quantidade

### Visualizar Coleção

#### Grid Visual

Veja todas as suas cartas em grid com imagens:

**Filtros:**
- Por set (SVI, PAL, OBF, etc.)
- Por tipo (Pokémon, Trainer, Energy)
- Por raridade
- Apenas faltantes (cartas que você não tem)

#### Estatísticas

```
┌─────────────────────────────────────────┐
│ RESUMO DA COLEÇÃO                        │
├─────────────────────────────────────────┤
│ Total de Cartas: 1,248                   │
│ Cartas Únicas: 342                       │
│                                          │
│ Por Tipo:                                │
│ • Pokémon: 189 (55%)                     │
│ • Trainer: 128 (37%)                     │
│ • Energy: 25 (7%)                        │
│                                          │
│ Por Raridade:                            │
│ • Ultra Rare: 23                         │
│ • Rare: 67                               │
│ • Uncommon: 142                          │
│ • Common: 110                            │
└─────────────────────────────────────────┘
```

### Ver Cartas Faltantes por Deck

1. Selecione um **Meta Deck** ou **Seu Deck**
2. O sistema compara com sua coleção
3. Exibe lista de cartas que você ainda precisa

**Exemplo:**
```
Cartas Faltantes para Charizard ex:
✗ Charizard ex OBF 125 (precisa: 3, tem: 1)
✗ Pidgeot ex OBF 164 (precisa: 2, tem: 0)
✗ Rare Candy SVI 191 (precisa: 2, tem: 1)

Total Faltante: 7 cartas
Progresso: 88% completo
```

### Marcar Cartas como "Para Trocar"

1. Abra uma carta na coleção
2. Clique em **"Marcar para Trocar"**
3. A carta aparece em **"Minhas Cartas para Troca"**

---

## Batalhas

Acesse: **Menu > Batalhas** ou `/battles`

### Registrar Batalha

#### Passo a Passo

1. Clique em **"Nova Batalha"**
2. Preencha:
   - **Seu Deck**: Selecione da lista
   - **Deck Oponente**: Selecione meta deck ou crie custom
   - **Resultado**: Vitória / Derrota
   - **Formato**: Standard, Expanded, Limitless
   - **Torneio** (opcional): Nome do evento
   - **Data/Hora**: Automático ou manual
3. Adicione **notas** (opcional):
   - Jogadas chave
   - Misplays
   - Sorte/azar
4. **Upload de Vídeo** (opcional):
   - Arquivo local (MP4, MOV)
   - Link do YouTube/Twitch
5. Clique em **"Salvar Batalha"**

### Análise com IA

Se você fez upload de vídeo, clique em **"Analisar com IA"**:

#### Processo de Análise

1. **Extração de Frames**: IA analisa frames-chave do vídeo
2. **Detecção de Cartas**: Reconhece cartas jogadas
3. **Sequência de Jogadas**: Recria o log da partida
4. **Análise Estratégica**: Identifica jogadas ótimas e erros

**Resultado:**
```
┌─────────────────────────────────────────┐
│ ANÁLISE IA - BATALHA #42                 │
├─────────────────────────────────────────┤
│ Duração: 18min 34s                       │
│ Turno Vencedor: Turno 9                  │
│                                          │
│ Jogadas Chave:                           │
│ ✓ T2: Boss's Orders no Pidgey (ótimo)   │
│ ✓ T5: Rare Candy + Charizard ex (ótimo) │
│ ✗ T7: Atacou com Charizard em vez de    │
│       usar Boss's Orders (erro)          │
│                                          │
│ Sugestões:                               │
│ • No T7, Boss's Orders no Radiant       │
│   Greninja teria garantido KO            │
│ • Considere jogar Ultra Ball mais cedo  │
│   para buscar Pidgeot ex                 │
└─────────────────────────────────────────┘
```

### Estatísticas

Visualize suas estatísticas gerais:

#### Resumo Global

```
┌─────────────────────────────────────────┐
│ ESTATÍSTICAS GERAIS                      │
├─────────────────────────────────────────┤
│ Total de Batalhas: 87                    │
│ Vitórias: 54 (62.1%)                     │
│ Derrotas: 33 (37.9%)                     │
│                                          │
│ Win Rate por Deck:                       │
│ • Charizard ex: 68% (34V / 16D)          │
│ • Lugia VSTAR: 58% (11V / 8D)            │
│ • Miraidon ex: 53% (9V / 8D)             │
└─────────────────────────────────────────┘
```

#### Matchups Específicos

```
Seu Charizard ex vs. Decks Meta:
🟢 vs. Lugia VSTAR: 75% (9V / 3D)
🟢 vs. Mew VMAX: 66% (8V / 4D)
🟡 vs. Gardevoir ex: 50% (5V / 5D)
🔴 vs. Miraidon ex: 40% (6V / 9D)
```

#### Gráficos

- Win rate ao longo do tempo (linha)
- Distribuição de decks usados (pizza)
- Matchups mais jogados (barra)

---

## Chat IA

Acesse: **Menu > Chat IA** ou `/chat`

### Fazer Perguntas sobre Estratégia

O assistente de IA responde perguntas sobre:
- Estratégias de deck
- Matchups específicos
- Tech cards
- Decisões de jogo

#### Exemplos de Perguntas

**Pergunta 1:**
```
User: Qual a melhor estratégia contra Miraidon ex
      usando Charizard ex?

IA: Contra Miraidon ex, a chave é:

1. Setup Rápido:
   • Priorize evoluir Pidgeot ex no T2
   • Use Rare Candy para acelerar Charizard ex

2. Gerenciamento de Prize:
   • Evite deixar Pokémon ex vulneráveis no Banco
   • Use Radiant Charizard como atacante alternativo
     (1 prize ao invés de 2)

3. Boss's Orders:
   • Alvo prioritário: Miraidon ex com energia (2 KO)
   • Segundo alvo: Iron Hands ex (setup)

4. Tech Cards Recomendadas:
   • Counter Catcher (quando está perdendo)
   • Earthen Vessel (acelerar energia)

Win rate esperado: 45-48% (matchup desfavorável)
```

**Pergunta 2:**
```
User: Vale a pena jogar Dusknoir no meu deck
      Charizard ex?

IA: Dusknoir (ASC 111) é uma tech interessante:

Vantagens:
✓ Habilidade "Cursed Blast" causa 40 de dano
  ao entrar em jogo
✓ Útil para atingir números de KO específicos
✓ Counter para decks de spread damage

Desvantagens:
✗ Ocupa 3 slots (Duskull + Dusclops + Dusknoir)
✗ Reduz consistência do deck
✗ Lento (evolução Stage 2)

Recomendação:
Apenas se você enfrenta muito Snorlax/Mew VMAX
(que dependem de HP exatos). Na maioria dos casos,
prefira adicionar mais draw/search.

Uso em torneios: 12% dos Charizard ex top 8
```

### Selecionar Contexto de Deck

Para respostas personalizadas:

1. Clique em **"Selecionar Deck"**
2. Escolha um dos seus decks
3. A IA passa a considerar sua decklist específica

**Exemplo com Contexto:**
```
User: [Com deck Charizard ex selecionado]
      Quais cartas eu deveria substituir após a rotação?

IA: Analisando seu Charizard ex:

Cartas Rotacionando:
1. Professor's Research SVI 189 (4x)
   → Substituir por: Professor's Research TEF 190

2. Boss's Orders PAL 172 (4x)
   → Substituir por: Boss's Orders TEF 190

3. Ultra Ball SVI 196 (3x)
   → Substituir por: Nest Ball TEF 181 (2x)
                   + Arven TEF 186 (1x)

Seu deck ficará 95% legal após essas mudanças.
```

### Sugestões Rápidas

Botões de perguntas comuns:

- 📊 "Qual o melhor deck para iniciantes?"
- 🔄 "Como substituir cartas rotacionando?"
- ⚔️ "Qual deck contra o meta atual?"
- 💡 "Tech cards para meu deck?"
- 📈 "Como melhorar consistência?"

---

## Simulação

Acesse: **Menu > Simulação** ou `/simulation`

### Simular Sequência de Jogadas

Teste jogadas antes de executá-las em partida real.

#### Passo a Passo

1. Selecione **Seu Deck**
2. Selecione **Deck Oponente**
3. Configure **Estado Inicial**:
   - Cartas na mão
   - Pokémon Ativo/Banco (seu e oponente)
   - Energias anexadas
   - Prize cards restantes
4. Clique em **"Iniciar Simulação"**

#### Interface de Simulação

```
┌─────────────────────────────────────────┐
│ SIMULADOR - TURNO 5 (Você)               │
├─────────────────────────────────────────┤
│ Mão (6 cartas):                          │
│ • Boss's Orders                          │
│ • Ultra Ball                             │
│ • Rare Candy                             │
│ • Charmeleon                             │
│ • Fire Energy                            │
│ • Professor's Research                   │
│                                          │
│ Ativo: Charmander (60 HP)                │
│ Banco: Pidgey, Pidgey                    │
│                                          │
│ Ações Disponíveis:                       │
│ [1] Jogar Professor's Research           │
│ [2] Jogar Ultra Ball (buscar carta)      │
│ [3] Evoluir Charmander → Charmeleon      │
│ [4] Anexar Fire Energy                   │
│ [5] Atacar com Charmander                │
│ [6] Recuar para Banco                    │
└─────────────────────────────────────────┘
```

#### Análise de IA

Após cada jogada, a IA sugere:
- **Jogada Ótima**: Melhor ação estatisticamente
- **Alternativas**: Outras opções viáveis
- **Probabilidades**: Chance de sucesso

**Exemplo:**
```
Análise IA:
✓ Jogada Ótima: [1] Professor's Research
  • Refresca a mão (6 → 7 cartas)
  • Aumenta chance de achar Pidgeot ex (78%)

Alternativas:
• [2] Ultra Ball → buscar Pidgey
  • Garantido, mas descarta 2 cartas
  • Recomendado se mão ruim

Evite:
✗ [5] Atacar com Charmander
  • Dano insuficiente (30 HP)
  • Desperdiça turno
```

---

## Torneios e Notícias

Acesse: **Menu > Torneios** ou `/tournaments`

### Calendário de Torneios

Visualize eventos oficiais e locais:

#### Filtros

- **Formato**: Standard, Expanded, Limitless
- **Nível**: Regional, International, World Championships, Local
- **Localização**: Por país/cidade
- **Data**: Próximos 7/30/90 dias

#### Exemplo de Lista

```
┌─────────────────────────────────────────┐
│ PRÓXIMOS TORNEIOS                        │
├─────────────────────────────────────────┤
│ 📅 22/02/2026 | Regional São Paulo       │
│    Format: Standard | Players: ~250     │
│    Local: Expo Center Norte              │
│    [Ver Detalhes] [Adicionar ao Calendário]│
├─────────────────────────────────────────┤
│ 📅 08/03/2026 | International LATAM      │
│    Format: Standard | Players: ~800     │
│    Local: Mexico City Convention Center  │
│    [Ver Detalhes] [Adicionar ao Calendário]│
└─────────────────────────────────────────┘
```

#### Integração com Calendário

1. Clique em **"Adicionar ao Calendário"**
2. O evento é adicionado ao **Google Calendar** ou **iCal** (Android)
3. Receba notificações antes do torneio

### Feed de Notícias (PokeBeach)

Fique atualizado com as últimas notícias:

#### Categorias

- **Revelações**: Novas cartas anunciadas
- **Metagame**: Análises de decks e torneios
- **Produtos**: Novos sets, produtos especiais
- **Competitivo**: Resultados de torneios, tier lists

#### Exemplo de Notícia

```
┌─────────────────────────────────────────┐
│ 🆕 Revelado: Mewtwo ex de Journey to Go │
│ há 2 horas | PokeBeach                   │
├─────────────────────────────────────────┤
│ [Imagem da Carta]                        │
│                                          │
│ Mewtwo ex - 220 HP                       │
│ Psychic Energy x2 | Psycho Sphere: 120  │
│                                          │
│ Análise:                                 │
│ "Mewtwo ex pode revitalizar decks       │
│  Psychic no formato pós-rotação..."     │
│                                          │
│ [Ler Mais] [Compartilhar]                │
└─────────────────────────────────────────┘
```

#### Notificações

Configure alertas para:
- Novas revelações de cartas
- Resultados de torneios específicos
- Análises de meta

---

## Dúvidas Frequentes

### 1. Como atualizo meu deck após a rotação?

Use **Análise de Decks > Rotação** para ver cartas rotacionando e sugestões automáticas de substituição.

### 2. Posso importar decks do TCG Live?

Sim! Use **Decks > Importar** e cole o texto exportado do TCG Live (formato PTCGO).

### 3. A análise de vídeo funciona em português?

Sim, a IA reconhece cartas em português e inglês automaticamente.

### 4. Minha coleção é sincronizada no mobile?

Sim, se você fizer login com a mesma conta, a coleção é sincronizada entre web e mobile.

### 5. Como faço para comparar meu deck com o meta?

Abra seu deck e clique em **"Analisar" > "Comparar com Meta"**. Selecione um meta deck e veja as diferenças.

---

## Suporte

Para dúvidas ou problemas:

- **Email**: strumendo@gmail.com
- **GitHub Issues**: https://github.com/strumendo/tcg-tool/issues
- **Discord**: [Em breve]

---

**Versão do Guia:** 3.0.0
**Última Atualização:** 15 de fevereiro de 2026
**Autor:** Bruno Strumendo
