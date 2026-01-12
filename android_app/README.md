# TCG Meta Analyzer - Android App

Aplicativo Android para navegar pelos top decks competitivos de Pokemon TCG com análise de matchups e suporte bilíngue (Português/Inglês).

## Funcionalidades

- **Browse Meta Decks**: Visualize os top 8 decks do meta
- **Deck Details**: Informações completas incluindo estratégia, pontos fortes/fracos
- **Complete Deck Lists**: Todas as 60 cartas com nomes em PT/EN
- **Matchup Analysis**: Win rates e notas para cada confronto
- **Pokemon Search**: Busque decks que contêm um Pokemon específico
- **Bilingual**: Suporte completo para Português e Inglês

## Requisitos para Build

### Sistema Operacional
- Linux (recomendado: Ubuntu 20.04+)
- macOS (com algumas limitações)
- Windows via WSL2

### Dependências

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake
```

### Instalação do Buildozer

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar Kivy e Buildozer
pip install --upgrade pip
pip install kivy buildozer cython

# Verificar instalação
buildozer --version
```

## Build do APK

### Modo Debug (para testes)

```bash
cd android_app

# Primeira build (demora ~30 min, baixa Android SDK/NDK)
buildozer android debug

# O APK será gerado em: bin/tcgmeta-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Modo Release (para distribuição)

```bash
buildozer android release
```

## Instalação no Dispositivo

### Via ADB (com cabo USB)

```bash
# Habilite "Depuração USB" no Android
# Conecte o dispositivo via USB

adb install bin/tcgmeta-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Via Transferência de Arquivo

1. Copie o arquivo `.apk` para o dispositivo
2. Use um gerenciador de arquivos para abrir o APK
3. Permita instalação de "fontes desconhecidas" se solicitado

## Teste no Desktop (sem build)

Para testar a interface antes de gerar o APK:

```bash
cd android_app

# Instalar dependências
pip install kivy

# Executar
python main.py
```

## Estrutura do Projeto

```
android_app/
├── main.py           # Aplicativo Kivy principal
├── meta_data.py      # Dados dos decks (offline)
├── buildozer.spec    # Configuração do build
└── README.md         # Este arquivo
```

## Troubleshooting

### Erro: "SDK/NDK not found"

```bash
# Limpar cache e reconstruir
buildozer android clean
buildozer android debug
```

### Erro: "Java version not compatible"

```bash
# Verificar versão do Java
java -version

# Deve ser Java 11 ou 17
sudo apt install openjdk-17-jdk
sudo update-alternatives --config java
```

### Erro: "Recipe for X failed"

```bash
# Limpar tudo e recomeçar
rm -rf .buildozer
buildozer android debug
```

### App fecha imediatamente no Android

```bash
# Ver logs do app
adb logcat | grep python
```

## Build via GitHub Actions (CI/CD)

Crie `.github/workflows/build.yml`:

```yaml
name: Build Android APK

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install buildozer cython kivy

    - name: Build APK
      run: |
        cd android_app
        buildozer android debug

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: app-debug
        path: android_app/bin/*.apk
```

## Customização

### Alterar Ícone

1. Crie um ícone PNG 512x512
2. Salve como `android_app/icon.png`
3. Atualize `buildozer.spec`:
   ```
   icon.filename = %(source.dir)s/icon.png
   ```

### Alterar Cores

Edite em `main.py`:
```python
# Cor primária (header, botões)
get_color_from_hex('#2196F3')  # Azul

# Cor de sucesso (favorecido)
get_color_from_hex('#4CAF50')  # Verde

# Cor de perigo (desfavorecido)
get_color_from_hex('#F44336')  # Vermelho
```

### Adicionar Novos Decks

Edite `meta_data.py` e adicione ao dicionário `META_DECKS`:

```python
META_DECKS["novo_deck"] = MetaDeck(
    id="novo_deck",
    name_en="New Deck",
    name_pt="Novo Deck",
    tier=2,
    # ... resto dos campos
)
```

## Versões Testadas

- Python: 3.10+
- Kivy: 2.2.1
- Buildozer: 1.5.0
- Android API: 21-33
- Arquiteturas: arm64-v8a, armeabi-v7a

## Licença

MIT
