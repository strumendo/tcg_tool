# Diagramas de Fluxo - TCG Tool

## Visualização dos Diagramas

Os diagramas abaixo utilizam a sintaxe Mermaid. Para visualizá-los:
- **GitHub**: Renderiza automaticamente
- **VS Code**: Extensão "Markdown Preview Mermaid Support"
- **Online**: https://mermaid.live

---

## 1. Arquitetura Geral do Sistema

```mermaid
flowchart TB
    subgraph App["Aplicativo Android (Kivy)"]
        UI[Interface do Usuário]
        BL[Business Logic]
        DB[(SQLite Local)]
        Cache[Cache de Imagens]
    end

    subgraph APIs["APIs Externas"]
        TCGdex[TCGdex API]
        PTCGAPI[Pokemon TCG API]
        Limitless[Limitless TCG]
        PokeBeach[PokeBeach RSS]
        RK9[RK9 Events]
    end

    subgraph Device["Integrações do Dispositivo"]
        Calendar[Calendário Nativo]
        FileSystem[Sistema de Arquivos]
        Gallery[Galeria/Câmera]
    end

    subgraph AI["Sistema de IA"]
        VideoProc[Processador de Vídeo]
        MLModel[Modelo de ML]
        NLP[Parser de Transcrição]
    end

    UI --> BL
    BL --> DB
    BL --> Cache
    BL --> TCGdex
    TCGdex -.->|fallback| PTCGAPI
    BL --> Limitless
    BL --> PokeBeach
    BL --> RK9
    BL --> Calendar
    BL --> FileSystem
    BL --> Gallery
    BL --> AI
    VideoProc --> MLModel
    NLP --> MLModel
```

---

## 2. Navegação Principal do App

```mermaid
flowchart LR
    subgraph Home["HOME"]
        H1[Bem-vindo]
        H2[Notícias]
        H3[Próximos Eventos]
        H4[Deck Ativo]
    end

    subgraph Import["IMPORTAÇÃO"]
        I1[Colar Texto]
        I2[Selecionar Arquivo]
        I3[Validação]
        I4[Preview]
        I5[Salvar]
    end

    subgraph MyDecks["MEUS DECKS"]
        D1[Lista de Decks]
        D2[Detalhes do Deck]
        D3[Editar Deck]
        D4[Comparar]
    end

    subgraph Meta["META"]
        M1[Lista Meta Decks]
        M2[Detalhes Meta]
        M3[Matchups]
    end

    subgraph Calendar["CALENDÁRIO"]
        C1[Visualização]
        C2[Novo Evento]
        C3[Resultados]
        C4[Estatísticas]
    end

    subgraph AI["IA/VÍDEOS"]
        A1[Upload Vídeo]
        A2[URL YouTube]
        A3[Transcrição]
        A4[Processamento]
    end

    subgraph Settings["CONFIG"]
        S1[Idioma]
        S2[Notificações]
        S3[Perfil]
    end

    Home --> Import
    Home --> MyDecks
    Home --> Meta
    Home --> Calendar
    Home --> AI
    Home --> Settings

    Import --> MyDecks
    MyDecks --> Meta
    Meta --> MyDecks
    Calendar --> MyDecks
```

---

## 3. Fluxo de Importação de Deck

