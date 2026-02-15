# Documento de Levantamento de Requisitos

## TCG Tool - Plataforma de Gestão de Decks Pokemon TCG

**Versão:** 2.0
**Data:** 2026-02-02
**Autor:** Bruno Strumendo
**Status:** Implementado

---

## 1. Visão Geral do Projeto

### 1.1 Objetivo
Desenvolver uma plataforma completa de gestão, análise e comparação de decks Pokemon TCG com recursos avançados de Inteligência Artificial para sugestões de jogadas, sequenciamento e análise de partidas.

### 1.2 Escopo
O sistema contempla:
- Aplicativo Android nativo (Samsung Galaxy Z Fold 6)
- Integração com APIs de dados Pokemon TCG
- Sistema de IA para análise de vídeos e sugestões
- Calendário de competições com alertas
- Portal de notícias integrado

### 1.3 Dispositivo Alvo
- **Modelo:** Samsung Galaxy Z Fold 6
- **Modos de Operação:** Tela fechada (Cover Screen) e tela aberta (Main Screen)
- **Requisito:** Layout responsivo para ambos os modos

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse |
|------------|-------|-----------|
| Jogador Competitivo | Usuário Final | Análise de decks, comparações, sugestões de jogadas |
| Jogador Casual | Usuário Final | Construção de decks, visualização de meta |
| Desenvolvedor | Técnico | Implementação e manutenção |

---

## 3. Requisitos Funcionais

### 3.1 Módulo: Importação de Decks [RF-IMP]

