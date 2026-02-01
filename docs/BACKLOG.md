# Product Backlog - TCG Tool

## Estrutura de Priorização

**Prioridade:**
- P0: Crítico (MVP)
- P1: Alta (Primeira Release)
- P2: Média (Segunda Release)
- P3: Baixa (Futuro)

**Estimativa (Story Points):**
- 1: Trivial (< 2 horas)
- 2: Pequeno (2-4 horas)
- 3: Médio (4-8 horas)
- 5: Grande (1-2 dias)
- 8: Muito Grande (2-3 dias)
- 13: Épico (> 3 dias, deve ser quebrado)

---

# ÉPICO 1: IMPORTAÇÃO DE DECKS

**Descrição:** Permitir aos usuários importar decks do Pokemon TCG Live via texto ou arquivo, validar e salvar em sua coleção pessoal.

**Valor de Negócio:** Entrada principal de dados do usuário no sistema. Sem importação, não há decks para gerenciar.

**Prioridade:** P0 (MVP)

---

## User Story 1.1: Importar Deck via Texto (Copiar/Colar)

**Como** jogador de Pokemon TCG,
**Quero** importar um deck copiando o texto do TCG Live,
**Para que** eu possa analisar e gerenciar meu deck no aplicativo.

**Critérios de Aceitação:**
- [ ] Campo de texto aceita formato PTCGO (ex: "4 Charizard ex OBF 125")
- [ ] Sistema parseia corretamente quantidade, nome, set e número
- [ ] Linhas de comentário (#, //) são ignoradas
- [ ] Headers de seção (Pokemon:, Trainer:, Energy:) são ignorados
- [ ] Exibe feedback visual de sucesso/erro

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 1.1.1 | Criar tela de importação | Tela com campo de texto multilinha e botão "Importar" | 2 |
| 1.1.2 | Implementar parser PTCGO | Usar regex para parsear formato "QTD NOME SET NUM" | 3 |
| 1.1.3 | Validar linhas parseadas | Verificar se quantidade é número, set é válido | 2 |
| 1.1.4 | Feedback visual | Exibir toast/snackbar de sucesso ou erros encontrados | 1 |
| 1.1.5 | Testes unitários | Testes para parser com casos válidos e inválidos | 2 |

---

## User Story 1.2: Importar Deck via Arquivo .txt

**Como** jogador de Pokemon TCG,
**Quero** importar decks a partir de um arquivo .txt,
**Para que** eu possa importar múltiplos decks de uma vez ou backups salvos.

**Critérios de Aceitação:**
- [ ] Botão "Selecionar Arquivo" abre seletor de arquivos do sistema
- [ ] Aceita apenas arquivos .txt
- [ ] Suporta múltiplos decks no mesmo arquivo (separados por linha em branco)
- [ ] Exibe relatório: X decks encontrados, Y válidos, Z inválidos
- [ ] Lista decks válidos para revisão antes de salvar

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 1.2.1 | Integrar file picker | Usar Kivy FileChooser para seleção de arquivo | 2 |
| 1.2.2 | Parser de arquivo multi-deck | Separar decks por linha em branco ou marcador | 3 |
| 1.2.3 | Tela de relatório de importação | Exibir lista de decks encontrados com status | 2 |
| 1.2.4 | Validação individual | Validar cada deck separadamente | 2 |
| 1.2.5 | Seleção para importar | Checkboxes para selecionar quais decks importar | 2 |

---

## User Story 1.3: Validar Estrutura do Deck

**Como** jogador de Pokemon TCG,
**Quero** que o sistema valide meu deck importado,
**Para que** eu saiba se está legal para jogar.

**Critérios de Aceitação:**
- [ ] Verifica se deck tem exatamente 60 cartas (deck completo)
- [ ] Permite deck incompleto (< 60) com aviso visual
- [ ] Verifica regra de 4 cópias (exceto energia básica)
- [ ] Verifica legalidade das cartas (regulation mark)
- [ ] Exibe relatório detalhado de validação

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 1.3.1 | Validador de quantidade total | Verificar soma de cartas = 60 | 1 |
| 1.3.2 | Validador de cópias | Verificar máximo 4 cópias por nome | 2 |
| 1.3.3 | Validador de rotation | Verificar regulation mark (G = rotando) | 2 |
| 1.3.4 | Componente de relatório | UI para exibir erros e avisos de validação | 2 |
| 1.3.5 | Indicadores visuais | Badges de "Completo", "Incompleto", "Ilegal" | 1 |

---

## User Story 1.4: Visualizar Deck Importado

**Como** jogador de Pokemon TCG,
**Quero** visualizar meu deck importado com imagens das cartas,
**Para que** eu possa conferir visualmente se está correto.

**Critérios de Aceitação:**
- [ ] Exibe grid de cartas com imagens da API
- [ ] Cartas agrupadas: Pokemon > Treinadores > Energias
- [ ] Clique na carta expande para visualização grande
- [ ] Exibe quantidade de cada carta sobre a imagem
- [ ] Loading skeleton enquanto carrega imagens

**Prioridade:** P0 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 1.4.1 | Grid de cartas | Layout responsivo para exibir cards | 3 |
| 1.4.2 | Integração com API de imagens | Buscar imagens via TCGdex/Pokemon TCG API | 3 |
| 1.4.3 | Modal de carta expandida | Popup com imagem grande e detalhes | 2 |
| 1.4.4 | Agrupamento por tipo | Separadores visuais por categoria | 1 |
| 1.4.5 | Contador de quantidade | Badge com número sobre cada carta | 1 |
| 1.4.6 | Loading states | Skeleton/placeholder enquanto carrega | 2 |

---

## User Story 1.5: Exibir Estatísticas de Utilização da Carta

**Como** jogador competitivo,
**Quero** ver estatísticas de uso das cartas do meu deck,
**Para que** eu saiba quão populares elas são no meta atual.

**Critérios de Aceitação:**
- [ ] Ao expandir carta, exibe % de uso em decks meta
- [ ] Exibe decks mais populares que usam a carta
- [ ] Dados obtidos do Limitless TCG
- [ ] Indicador quando não há dados disponíveis

**Prioridade:** P1 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 1.5.1 | Integração Limitless TCG | Endpoint para buscar estatísticas de carta | 3 |
| 1.5.2 | Componente de estatísticas | UI para exibir % uso e decks relacionados | 2 |
| 1.5.3 | Cache de estatísticas | Salvar dados localmente para performance | 2 |
| 1.5.4 | Estado "sem dados" | UI para quando não há estatísticas | 1 |

---

## User Story 1.6: Salvar Deck Importado

**Como** jogador de Pokemon TCG,
**Quero** salvar o deck importado em "Meus Decks",
**Para que** eu possa acessá-lo posteriormente.

**Critérios de Aceitação:**
- [ ] Botão "Salvar" disponível após importação válida
- [ ] Solicita nome para o deck (com sugestão automática)
- [ ] Salva no banco de dados local
- [ ] Remove deck da tela de importação após salvar
- [ ] Confirmação visual de sucesso

**Prioridade:** P0 | **Pontos:** 3

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 1.6.1 | Modal de nome do deck | Input para definir nome com sugestão | 1 |
| 1.6.2 | Persistência SQLite | Salvar deck no banco local | 2 |
| 1.6.3 | Navegação pós-save | Redirecionar para "Meus Decks" ou limpar tela | 1 |
| 1.6.4 | Toast de confirmação | Feedback visual de sucesso | 1 |

---

## User Story 1.7: Descartar Deck Importado

**Como** jogador de Pokemon TCG,
**Quero** poder descartar um deck importado sem salvar,
**Para que** eu possa recomeçar se importei errado.

**Critérios de Aceitação:**
- [ ] Botão "Descartar" visível na tela de importação
- [ ] Exibe confirmação "Tem certeza? Esta ação não pode ser desfeita"
- [ ] Limpa tela de importação após confirmar
- [ ] Não afeta decks já salvos

**Prioridade:** P0 | **Pontos:** 2

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 1.7.1 | Botão descartar | Botão com ícone de lixeira | 1 |
| 1.7.2 | Modal de confirmação | Dialog de confirmação antes de descartar | 1 |
| 1.7.3 | Reset de estado | Limpar dados da tela de importação | 1 |

---

# ÉPICO 2: MEUS DECKS

**Descrição:** Gerenciamento completo da coleção pessoal de decks do usuário, incluindo listagem, seleção, edição e organização.

**Valor de Negócio:** Central de gerenciamento dos decks do usuário, ponto de partida para todas as análises.

**Prioridade:** P0 (MVP)

---

## User Story 2.1: Listar Decks Salvos

**Como** jogador de Pokemon TCG,
**Quero** ver todos os meus decks salvos em uma lista,
**Para que** eu possa escolher qual utilizar.

**Critérios de Aceitação:**
- [ ] Lista todos os decks do banco de dados
- [ ] Exibe thumbnail (carta principal), nome, data
- [ ] Indica status: completo/incompleto
- [ ] Indica deck ativo com destaque visual
- [ ] Permite ordenar por nome, data ou uso

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 2.1.1 | Query de decks | Buscar decks do SQLite | 1 |
| 2.1.2 | Lista de decks | RecyclerView/ScrollView com cards | 3 |
| 2.1.3 | Thumbnail do deck | Exibir imagem da carta principal | 2 |
| 2.1.4 | Indicadores de status | Badges de completo/incompleto/ativo | 1 |
| 2.1.5 | Ordenação | Dropdown para ordenar lista | 2 |

---

## User Story 2.2: Selecionar Deck para Ações

**Como** jogador de Pokemon TCG,
**Quero** selecionar um deck e ver opções disponíveis,
**Para que** eu possa realizar ações como editar ou comparar.

**Critérios de Aceitação:**
- [ ] Ao tocar no deck, abre tela de detalhes
- [ ] Exibe informações do deck (nome, cartas, estatísticas)
- [ ] Botões de ação: Editar, Comparar META, Comparar Variações, Tornar Ativo, Excluir
- [ ] Estatísticas visíveis: Pokemon/Treinadores/Energias, impacto de rotação

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 2.2.1 | Tela de detalhes do deck | Layout com informações e ações | 3 |
| 2.2.2 | Cálculo de estatísticas | Contagem por tipo, impacto de rotação | 2 |
| 2.2.3 | Botões de ação | Grid de botões com navegação | 2 |
| 2.2.4 | Navegação para edição | Abrir tela de edição com deck carregado | 1 |

---

## User Story 2.3: Marcar Deck como Ativo

**Como** jogador de Pokemon TCG,
**Quero** marcar um deck como "ativo",
**Para que** ele seja usado automaticamente em comparações.

**Critérios de Aceitação:**
- [ ] Botão "Tornar Ativo" na tela de detalhes
- [ ] Apenas um deck ativo por vez (desmarca anterior)
- [ ] Indicador visual claro do deck ativo na listagem
- [ ] Deck ativo é pré-selecionado em comparações
- [ ] Informações do deck ativo visíveis em outros menus

**Prioridade:** P0 | **Pontos:** 3

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 2.3.1 | Flag de deck ativo | Campo no banco de dados | 1 |
| 2.3.2 | Lógica de ativação | Desmarcar anterior, marcar novo | 1 |
| 2.3.3 | Indicador na listagem | Ícone ou badge destacando ativo | 1 |
| 2.3.4 | Widget de deck ativo | Componente reutilizável para outros menus | 2 |

---

## User Story 2.4: Excluir Deck

**Como** jogador de Pokemon TCG,
**Quero** excluir um deck da minha coleção,
**Para que** eu possa manter apenas os decks relevantes.

**Critérios de Aceitação:**
- [ ] Botão "Excluir" na tela de detalhes
- [ ] Confirmação antes de excluir: "Tem certeza?"
- [ ] Remove do banco de dados permanentemente
- [ ] Retorna para lista de decks após exclusão
- [ ] Toast de confirmação

**Prioridade:** P0 | **Pontos:** 2

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 2.4.1 | Modal de confirmação | Dialog antes de excluir | 1 |
| 2.4.2 | Delete no SQLite | Remover registro do banco | 1 |
| 2.4.3 | Navegação pós-delete | Voltar para lista | 1 |

---

# ÉPICO 3: CRIAÇÃO E EDIÇÃO DE DECKS

**Descrição:** Ferramentas completas para criar novos decks e editar decks existentes, com pesquisa avançada, filtros e sugestões de IA.

**Valor de Negócio:** Permite aos usuários construir e otimizar seus decks dentro do aplicativo.

**Prioridade:** P0 (MVP)

---

## User Story 3.1: Visualização Completa do Deck em Edição

**Como** jogador de Pokemon TCG,
**Quero** ver todas as cartas do meu deck durante a edição,
**Para que** eu tenha visão geral da composição.

**Critérios de Aceitação:**
- [ ] Exibe todas as cartas (até 60) em grid
- [ ] Organização: Pokemon > Treinadores (Supporter, Item, Tool, Stadium) > Energias
- [ ] Contador visível: X/60 cartas
- [ ] Scroll vertical para ver todas as cartas
- [ ] Cartas clicáveis para expandir detalhes

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.1.1 | Grid de edição | Layout responsivo para cartas | 3 |
| 3.1.2 | Ordenação automática | Agrupar e ordenar por tipo | 2 |
| 3.1.3 | Contador de cartas | Widget com contagem atual/total | 1 |
| 3.1.4 | Separadores de seção | Headers visuais por categoria | 1 |

---

## User Story 3.2: Filtrar Cartas por Tipo

**Como** jogador de Pokemon TCG,
**Quero** filtrar a visualização do deck por tipo de carta,
**Para que** eu possa focar em uma categoria específica.

**Critérios de Aceitação:**
- [ ] Botões de filtro: Todos, Pokemon, Treinadores, Energias
- [ ] Sub-filtros para Treinadores: Supporter, Item, Tool, Stadium
- [ ] Atualiza visualização em tempo real
- [ ] Mantém contador atualizado por filtro

**Prioridade:** P1 | **Pontos:** 3

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.2.1 | Botões de filtro | ToggleButtons para cada tipo | 2 |
| 3.2.2 | Lógica de filtro | Filtrar lista de cartas exibidas | 1 |
| 3.2.3 | Sub-filtros de treinadores | Dropdown ou chips para subtipos | 2 |

---

## User Story 3.3: Pesquisar Cartas (Multilíngue)

**Como** jogador de Pokemon TCG,
**Quero** pesquisar cartas por nome, coleção ou número,
**Para que** eu encontre rapidamente a carta que procuro.

**Critérios de Aceitação:**
- [ ] Campo de pesquisa no topo da tela
- [ ] Busca por nome em português E inglês
- [ ] Busca por código de coleção (OBF, SVI, etc.)
- [ ] Busca por número da carta
- [ ] Busca por tipo de Pokemon ou habilidade
- [ ] Respeita filtros ativos (combina com filtro de tipo)
- [ ] Debounce de 300ms para não sobrecarregar API
- [ ] Resultados em tempo real

**Prioridade:** P0 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.3.1 | Campo de pesquisa | TextInput com ícone de busca | 1 |
| 3.3.2 | Debounce | Timer de 300ms antes de buscar | 1 |
| 3.3.3 | Busca local | Pesquisar no cache local primeiro | 2 |
| 3.3.4 | Busca na API | Chamar TCGdex/Pokemon TCG API | 3 |
| 3.3.5 | Combinação com filtros | Aplicar filtro de tipo nos resultados | 2 |
| 3.3.6 | Exibição de resultados | Grid de cartas encontradas | 2 |

---

## User Story 3.4: Expandir Carta para Detalhes

**Como** jogador de Pokemon TCG,
**Quero** clicar em uma carta para ver detalhes,
**Para que** eu possa ler habilidades e ataques.

**Critérios de Aceitação:**
- [ ] Clique na carta abre modal/fullscreen
- [ ] Imagem em alta resolução
- [ ] Nome, tipo, HP (para Pokemon)
- [ ] Lista de habilidades e ataques
- [ ] Custo de energia dos ataques
- [ ] Fraqueza, resistência, custo de recuo
- [ ] Set, número, regulation mark

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.4.1 | Modal de detalhes | Popup/screen com layout de detalhes | 3 |
| 3.4.2 | Buscar dados completos | API call para dados detalhados da carta | 2 |
| 3.4.3 | Formatação de ataques | Exibir custos de energia com ícones | 2 |

---

## User Story 3.5: Adicionar Carta ao Deck

**Como** jogador de Pokemon TCG,
**Quero** adicionar cartas ao meu deck,
**Para que** eu possa construir minha lista.

**Critérios de Aceitação:**
- [ ] Botão "+" ou "Adicionar" na carta dos resultados de pesquisa
- [ ] Incrementa quantidade se carta já existe no deck
- [ ] Valida máximo de 4 cópias (exceto energia básica)
- [ ] Exibe erro se tentar adicionar além do limite
- [ ] Atualiza contador X/60 em tempo real
- [ ] Bloqueia adição se deck já tem 60 cartas

**Prioridade:** P0 | **Pontos:** 3

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.5.1 | Botão adicionar | Ícone "+" na carta de resultado | 1 |
| 3.5.2 | Validação de cópias | Verificar regra de 4 cópias | 1 |
| 3.5.3 | Validação de total | Verificar se < 60 cartas | 1 |
| 3.5.4 | Atualizar estado | Adicionar carta à lista do deck | 1 |

---

## User Story 3.6: Remover Carta do Deck

**Como** jogador de Pokemon TCG,
**Quero** remover cartas do meu deck,
**Para que** eu possa ajustar a composição.

**Critérios de Aceitação:**
- [ ] Botão "-" ou swipe para remover
- [ ] Decrementa quantidade (1 cópia por vez)
- [ ] Remove carta completamente quando quantidade = 0
- [ ] Confirmação se remover última cópia de carta-chave
- [ ] Atualiza contador X/60 em tempo real

**Prioridade:** P0 | **Pontos:** 2

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.6.1 | Botão remover | Ícone "-" na carta do deck | 1 |
| 3.6.2 | Lógica de remoção | Decrementar ou remover carta | 1 |
| 3.6.3 | Atualizar estado | Atualizar lista do deck | 1 |

---

## User Story 3.7: Insights de IA ao Modificar Deck

**Como** jogador competitivo,
**Quero** receber sugestões ao adicionar/remover cartas,
**Para que** eu tome decisões informadas.

**Critérios de Aceitação:**
- [ ] Ao adicionar carta, exibe sugestões relacionadas
- [ ] Mostra impacto no matchup (melhora/piora contra quais decks)
- [ ] Detecta sinergias com outras cartas do deck
- [ ] Alerta problemas (ex: pouco draw power, muita energia)
- [ ] Sugestões de substituição para cartas rotando

**Prioridade:** P2 | **Pontos:** 13

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.7.1 | Análise de sinergias | Algoritmo para detectar combos | 5 |
| 3.7.2 | Análise de matchup | Impacto da carta em matchups conhecidos | 5 |
| 3.7.3 | Alertas de composição | Verificar proporções ideais | 3 |
| 3.7.4 | UI de sugestões | Painel lateral ou bottom sheet | 3 |
| 3.7.5 | Integração com IA | Chamar modelo para sugestões avançadas | 8 |

---

## User Story 3.8: Salvar Deck (Completo ou Incompleto)

**Como** jogador de Pokemon TCG,
**Quero** salvar meu deck a qualquer momento,
**Para que** eu não perca meu progresso.

**Critérios de Aceitação:**
- [ ] Botão "Salvar" sempre visível
- [ ] Se < 60 cartas, exibe aviso: "Deck incompleto. Deseja salvar mesmo assim?"
- [ ] Marca deck como "incompleto" no banco
- [ ] Se = 60 cartas, salva como "completo"
- [ ] Atualiza timestamp de modificação
- [ ] Toast de confirmação

**Prioridade:** P0 | **Pontos:** 3

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.8.1 | Verificação de completude | Checar se deck tem 60 cartas | 1 |
| 3.8.2 | Modal de aviso | Dialog para deck incompleto | 1 |
| 3.8.3 | Persistir no SQLite | Insert/Update no banco | 1 |
| 3.8.4 | Atualizar metadata | Timestamp, status completo/incompleto | 1 |

---

## User Story 3.9: Base de Dados de Habilidades

**Como** jogador competitivo,
**Quero** filtrar cartas por categoria de habilidade,
**Para que** eu encontre cartas com funções específicas.

**Critérios de Aceitação:**
- [ ] Filtros por função: Draw, Search, Recovery, Energy Accel, Switching, Disruption, Protection
- [ ] Cartas categorizadas no banco de dados
- [ ] Combina com outros filtros (tipo + função)
- [ ] Atualização periódica com novas cartas

**Prioridade:** P1 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 3.9.1 | Schema de habilidades | Tabela de categorias no SQLite | 2 |
| 3.9.2 | Categorização inicial | Popular banco com cartas categorizadas | 5 |
| 3.9.3 | UI de filtro por função | Chips ou dropdown para funções | 2 |
| 3.9.4 | Combinação de filtros | Aplicar múltiplos filtros simultaneamente | 2 |

---

# ÉPICO 4: COMPARAÇÃO DE DECKS

**Descrição:** Ferramentas para comparar o deck do usuário contra decks meta e variações, com insights estatísticos e sugestões.

**Valor de Negócio:** Ajuda jogadores a entender forças e fraquezas do seu deck, otimizando para o meta atual.

**Prioridade:** P1

---

## User Story 4.1: Comparar com Decks META

**Como** jogador competitivo,
**Quero** comparar meu deck contra os decks do meta,
**Para que** eu entenda meus matchups.

**Critérios de Aceitação:**
- [ ] Lista decks META disponíveis para comparação
- [ ] Permite selecionar múltiplos decks META
- [ ] Usa deck ativo automaticamente como referência
- [ ] Exibe comparação lado a lado
- [ ] Mostra win rate esperado por matchup
- [ ] Destaca diferenças de cartas

**Prioridade:** P1 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 4.1.1 | Tela de seleção META | Lista de decks meta com checkboxes | 2 |
| 4.1.2 | Layout de comparação | Side-by-side ou tabbed view | 3 |
| 4.1.3 | Cálculo de matchup | Buscar/calcular win rate | 3 |
| 4.1.4 | Destaque de diferenças | Marcar cartas diferentes | 2 |

---

## User Story 4.2: Comparar Variações do Deck

**Como** jogador competitivo,
**Quero** ver variações do meu arquétipo de deck,
**Para que** eu possa avaliar diferentes builds.

**Critérios de Aceitação:**
- [ ] Busca variações do mesmo arquétipo no Limitless TCG
- [ ] Lista variações com % de uso em campeonatos
- [ ] Exibe diferenças de cartas entre variações
- [ ] Mostra win rate de cada variação
- [ ] Permite copiar variação para "Meus Decks"

**Prioridade:** P1 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 4.2.1 | Integração Limitless (variações) | API para buscar variações | 3 |
| 4.2.2 | Lista de variações | Cards com thumbnail e stats | 2 |
| 4.2.3 | Diff de decks | Algoritmo para calcular diferenças | 3 |
| 4.2.4 | Botão copiar variação | Importar variação para Meus Decks | 2 |

---

## User Story 4.3: Insights de Sequenciamento

**Como** jogador competitivo,
**Quero** ver sugestões de sequência de jogadas,
**Para que** eu saiba como pilotar o deck corretamente.

**Critérios de Aceitação:**
- [ ] Para variações conhecidas, exibe sequência típica (Turn 1, Turn 2, etc.)
- [ ] Indica cartas-chave para setup inicial
- [ ] Mostra probabilidade de setup ideal
- [ ] Quando não há dados, usa IA para gerar previsões
- [ ] Indica claramente quando são estimativas de IA

**Prioridade:** P2 | **Pontos:** 13

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 4.3.1 | Parser de sequências | Extrair sequências de dados Limitless | 5 |
| 4.3.2 | UI de timeline | Componente de timeline de turnos | 3 |
| 4.3.3 | Cálculo de probabilidade | Estatísticas de mão inicial | 3 |
| 4.3.4 | Fallback de IA | Gerar sequência quando não há dados | 5 |

---

## User Story 4.4: Estatísticas de Campeonatos

**Como** jogador competitivo,
**Quero** ver estatísticas de uso em campeonatos,
**Para que** eu saiba o desempenho real do deck.

**Critérios de Aceitação:**
- [ ] Exibe Top 8/16/32 appearances
- [ ] Win rate geral em torneios
- [ ] Matchups mais comuns em torneios
- [ ] Dados de City Leagues japonesas (cartas recentes)
- [ ] Mensagem clara quando não há dados

**Prioridade:** P1 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 4.4.1 | API Limitless (stats) | Endpoint para estatísticas de deck | 2 |
| 4.4.2 | UI de estatísticas | Cards com métricas principais | 2 |
| 4.4.3 | Gráfico de desempenho | Chart de win rate ao longo do tempo | 3 |

---

# ÉPICO 5: MODELO E AGENTE IA - VÍDEOS

**Descrição:** Sistema de IA para processar vídeos de partidas, treinar modelo de sugestões e fornecer insights avançados.

**Valor de Negócio:** Diferencial competitivo - nenhum outro app oferece análise de vídeos com IA.

**Prioridade:** P2

---

## User Story 5.1: Upload de Vídeos de Partidas

**Como** jogador,
**Quero** fazer upload de vídeos de minhas partidas,
**Para que** o sistema aprenda com elas.

**Critérios de Aceitação:**
- [ ] Botão de upload aceita MP4, MOV, AVI, WebM
- [ ] Progress bar durante upload
- [ ] Limite de tamanho: 500MB por vídeo
- [ ] Armazena localmente para processamento
- [ ] Lista vídeos enviados com status de processamento

**Prioridade:** P2 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 5.1.1 | File picker para vídeo | Seletor de arquivos com filtro | 2 |
| 5.1.2 | Upload com progress | Copiar arquivo com barra de progresso | 3 |
| 5.1.3 | Validação de formato | Verificar tipo e tamanho do arquivo | 1 |
| 5.1.4 | Lista de vídeos | Tela com vídeos enviados e status | 2 |

---

## User Story 5.2: Processar Vídeos do YouTube

**Como** jogador,
**Quero** colar URL de vídeos do YouTube,
**Para que** o sistema processe partidas de outros jogadores.

**Critérios de Aceitação:**
- [ ] Campo para colar URL do YouTube
- [ ] Valida se URL é válida e acessível
- [ ] Download do vídeo para processamento
- [ ] Suporta partidas TCG Live, table tops, torneios
- [ ] Exibe thumbnail e título do vídeo

**Prioridade:** P2 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 5.2.1 | Campo de URL | Input com validação de YouTube URL | 1 |
| 5.2.2 | Fetch de metadata | Obter thumbnail e título via API | 2 |
| 5.2.3 | Download de vídeo | Integração com yt-dlp ou similar | 5 |
| 5.2.4 | Fila de processamento | Gerenciar downloads em background | 3 |

---

## User Story 5.3: Processar Transcrições de Partidas

**Como** jogador,
**Quero** colar transcrições textuais de partidas,
**Para que** o sistema aprenda sem precisar de vídeo.

**Critérios de Aceitação:**
- [ ] Campo de texto multilinha para transcrição
- [ ] Parser identifica cartas mencionadas
- [ ] Constrói timeline de jogadas
- [ ] Associa com decks conhecidos
- [ ] Feedback de cartas identificadas

**Prioridade:** P2 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 5.3.1 | Campo de transcrição | TextArea grande com scroll | 1 |
| 5.3.2 | Parser de transcrição | NLP para identificar cartas e ações | 5 |
| 5.3.3 | Builder de timeline | Construir sequência de jogadas | 3 |
| 5.3.4 | Associação com decks | Mapear cartas para arquétipos | 2 |

---

## User Story 5.4: Reconhecimento de Cartas em Vídeo

**Como** sistema,
**Quero** identificar cartas jogadas em vídeos,
**Para que** eu possa extrair dados de partidas.

**Critérios de Aceitação:**
- [ ] Extrai frames relevantes do vídeo
- [ ] Detecta cartas visíveis na tela
- [ ] Identifica nome da carta via OCR ou image matching
- [ ] Registra sequência de jogadas por turno
- [ ] Armazena dados para treinamento do modelo

**Prioridade:** P3 | **Pontos:** 21

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 5.4.1 | Extração de frames | FFmpeg para extrair frames-chave | 3 |
| 5.4.2 | Detecção de cartas | Computer vision para localizar cartas | 8 |
| 5.4.3 | Identificação via matching | Comparar com banco de imagens de cartas | 8 |
| 5.4.4 | OCR de nomes | Fallback com leitura de texto | 5 |
| 5.4.5 | Persistência de dados | Salvar sequência extraída | 2 |

---

## User Story 5.5: Treinamento do Modelo de IA

**Como** sistema,
**Quero** treinar um modelo com dados de partidas,
**Para que** eu possa gerar sugestões precisas.

**Critérios de Aceitação:**
- [ ] Coleta dados de múltiplas fontes (vídeos, transcrições, Limitless)
- [ ] Treina modelo de sequenciamento
- [ ] Valida precisão do modelo
- [ ] Permite retraining com novos dados
- [ ] Versionamento de modelos

**Prioridade:** P3 | **Pontos:** 21

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 5.5.1 | Pipeline de dados | ETL para consolidar dados de treinamento | 5 |
| 5.5.2 | Arquitetura do modelo | Definir modelo de ML apropriado | 8 |
| 5.5.3 | Training loop | Implementar treinamento | 8 |
| 5.5.4 | Validação e métricas | Avaliar precisão do modelo | 3 |
| 5.5.5 | Versionamento | Sistema para versionar modelos | 2 |

---

# ÉPICO 6: NOTÍCIAS E EVENTOS

**Descrição:** Integração com fontes de notícias e calendário de eventos Pokemon TCG.

**Valor de Negócio:** Mantém usuários informados e engajados com a comunidade competitiva.

**Prioridade:** P1

---

## User Story 6.1: Feed de Notícias na Home

**Como** jogador de Pokemon TCG,
**Quero** ver as últimas notícias na tela inicial,
**Para que** eu fique atualizado sobre o jogo.

**Critérios de Aceitação:**
- [ ] Seção de notícias na home screen
- [ ] Busca notícias do PokeBeach via RSS/scraping
- [ ] Exibe título, thumbnail, data
- [ ] Clique abre artigo no navegador
- [ ] Scroll horizontal para mais notícias
- [ ] Refresh ao pull-down

**Prioridade:** P1 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 6.1.1 | Integração PokeBeach | Parser de RSS ou scraper | 3 |
| 6.1.2 | Card de notícia | Componente com thumbnail e título | 1 |
| 6.1.3 | Lista horizontal | Scroll horizontal de notícias | 1 |
| 6.1.4 | Open in browser | Abrir link externo | 1 |

---

## User Story 6.2: Próximos Campeonatos Oficiais

**Como** jogador competitivo,
**Quero** ver os próximos campeonatos oficiais,
**Para que** eu possa me planejar para participar.

**Critérios de Aceitação:**
- [ ] Seção de eventos na home
- [ ] Busca eventos do RK9
- [ ] Exibe nome, data, local, formato
- [ ] Filtro por região/país
- [ ] Link para página do evento

**Prioridade:** P1 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 6.2.1 | Integração RK9 | API ou scraper para eventos | 3 |
| 6.2.2 | Card de evento | Componente com dados do evento | 1 |
| 6.2.3 | Filtro de região | Dropdown para filtrar por local | 2 |
| 6.2.4 | Link para inscrição | Botão para abrir página do evento | 1 |

---

## User Story 6.3: Visualização Rápida de Eventos Inscritos

**Como** jogador competitivo,
**Quero** ver rapidamente meus próximos eventos na home,
**Para que** eu lembre das minhas inscrições.

**Critérios de Aceitação:**
- [ ] Widget na home com próximos eventos inscritos
- [ ] Countdown para o próximo evento
- [ ] Exibe deck associado (se definido)
- [ ] Link para detalhes no calendário
- [ ] Máximo 3-5 eventos visíveis

**Prioridade:** P1 | **Pontos:** 3

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 6.3.1 | Widget de eventos | Componente compacto para home | 2 |
| 6.3.2 | Countdown | Timer até próximo evento | 1 |
| 6.3.3 | Navegação para calendário | Link para tela de detalhes | 1 |

---

# ÉPICO 7: CALENDÁRIO DE COMPETIÇÕES

**Descrição:** Sistema para gerenciar participação em competições, registrar resultados e acompanhar performance.

**Valor de Negócio:** Ajuda jogadores a organizar sua carreira competitiva e analisar evolução.

**Prioridade:** P1

---

## User Story 7.1: Registrar Competição

**Como** jogador competitivo,
**Quero** registrar competições no meu calendário,
**Para que** eu possa me organizar.

**Critérios de Aceitação:**
- [ ] Formulário com campos: nome, data, horário, tipo, local/plataforma, formato
- [ ] Tipos: Online, Presencial, League Cup, League Challenge, Regional, Internacional, Worlds
- [ ] Associar deck utilizado (seleção de "Meus Decks")
- [ ] Salvar no banco de dados local
- [ ] Exibir na visualização de calendário

**Prioridade:** P1 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 7.1.1 | Formulário de evento | Tela com campos do evento | 2 |
| 7.1.2 | Seletor de deck | Dropdown com Meus Decks | 1 |
| 7.1.3 | Persistência de evento | Salvar no SQLite | 1 |
| 7.1.4 | Visualização de calendário | Componente de calendário com eventos | 3 |

---

## User Story 7.2: Registrar Resultados de Competição

**Como** jogador competitivo,
**Quero** registrar meus resultados após competir,
**Para que** eu possa acompanhar meu desempenho.

**Critérios de Aceitação:**
- [ ] Campos: vitórias, derrotas, empates, colocação final
- [ ] Registrar decks enfrentados por rodada
- [ ] Campo de notas opcional
- [ ] Calcular win rate automaticamente
- [ ] Atualizar estatísticas do jogador

**Prioridade:** P1 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 7.2.1 | Formulário de resultados | Campos de V/D/E e colocação | 2 |
| 7.2.2 | Registro por rodada | Lista de rodadas com deck enfrentado | 3 |
| 7.2.3 | Campo de notas | TextArea para observações | 1 |
| 7.2.4 | Cálculo de win rate | Atualizar estatísticas | 1 |

---

## User Story 7.3: Estatísticas de Performance

**Como** jogador competitivo,
**Quero** ver minhas estatísticas de performance,
**Para que** eu acompanhe minha evolução.

**Critérios de Aceitação:**
- [ ] Win rate geral
- [ ] Win rate por deck
- [ ] Win rate por matchup
- [ ] Gráfico de evolução ao longo do tempo
- [ ] Decks mais enfrentados
- [ ] Melhor/pior matchup

**Prioridade:** P1 | **Pontos:** 8

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 7.3.1 | Cálculo de estatísticas | Queries agregadas no SQLite | 3 |
| 7.3.2 | Tela de estatísticas | Dashboard com métricas | 3 |
| 7.3.3 | Gráfico de evolução | Chart line de win rate por período | 3 |
| 7.3.4 | Breakdown por matchup | Tabela de win rate por oponente | 2 |

---

## User Story 7.4: Criar Alerta no Calendário do Telefone

**Como** jogador competitivo,
**Quero** criar alertas automáticos no calendário do telefone,
**Para que** eu não esqueça das competições.

**Critérios de Aceitação:**
- [ ] Ao salvar evento, opção de criar alerta
- [ ] Selecionar quando alertar (1 dia antes, 2 horas antes, etc.)
- [ ] Integração com Google Calendar / Samsung Calendar
- [ ] Incluir nome do evento e deck no alerta
- [ ] Funcionar offline após criação

**Prioridade:** P1 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 7.4.1 | Opção de criar alerta | Checkbox no formulário de evento | 1 |
| 7.4.2 | Seletor de horário | Dropdown de opções de antecedência | 1 |
| 7.4.3 | Integração com calendário | Android Calendar Intent | 3 |
| 7.4.4 | Dados do evento | Passar informações para o alerta | 1 |

---

# ÉPICO 8: SUPORTE A SAMSUNG FOLD 6

**Descrição:** Garantir que o aplicativo funcione corretamente em ambos os modos de tela do Samsung Galaxy Z Fold 6.

**Valor de Negócio:** Requisito obrigatório para o dispositivo-alvo do usuário.

**Prioridade:** P0 (MVP)

---

## User Story 8.1: Layout Responsivo para Tela Fechada

**Como** usuário do Samsung Fold 6,
**Quero** usar o app na tela fechada (Cover Screen),
**Para que** eu tenha acesso rápido às funcionalidades.

**Critérios de Aceitação:**
- [ ] Layout adapta para proporção estreita (~25:9)
- [ ] Todos os elementos clicáveis são acessíveis
- [ ] Tamanho de fonte legível (mínimo 12sp)
- [ ] Navegação simplificada se necessário
- [ ] Performance adequada

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 8.1.1 | Media queries para Cover | Detectar dimensões da Cover Screen | 2 |
| 8.1.2 | Layout adaptado | Ajustes de layout para tela estreita | 3 |
| 8.1.3 | Teste em Cover Screen | Validar todas as telas na Cover | 2 |

---

## User Story 8.2: Layout Otimizado para Tela Aberta

**Como** usuário do Samsung Fold 6,
**Quero** aproveitar a tela grande quando aberta,
**Para que** eu tenha melhor experiência de uso.

**Critérios de Aceitação:**
- [ ] Layout expande para proporção tablet (~4:3)
- [ ] Grids de cartas mostram mais itens
- [ ] Comparações side-by-side aproveitam espaço
- [ ] Painéis laterais onde apropriado
- [ ] Transição suave entre modos

**Prioridade:** P0 | **Pontos:** 5

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 8.2.1 | Media queries para Main | Detectar dimensões da Main Screen | 2 |
| 8.2.2 | Layout expandido | Layouts otimizados para tela grande | 3 |
| 8.2.3 | Painéis laterais | Side panels para comparações | 2 |
| 8.2.4 | Teste em Main Screen | Validar todas as telas expandidas | 2 |

---

## User Story 8.3: Transição entre Modos de Tela

**Como** usuário do Samsung Fold 6,
**Quero** transição suave ao abrir/fechar o telefone,
**Para que** eu não perca meu contexto.

**Critérios de Aceitação:**
- [ ] Estado preservado durante transição
- [ ] Layout atualiza sem reiniciar tela
- [ ] Posição de scroll mantida (proporcional)
- [ ] Modals adaptam sem fechar
- [ ] Performance sem lag

**Prioridade:** P0 | **Pontos:** 3

### Tasks:

| ID | Task | Descrição | Pontos |
|----|------|-----------|--------|
| 8.3.1 | Listener de config change | Detectar mudança de tela | 1 |
| 8.3.2 | Preservação de estado | Manter estado durante transição | 2 |
| 8.3.3 | Teste de transição | Validar fluxos de dobra/desdobra | 2 |

---

# Resumo do Backlog

## Por Épico

| Épico | Stories | Story Points | Prioridade |
|-------|---------|--------------|------------|
| 1. Importação de Decks | 7 | 33 | P0 |
| 2. Meus Decks | 4 | 15 | P0 |
| 3. Criação e Edição | 9 | 51 | P0-P2 |
| 4. Comparação de Decks | 4 | 34 | P1-P2 |
| 5. IA e Vídeos | 5 | 66 | P2-P3 |
| 6. Notícias e Eventos | 3 | 13 | P1 |
| 7. Calendário | 4 | 23 | P1 |
| 8. Samsung Fold 6 | 3 | 13 | P0 |
| **TOTAL** | **39** | **248** | |

## Por Prioridade

| Prioridade | Stories | Story Points |
|------------|---------|--------------|
| P0 (MVP) | 18 | ~100 |
| P1 | 13 | ~70 |
| P2 | 5 | ~50 |
| P3 | 3 | ~28 |

---

# Roadmap Sugerido

## Sprint 1-2: MVP Core
- Épico 1: Importação de Decks (completo)
- Épico 2: Meus Decks (completo)
- User Stories 3.1-3.6 do Épico 3

## Sprint 3-4: MVP Completo
- User Stories 3.7-3.9 do Épico 3
- Épico 8: Samsung Fold 6 (completo)
- Testes e ajustes

## Sprint 5-6: Comparações e Eventos
- Épico 4: Comparação de Decks
- Épico 6: Notícias e Eventos

## Sprint 7-8: Calendário e IA Básica
- Épico 7: Calendário
- User Stories 5.1-5.3 do Épico 5

## Sprint 9+: IA Avançada
- User Stories 5.4-5.5 do Épico 5
- Melhorias contínuas

---

*Documento gerado em 2026-02-01*
*Autor: Bruno Strumendo*