```mermaid
flowchart TD
    Start([Início]) --> Choice{Método de Importação}

    Choice -->|Texto| TextInput[Colar texto do TCG Live]
    Choice -->|Arquivo| FileSelect[Selecionar arquivo .txt]

    TextInput --> Parse[Parser PTCGO]
    FileSelect --> MultiDeck{Múltiplos decks?}

    MultiDeck -->|Sim| SplitDecks[Separar decks]
    MultiDeck -->|Não| Parse
    SplitDecks --> Parse

    Parse --> Validate{Validação}

    Validate -->|Erro de formato| ErrorFormat[Exibir erro de formato]
    ErrorFormat --> TextInput

    Validate -->|Válido| CheckComplete{60 cartas?}

    CheckComplete -->|Sim| Complete[Deck Completo]
    CheckComplete -->|Não| Incomplete[Deck Incompleto]

    Complete --> Preview[Visualizar Deck]
    Incomplete --> WarnIncomplete[Aviso: Deck Incompleto]
    WarnIncomplete --> Preview

    Preview --> FetchImages[Buscar Imagens via API]
    FetchImages --> ShowCards[Exibir Grid de Cartas]

    ShowCards --> Actions{Ação}

    Actions -->|Expandir| ExpandCard[Modal com detalhes da carta]
    ExpandCard --> ShowCards

    Actions -->|Salvar| NameDeck[Definir nome do deck]
    NameDeck --> SaveDB[(Salvar no SQLite)]
    SaveDB --> ClearScreen[Limpar tela]
    ClearScreen --> End([Fim - Ir para Meus Decks])

    Actions -->|Descartar| ConfirmDiscard{Confirmar descarte?}
    ConfirmDiscard -->|Sim| ClearScreen
    ConfirmDiscard -->|Não| ShowCards

    Actions -->|Estatísticas| FetchStats[Buscar dados Limitless]
    FetchStats --> ShowStats[Exibir estatísticas]
    ShowStats --> ShowCards
```

---

## 4. Fluxo de Criação/Edição de Deck

```mermaid
flowchart TD
    Start([Início]) --> LoadDeck{Novo ou Editar?}

    LoadDeck -->|Novo| EmptyDeck[Criar deck vazio]
    LoadDeck -->|Editar| FetchDeck[Carregar deck do SQLite]

    EmptyDeck --> DeckView[Visualização do Deck]
    FetchDeck --> DeckView

    DeckView --> UserAction{Ação do Usuário}

    UserAction -->|Pesquisar| SearchInput[Digite termo de busca]
    SearchInput --> Debounce[Aguarda 300ms]
    Debounce --> SearchAPI[Buscar no cache/API]
    SearchAPI --> FilterActive{Filtros ativos?}
    FilterActive -->|Sim| ApplyFilter[Aplicar filtros]
    FilterActive -->|Não| ShowResults[Exibir resultados]
    ApplyFilter --> ShowResults
    ShowResults --> DeckView

    UserAction -->|Filtrar| SelectFilter[Selecionar tipo/função]
    SelectFilter --> ApplyFilter2[Filtrar cartas visíveis]
    ApplyFilter2 --> DeckView

    UserAction -->|Adicionar Carta| CheckAdd{Pode adicionar?}
    CheckAdd -->|< 4 cópias E < 60 total| AddCard[Adicionar ao deck]
    CheckAdd -->|>= 4 cópias| ErrorCopies[Erro: Limite de cópias]
    CheckAdd -->|>= 60 cartas| ErrorFull[Erro: Deck cheio]
    AddCard --> UpdateCounter[Atualizar contador]
    ErrorCopies --> DeckView
    ErrorFull --> DeckView
    UpdateCounter --> TriggerIA[Disparar análise IA]
    TriggerIA --> ShowInsights[Exibir sugestões]
    ShowInsights --> DeckView

    UserAction -->|Remover Carta| RemoveCard[Decrementar quantidade]
    RemoveCard --> CheckZero{Quantidade = 0?}
    CheckZero -->|Sim| DeleteCard[Remover carta do deck]
    CheckZero -->|Não| UpdateCounter2[Atualizar contador]
    DeleteCard --> UpdateCounter2
    UpdateCounter2 --> DeckView

    UserAction -->|Expandir Carta| FetchDetails[Buscar detalhes da API]
    FetchDetails --> ShowModal[Exibir modal com detalhes]
    ShowModal --> DeckView

    UserAction -->|Salvar| CheckComplete{60 cartas?}
    CheckComplete -->|Sim| SaveComplete[Salvar como completo]
    CheckComplete -->|Não| WarnSave{Salvar incompleto?}
    WarnSave -->|Sim| SaveIncomplete[Salvar como incompleto]
    WarnSave -->|Não| DeckView
    SaveComplete --> Persist[(Persistir no SQLite)]
    SaveIncomplete --> Persist
    Persist --> Success[Toast: Deck salvo!]
    Success --> End([Fim])
```

---

## 5. Fluxo de Comparação de Decks