#### RF-IMP-001: Importar Deck via Texto
**Descrição:** O sistema deve permitir importar decks copiando texto diretamente do Pokemon TCG Live.
**Entrada:** Texto no formato PTCGO (ex: "4 Charizard ex OBF 125")
**Saída:** Deck parseado e validado
**Regras de Negócio:**
- Formato aceito: `[quantidade] [nome] [set] [número]`
- Ignorar linhas de comentário (iniciadas com # ou //)
- Ignorar headers de seção (Pokemon:, Trainer:, Energy:)

#### RF-IMP-002: Importar Deck via Arquivo
**Descrição:** O sistema deve permitir importar um ou mais decks a partir de arquivo .txt.
**Entrada:** Arquivo .txt contendo um ou mais decks
**Saída:** Lista de decks válidos importados
**Regras de Negócio:**
- Suportar múltiplos decks no mesmo arquivo (separados por linha em branco ou marcador)
- Validar cada deck individualmente
- Importar apenas decks válidos, ignorando inválidos
- Exibir relatório de importação (sucessos e falhas)

#### RF-IMP-003: Validação de Deck
**Descrição:** O sistema deve validar a estrutura do deck importado.
**Regras de Negócio:**
- Deck completo: exatamente 60 cartas
- Deck incompleto: menos de 60 cartas (permitido salvar com aviso)
- Máximo 4 cópias de cartas com mesmo nome (exceto energia básica)
- Verificar legalidade das cartas (rotation check)

#### RF-IMP-004: Visualização de Deck Importado
**Descrição:** O sistema deve exibir o deck importado de forma visual.
**Requisitos:**
- Exibir imagens das cartas (obtidas via API)
- Permitir clique na carta para visualização expandida
- Exibir estatísticas de utilização da carta (dados do Limitless TCG)
- Agrupar cartas por tipo: Pokemon, Treinadores, Energias

#### RF-IMP-005: Salvar Deck Importado
**Descrição:** O sistema deve permitir salvar o deck em "Meus Decks".
**Regras de Negócio:**
- Solicitar nome para o deck
- Associar deck ao perfil do usuário
- Remover deck da tela de importação após salvar
- Permitir salvar decks incompletos (com aviso visual)

#### RF-IMP-006: Remover Deck da Tela de Importação
**Descrição:** O sistema deve permitir remover o deck da tela sem salvar.
**Comportamento:** Exibir confirmação antes de descartar

---

### 3.2 Módulo: Meus Decks [RF-DECK]

#### RF-DECK-001: Listar Decks Salvos
**Descrição:** O sistema deve exibir todos os decks salvos pelo usuário.
**Requisitos:**
- Exibir thumbnail do deck (carta principal)
- Exibir nome, data de criação, status (completo/incompleto)
- Permitir ordenação (nome, data, mais usado)
- Indicar visualmente o deck ativo

#### RF-DECK-002: Selecionar Deck para Ações
**Descrição:** Ao selecionar um deck, exibir opções de ação.
**Opções Disponíveis:**
- Comparar contra decks META
- Comparar contra variações do deck
- Editar deck
- Tornar deck ativo
- Excluir deck

#### RF-DECK-003: Deck Ativo
**Descrição:** O sistema deve permitir marcar um deck como "ativo".
**Comportamento:**
- Apenas um deck pode estar ativo por vez
- Deck ativo é usado como referência em comparações
- Deck ativo exibe informações rápidas ao acessar outros menus
- Indicador visual claro do deck ativo

#### RF-DECK-004: Exibir Estatísticas do Deck
**Descrição:** Exibir informações estatísticas do deck selecionado.
**Métricas:**
- Quantidade de Pokemon/Treinadores/Energias
- Impacto de rotação (% de cartas que rotam)
- Win rate em campeonatos (se disponível no Limitless)
- Matchups favoráveis/desfavoráveis

---

### 3.3 Módulo: Criação e Edição de Deck [RF-BUILD]

#### RF-BUILD-001: Visualização Completa do Deck
**Descrição:** Exibir todas as 60 cartas do deck na tela.
**Organização:**
1. Pokemon (ordenados por linha evolutiva)
2. Treinadores (Supporters, Items, Tools, Stadiums)
3. Energias (Básicas, Especiais)

#### RF-BUILD-002: Filtro por Tipo de Carta
**Descrição:** Permitir filtrar a exibição por tipo.
**Filtros:**
- Todos
- Pokemon
- Treinadores (com sub-filtros: Supporter, Item, Tool, Stadium)
- Energias

#### RF-BUILD-003: Campo de Pesquisa Multilíngue
**Descrição:** Campo de busca que pesquisa em múltiplos atributos.
**Atributos Pesquisáveis:**
- Nome da carta (português e inglês)
- Código da coleção (ex: OBF, SVI)
- Número da carta
- Tipo de Pokemon
- Habilidades/Ataques

**Comportamento:**
- Pesquisa deve respeitar os filtros ativos
- Exibir resultados em tempo real (debounce de 300ms)
- Suportar busca parcial (ex: "Chari" encontra "Charizard")

#### RF-BUILD-004: Visualização de Cartas
**Descrição:** Exibir cartas em tamanho compatível com a tela.
**Comportamento:**
- Tamanho padrão: miniatura clicável
- Ao clicar: expandir para visualização detalhada
- Exibir quantidade de cópias no deck
- Indicar visualmente se carta está rotando

#### RF-BUILD-005: Adicionar/Remover Cartas
**Descrição:** Permitir adicionar e remover cartas do deck.
**Regras:**
- Máximo 4 cópias de cartas com mesmo nome
- Energia básica: sem limite
- Validar em tempo real (não permitir adicionar além do limite)
- Exibir contador de cartas (X/60)

#### RF-BUILD-006: Insights de IA ao Modificar Deck
**Descrição:** Ao trocar ou selecionar uma carta, exibir sugestões inteligentes.
**Funcionalidades:**
- Sugestões de substituição (cartas similares)
- Impacto no matchup (melhora/piora contra quais decks)
- Sinergias detectadas
- Alertas de problemas (ex: falta draw power)

#### RF-BUILD-007: Salvar Deck Incompleto
**Descrição:** Permitir salvar decks com menos de 60 cartas.
**Comportamento:**
- Exibir mensagem de aviso antes de salvar
- Marcar deck como "incompleto" na listagem
- Não permitir uso em comparações até estar completo

#### RF-BUILD-008: Base de Dados de Habilidades
**Descrição:** Manter base de habilidades categorizadas para filtros avançados.
**Categorias:**
- Draw (buscar cartas)
- Search (procurar no deck)
- Recovery (recuperar do descarte)
- Energy Acceleration (acelerar energia)
- Switching (trocar Pokemon ativo)
- Disruption (atrapalhar oponente)
- Protection (proteção)
- Damage Boost (aumentar dano)

---

### 3.4 Módulo: Comparação de Decks [RF-COMP]

#### RF-COMP-001: Comparar com Decks META
**Descrição:** Comparar o deck ativo contra decks do meta atual.
**Exibição:**
- Lista de decks META disponíveis para comparação
- Selecionar múltiplos decks para comparar
- Exibir lado a lado ou em lista

#### RF-COMP-002: Comparar Variações do Deck
**Descrição:** Comparar o deck ativo com variações do mesmo arquétipo.
**Fonte de Dados:** Limitless TCG (variações de decks em campeonatos)
**Exibição:**
- Diferenças de cartas destacadas
- % de uso de cada variação em campeonatos
- Win rate de cada variação

#### RF-COMP-003: Insights de Sequenciamento
**Descrição:** Para variações de deck, exibir insights de sequenciamento.
**Conteúdo:**
- Ordem sugerida de jogadas (Turn 1, Turn 2, etc.)
- Probabilidade de setup ideal
- Cartas-chave para mulligan

**Fonte de Dados:**
- Dados de campeonatos (Limitless TCG)
- City Leagues japonesas (cartas recentes)
- Análise de IA (quando não houver dados)

#### RF-COMP-004: Estatísticas de Utilização em Campeonatos
**Descrição:** Exibir dados estatísticos de uso em competições.
**Métricas:**
- Número de aparições em Top 8/16/32
- Win rate geral
- Matchups mais comuns

**Comportamento quando não há dados:**
- Informar que não há dados de campeonatos
- Gerar previsões via agente IA
- Indicar claramente que são estimativas

#### RF-COMP-005: Exibir Informações Estatísticas Laterais
**Descrição:** Ao comparar, exibir estatísticas em painel lateral ou inferior.
**Informações:**
- Diferença de cartas
- Impacto estimado no matchup
- Custo de modificação (cartas a adquirir)

---

### 3.5 Módulo: Modelo e Agente IA - Vídeos [RF-IA]

#### RF-IA-001: Upload de Vídeos de Partidas
**Descrição:** Permitir upload de vídeos gravados de partidas do TCG Live.
**Formatos Suportados:** MP4, MOV, AVI, WebM
**Fonte Típica:** Gravação de tela do celular
**Processamento:**
- Extrair frames relevantes
- Identificar cartas jogadas
- Registrar sequência de jogadas
- Armazenar para treinamento do modelo

#### RF-IA-002: Processar Vídeos do YouTube
**Descrição:** Permitir colar URL de vídeos do YouTube para processamento.
**Tipos de Vídeo:**
- Partidas do TCG Live
- Table tops (partidas presenciais filmadas)
- Torneios oficiais

**Processamento:**
- Download do vídeo (via API)
- Reconhecimento de cartas
- Extração de sequência de jogadas
- Armazenamento para treinamento

#### RF-IA-003: Processar Transcrições de Partidas
**Descrição:** Permitir colar transcrições textuais de partidas.
**Formato:** Texto livre descrevendo jogadas
**Processamento:**
- Parsing do texto
- Identificação de cartas mencionadas
- Construção de timeline de jogadas
- Associação com decks conhecidos

#### RF-IA-004: Treinamento do Modelo
**Descrição:** Usar dados coletados para treinar modelo de sugestões.
**Objetivos do Modelo:**
- Sugerir sequência de jogadas
- Prever jogadas do oponente
- Identificar melhores decisões por turno
- Calcular probabilidades de outcomes

#### RF-IA-005: Integração do Agente IA
**Descrição:** Agente IA disponível em todas as features.
**Funcionalidades:**
- Sugestões de jogadas em tempo real
- Análise de matchup
- Recomendações de modificação de deck
- Previsões quando não há dados reais

---

### 3.6 Módulo: Notícias [RF-NEWS]

#### RF-NEWS-001: Feed de Notícias na Home
**Descrição:** Exibir últimas notícias de Pokemon TCG na tela inicial.
**Fonte:** PokeBeach (https://www.pokebeach.com/)
**Exibição:**
- Título da notícia
- Thumbnail (se disponível)
- Data de publicação
- Link para artigo completo

#### RF-NEWS-002: Próximos Campeonatos Oficiais
**Descrição:** Exibir lista de próximos campeonatos oficiais.
**Fonte:** RK9 (https://rk9.gg/events/pokemon)
**Informações:**
- Nome do evento
- Data e horário
- Local (cidade/país)
- Formato (Standard, Expanded)
- Link para inscrição

#### RF-NEWS-003: Campeonatos Inscritos (Quick View)
**Descrição:** Exibir visualização rápida dos campeonatos em que o usuário está inscrito.
**Informações:**
- Próximo campeonato (destaque)
- Lista dos próximos 3-5 eventos
- Countdown para o mais próximo
- Link para detalhes no calendário

---

### 3.7 Módulo: Calendário [RF-CAL]

#### RF-CAL-001: Registrar Competições
**Descrição:** Permitir ao usuário registrar competições no calendário.
**Tipos de Competição:**
- Online (TCG Live, torneios online)
- Presencial (League Cups, League Challenges)
- Regionais
- Internacionais
- Worlds

**Campos:**
- Nome do evento
- Data e horário
- Local (presencial) ou plataforma (online)
- Formato (Standard, Expanded)
- Deck utilizado (link para Meus Decks)

#### RF-CAL-002: Registrar Resultados
**Descrição:** Permitir registrar resultados de competições.
**Campos:**
- Vitórias / Derrotas / Empates
- Colocação final
- Decks enfrentados (por rodada)
- Notas de partida (opcional)

#### RF-CAL-003: Estatísticas de Performance
**Descrição:** Calcular e exibir estatísticas de performance do jogador.
**Métricas:**
- Win rate geral
- Win rate por deck
- Win rate por matchup
- Evolução ao longo do tempo (gráfico)
- Decks mais enfrentados

#### RF-CAL-004: Criar Alerta no Calendário do Telefone
**Descrição:** Criar automaticamente alertas no calendário nativo do dispositivo.
**Comportamento:**
- Ao registrar competição, oferecer opção de criar alerta
- Definir horário do alerta (1 dia antes, 2 horas antes, etc.)
- Incluir informações básicas no evento
- Suportar Google Calendar / Samsung Calendar

---

## 4. Requisitos Não-Funcionais

### 4.1 Desempenho [RNF-PERF]

| ID | Requisito | Métrica |
|----|-----------|---------|
| RNF-PERF-001 | Tempo de carregamento inicial | < 3 segundos |
| RNF-PERF-002 | Tempo de resposta de busca | < 500ms |
| RNF-PERF-003 | Tempo de parse de deck | < 1 segundo |
| RNF-PERF-004 | Cache de imagens de cartas | Mínimo 100 cartas em cache |

### 4.2 Usabilidade [RNF-USA]

| ID | Requisito | Descrição |
|----|-----------|-----------|
| RNF-USA-001 | Responsividade | Suporte a tela fechada e aberta do Fold 6 |
| RNF-USA-002 | Idiomas | Suporte a Português e Inglês |
| RNF-USA-003 | Acessibilidade | Tamanho mínimo de fonte 12sp |
| RNF-USA-004 | Feedback visual | Loading indicators para operações > 1s |

### 4.3 Confiabilidade [RNF-CONF]

| ID | Requisito | Descrição |
|----|-----------|-----------|
| RNF-CONF-001 | Disponibilidade | Funcionamento offline para dados em cache |
| RNF-CONF-002 | Fallback de API | TCGdex (principal) -> Pokemon TCG API (fallback) |
| RNF-CONF-003 | Persistência | Dados salvos localmente (SQLite) |

### 4.4 Segurança [RNF-SEG]

| ID | Requisito | Descrição |
|----|-----------|-----------|
| RNF-SEG-001 | Dados do usuário | Armazenamento local criptografado |
| RNF-SEG-002 | Comunicação | HTTPS para todas as APIs |

---

## 5. Integrações

### 5.1 APIs Externas

| API | Uso | URL | Prioridade |
|-----|-----|-----|------------|
| TCGdex | Dados de cartas (10+ idiomas) | https://tcgdex.dev | Principal |
| Pokemon TCG API | Dados de cartas (inglês) | https://pokemontcg.io | Fallback |
| Limitless TCG | Dados de campeonatos e decks | https://limitlesstcg.com | Estatísticas |
| PokeBeach | Notícias | https://pokebeach.com | Notícias |
| RK9 | Calendário de eventos | https://rk9.gg | Eventos |

### 5.2 Integrações do Dispositivo

| Integração | Uso |
|------------|-----|
| Calendário Nativo | Criar alertas de competições |
| Sistema de Arquivos | Importar arquivos .txt |
| Câmera/Galeria | Upload de vídeos |

---

## 6. Restrições Técnicas

### 6.1 Plataforma
- Framework: Kivy (Python)
- Build: Buildozer
- Python: 3.10 ou 3.11 (não usar 3.12+ devido a distutils)
- Java: 17 (para build Android)

### 6.2 Dispositivo
- Mínimo Android 12
- Suporte a tela dobrável (Samsung Fold 6)
- Orientação: Portrait e Landscape

### 6.3 Armazenamento
- SQLite para cache de cartas
- JSON para configurações do usuário
- Sistema de arquivos para vídeos/imagens

---

## 7. Glossário

| Termo | Definição |
|-------|-----------|
| Meta | Conjunto de decks mais utilizados e eficientes no momento |
| Matchup | Relação de vantagem/desvantagem entre dois decks |
| Rotation | Processo de remoção de cartas antigas do formato Standard |
| PTCGO | Pokemon Trading Card Game Online (formato de exportação) |
| TCG Live | Versão atual do jogo digital oficial |
| Regulation Mark | Marcação que indica a era da carta (G, H, I) |
| Top 8 | Classificação entre os 8 melhores de um torneio |
| City League | Torneio local de nível intermediário |
| Win Rate | Percentual de vitórias |

---

## 8. Histórico de Revisões

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 2026-02-01 | Bruno Strumendo | Versão inicial |
| 2.0 | 2026-02-02 | Bruno Strumendo | Implementação completa de todos os módulos |

---

## 9. Aprovações

| Papel | Nome | Data | Assinatura |
|-------|------|------|------------|
| Product Owner | Bruno Strumendo | | |
| Tech Lead | | | |