```mermaid
flowchart TD
    Start([Início]) --> CheckActive{Deck ativo definido?}

    CheckActive -->|Não| SelectDeck[Selecionar deck para comparar]
    CheckActive -->|Sim| LoadActive[Carregar deck ativo]

    SelectDeck --> LoadActive
    LoadActive --> CompareType{Tipo de comparação}

    CompareType -->|vs META| ShowMetaList[Listar decks META]
    ShowMetaList --> SelectMeta[Selecionar decks META]
    SelectMeta --> LoadMeta[Carregar decks selecionados]
    LoadMeta --> CompareView[Visualização de Comparação]

    CompareType -->|Variações| FetchVariations[Buscar variações no Limitless]
    FetchVariations --> HasVariations{Variações encontradas?}
    HasVariations -->|Sim| ShowVariations[Listar variações]
    HasVariations -->|Não| NoData[Exibir: Sem dados]
    ShowVariations --> SelectVariation[Selecionar variação]
    SelectVariation --> CompareView
    NoData --> AIGenerate[Gerar sugestões via IA]
    AIGenerate --> CompareView

    CompareView --> DisplayMode{Modo de exibição}

    DisplayMode -->|Side by Side| SideBySide[Comparação lado a lado]
    DisplayMode -->|Diff View| DiffView[Exibir diferenças]
    DisplayMode -->|Stats| StatsView[Estatísticas comparativas]

    SideBySide --> Insights[Exibir insights]
    DiffView --> Insights
    StatsView --> Insights

    Insights --> Actions{Ações}

    Actions -->|Ver Matchup| ShowMatchup[Win rate por matchup]
    ShowMatchup --> CompareView

    Actions -->|Ver Sequência| HasSequence{Dados de sequência?}
    HasSequence -->|Sim| ShowSequence[Exibir timeline de turnos]
    HasSequence -->|Não| GenerateSequence[IA gera sequência]
    GenerateSequence --> ShowSequence
    ShowSequence --> CompareView

    Actions -->|Copiar Variação| CopyDeck[Importar para Meus Decks]
    CopyDeck --> End([Fim - Ir para Meus Decks])

    Actions -->|Voltar| End2([Fim])
```

---

## 6. Fluxo de Processamento de Vídeo/IA

```mermaid
flowchart TD
    Start([Início]) --> InputType{Tipo de entrada}

    InputType -->|Upload Vídeo| SelectVideo[Selecionar arquivo de vídeo]
    InputType -->|URL YouTube| PasteURL[Colar URL do YouTube]
    InputType -->|Transcrição| PasteText[Colar texto de transcrição]

    SelectVideo --> ValidateFile{Formato válido?}
    ValidateFile -->|Não| ErrorFormat[Erro: Formato inválido]
    ValidateFile -->|Sim| UploadFile[Upload do arquivo]
    ErrorFormat --> Start

    PasteURL --> ValidateURL{URL válida?}
    ValidateURL -->|Não| ErrorURL[Erro: URL inválida]
    ValidateURL -->|Sim| FetchMetadata[Buscar metadata do vídeo]
    ErrorURL --> Start
    FetchMetadata --> DownloadVideo[Download do vídeo]

    UploadFile --> Queue[Adicionar à fila de processamento]
    DownloadVideo --> Queue

    PasteText --> ParseText[Parser de transcrição]
    ParseText --> ExtractCards[Identificar cartas mencionadas]
    ExtractCards --> BuildTimeline[Construir timeline de jogadas]

    Queue --> Process[Iniciar processamento]
    Process --> ExtractFrames[Extrair frames-chave]
    ExtractFrames --> DetectCards[Detectar cartas nos frames]
    DetectCards --> IdentifyCards[Identificar cartas via matching]
    IdentifyCards --> BuildTimeline

    BuildTimeline --> ValidateData{Dados suficientes?}

    ValidateData -->|Não| PartialData[Dados parciais salvos]
    ValidateData -->|Sim| SaveData[(Salvar no banco de treinamento)]

    PartialData --> SaveData
    SaveData --> UpdateModel{Retreinar modelo?}

    UpdateModel -->|Sim| TrainModel[Executar treinamento]
    UpdateModel -->|Não| End([Fim])

    TrainModel --> ValidateModel[Validar precisão]
    ValidateModel --> SaveModel[Salvar nova versão do modelo]
    SaveModel --> End
```

---

## 7. Fluxo de Calendário e Eventos

```mermaid
flowchart TD
    Start([Início]) --> View{Visualização}

    View -->|Calendário| ShowCalendar[Exibir calendário mensal]
    View -->|Lista| ShowList[Exibir lista de eventos]

    ShowCalendar --> SelectDate[Selecionar data]
    SelectDate --> ShowDayEvents[Exibir eventos do dia]

    ShowList --> SelectEvent[Selecionar evento]
    ShowDayEvents --> SelectEvent

    SelectEvent --> EventDetails[Detalhes do evento]

    EventDetails --> EventAction{Ação}

    EventAction -->|Editar| EditEvent[Formulário de edição]
    EditEvent --> SaveEvent[(Salvar alterações)]
    SaveEvent --> EventDetails

    EventAction -->|Registrar Resultados| ResultForm[Formulário de resultados]
    ResultForm --> EnterResults[V/D/E, Colocação]
    EnterResults --> EnterRounds[Decks por rodada]
    EnterRounds --> EnterNotes[Notas opcionais]
    EnterNotes --> SaveResults[(Salvar resultados)]
    SaveResults --> UpdateStats[Atualizar estatísticas]
    UpdateStats --> EventDetails

    EventAction -->|Ver Estatísticas| ShowStats[Dashboard de performance]
    ShowStats --> StatsDetail{Detalhe}
    StatsDetail -->|Por Deck| DeckStats[Win rate por deck]
    StatsDetail -->|Por Matchup| MatchupStats[Win rate por oponente]
    StatsDetail -->|Evolução| TimeChart[Gráfico temporal]
    DeckStats --> ShowStats
    MatchupStats --> ShowStats
    TimeChart --> ShowStats

    EventAction -->|Excluir| ConfirmDelete{Confirmar?}
    ConfirmDelete -->|Sim| DeleteEvent[(Remover evento)]
    ConfirmDelete -->|Não| EventDetails
    DeleteEvent --> ShowCalendar

    View -->|Novo Evento| NewEvent[Formulário de novo evento]
    NewEvent --> FillForm[Preencher dados]
    FillForm --> SelectDeck[Associar deck]
    SelectDeck --> SetAlert{Criar alerta?}
    SetAlert -->|Sim| ChooseTime[Escolher antecedência]
    SetAlert -->|Não| SaveNew[(Salvar evento)]
    ChooseTime --> CreateCalendarEvent[Criar no calendário nativo]
    CreateCalendarEvent --> SaveNew
    SaveNew --> ShowCalendar
```

---

## 8. Fluxo de Transição de Tela (Samsung Fold 6)

```mermaid
flowchart TD
    Start([Usuário usando app]) --> ScreenState{Estado da tela}

    ScreenState -->|Fechada| CoverMode[Modo Cover Screen]
    ScreenState -->|Aberta| MainMode[Modo Main Screen]

    CoverMode --> UserFolds{Usuário abre telefone}
    UserFolds --> DetectChange[Detectar mudança de configuração]
    DetectChange --> SaveState[Preservar estado atual]
    SaveState --> ResizeLayout[Redimensionar layout]
    ResizeLayout --> ApplyMainLayout[Aplicar layout Main Screen]
    ApplyMainLayout --> RestoreState[Restaurar estado]
    RestoreState --> MainMode

    MainMode --> UserUnfolds{Usuário fecha telefone}
    UserUnfolds --> DetectChange2[Detectar mudança de configuração]
    DetectChange2 --> SaveState2[Preservar estado atual]
    SaveState2 --> ResizeLayout2[Redimensionar layout]
    ResizeLayout2 --> ApplyCoverLayout[Aplicar layout Cover Screen]
    ApplyCoverLayout --> RestoreState2[Restaurar estado]
    RestoreState2 --> CoverMode
```

---

## 9. Modelo de Dados (ER Simplificado)

```mermaid
erDiagram
    USER ||--o{ DECK : owns
    USER ||--o{ EVENT : participates
    USER {
        int id PK
        string name
        string email
        string language
        datetime created_at
    }

    DECK ||--|{ DECK_CARD : contains
    DECK {
        int id PK
        int user_id FK
        string name
        boolean is_complete
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CARD ||--o{ DECK_CARD : included_in
    CARD {
        int id PK
        string name_en
        string name_pt
        string set_code
        string set_number
        string card_type
        string subtype
        string regulation_mark
        string image_url
        json abilities
        json attacks
    }

    DECK_CARD {
        int deck_id FK
        int card_id FK
        int quantity
    }

    EVENT ||--o{ EVENT_ROUND : has
    EVENT {
        int id PK
        int user_id FK
        int deck_id FK
        string name
        string event_type
        string format
        datetime date
        string location
        int wins
        int losses
        int draws
        int placement
        text notes
    }

    EVENT_ROUND {
        int id PK
        int event_id FK
        int round_number
        string opponent_deck
        string result
        text notes
    }

    META_DECK ||--|{ META_DECK_CARD : contains
    META_DECK ||--o{ MATCHUP : has
    META_DECK {
        int id PK
        string name_en
        string name_pt
        int tier
        float meta_share
        string strategy_en
        string strategy_pt
    }

    MATCHUP {
        int deck_a_id FK
        int deck_b_id FK
        float win_rate
        text notes
    }

    VIDEO_DATA {
        int id PK
        string source_type
        string source_url
        datetime processed_at
        json extracted_sequence
        boolean used_for_training
    }
```

---

## 10. Sequência de API Calls - Busca de Carta

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as App
    participant C as Cache Local
    participant T as TCGdex API
    participant P as Pokemon TCG API

    U->>A: Digita termo de busca
    A->>A: Debounce 300ms
    A->>C: Buscar no cache

    alt Encontrado no cache
        C-->>A: Retorna cartas
        A-->>U: Exibe resultados
    else Não encontrado
        A->>T: GET /cards?name={termo}

        alt TCGdex responde
            T-->>A: Lista de cartas
            A->>C: Salvar no cache
            A-->>U: Exibe resultados
        else TCGdex falha
            T-->>A: Erro/Timeout
            A->>P: GET /cards?q=name:{termo}

            alt Pokemon TCG API responde
                P-->>A: Lista de cartas
                A->>C: Salvar no cache
                A-->>U: Exibe resultados
            else Pokemon TCG API falha
                P-->>A: Erro
                A-->>U: Exibe erro de conexão
            end
        end
    end
```

---

## 11. Estados da Interface - Deck Ativo

```mermaid
stateDiagram-v2
    [*] --> SemDeckAtivo: App iniciado

    SemDeckAtivo --> DeckAtivado: Usuário marca deck como ativo
    DeckAtivado --> SemDeckAtivo: Usuário desmarca deck
    DeckAtivado --> OutroDeckAtivado: Usuário ativa outro deck
    OutroDeckAtivado --> DeckAtivado: (automático)

    state DeckAtivado {
        [*] --> Exibindo
        Exibindo --> AtualizandoInfo: Dados mudaram
        AtualizandoInfo --> Exibindo: Atualização completa
    }

    state SemDeckAtivo {
        [*] --> OcultandoWidget
        OcultandoWidget --> SugerindoAtivacao: Usuário entra em Comparação
    }
```

---

## Legenda dos Diagramas

### Formas

| Forma | Significado |
|-------|-------------|
| `([texto])` | Início/Fim |
| `[texto]` | Processo |
| `{texto}` | Decisão |
| `[(texto)]` | Banco de dados |
| `(texto)` | Estado |

### Setas

| Seta | Significado |
|------|-------------|
| `-->` | Fluxo principal |
| `-.->` | Fluxo alternativo/fallback |
| `-->>` | Resposta/Retorno |

### Cores (quando renderizado)

| Cor | Significado |
|-----|-------------|
| Verde | Sucesso/Caminho feliz |
| Vermelho | Erro/Falha |
| Amarelo | Aviso/Atenção |
| Azul | Informação/Processo |

---

*Documento gerado em 2026-02-01*
*Atualizado em 2026-02-02*
*Autor: Bruno Strumendo*
*Ferramenta: Mermaid.js*
*Status: Implementado - v2.0*
