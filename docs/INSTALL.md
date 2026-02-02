# Guia de Instalação - TCG Tool v2.0

## Índice

1. [Requisitos do Sistema](#1-requisitos-do-sistema)
2. [Instalação do Ambiente de Desenvolvimento](#2-instalação-do-ambiente-de-desenvolvimento)
3. [Executar no Desktop (Teste)](#3-executar-no-desktop-teste)
4. [Build do APK Android](#4-build-do-apk-android)
5. [Instalação no Dispositivo](#5-instalação-no-dispositivo)
6. [Verificação da Instalação](#6-verificação-da-instalação)
7. [Solução de Problemas](#7-solução-de-problemas)

---

## 1. Requisitos do Sistema

### 1.1 Para Desenvolvimento (Desktop)

| Componente | Requisito |
|------------|-----------|
| Sistema Operacional | Linux (Ubuntu 20.04+), macOS, Windows (via WSL2) |
| Python | 3.10 ou 3.11 (NÃO usar 3.12+) |
| RAM | Mínimo 4GB |
| Espaço em Disco | 500MB para dependências |

### 1.2 Para Build Android

| Componente | Requisito |
|------------|-----------|
| Sistema Operacional | Linux (recomendado) ou macOS |
| Python | 3.10 ou 3.11 |
| Java | JDK 17 |
| RAM | Mínimo 8GB |
| Espaço em Disco | 10GB (SDK/NDK Android) |

### 1.3 Dispositivo Android

| Componente | Requisito |
|------------|-----------|
| Android | 5.0+ (API 21+) |
| Arquitetura | arm64-v8a ou armeabi-v7a |
| Dispositivo Alvo | Samsung Galaxy Z Fold 6 |

---

## 2. Instalação do Ambiente de Desenvolvimento

### Passo 2.1: Instalar Python 3.10/3.11

**Ubuntu/Debian:**
```bash
# Adicionar repositório deadsnakes (se necessário)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Instalar Python 3.10
sudo apt install python3.10 python3.10-venv python3.10-dev

# Verificar instalação
python3.10 --version
```

**macOS (via Homebrew):**
```bash
brew install python@3.10
```

**Windows (WSL2):**
```bash
# No terminal WSL2 Ubuntu
sudo apt update
sudo apt install python3.10 python3.10-venv
```

### Passo 2.2: Clonar o Repositório

```bash
# Via HTTPS
git clone https://github.com/strumendo/tcg_tool.git

# Via SSH
git clone git@github.com:strumendo/tcg_tool.git

# Entrar no diretório
cd tcg_tool
```

### Passo 2.3: Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python3.10 -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### Passo 2.4: Instalar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt

# Instalar Kivy (para Android app)
pip install kivy
```

### Passo 2.5: Verificar Instalação

```bash
# Verificar versão do Python
python --version
# Esperado: Python 3.10.x ou 3.11.x

# Verificar Kivy
python -c "import kivy; print(kivy.__version__)"
# Esperado: 2.x.x

# Executar testes
python -m pytest tests/ -v
# Esperado: 59 testes passando
```

---

## 3. Executar no Desktop (Teste)

### Passo 3.1: Executar CLI Tool

```bash
# Modo interativo
python main.py

# Analisar deck
python main.py example_deck.txt

# Ver decks meta
python main.py -m

# Ver matchups
python main.py --matchups

# Definir idioma
python main.py --lang pt
```

### Passo 3.2: Executar App Android (Desktop Preview)

```bash
# Opção 1: Do diretório raiz
python android_app/main.py

# Opção 2: Do diretório android_app
cd android_app
python main.py
```

**Navegação no App:**
- Use o mouse para simular toques
- A janela simula o tamanho de um smartphone
- Teste todas as telas: Home, Import, My Decks, etc.

### Passo 3.3: Testar Responsividade (Samsung Fold 6)

```bash
# Simular tela fechada (Cover Screen ~6.2")
# Redimensione a janela para aproximadamente 420x900 pixels

# Simular tela aberta (Main Screen ~7.6")
# Redimensione a janela para aproximadamente 800x600 pixels
```

---

## 4. Build do APK Android

### Passo 4.1: Instalar Dependências do Sistema (Ubuntu)

```bash
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
    libncurses-dev \
    libtinfo6 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake \
    ant
```

### Passo 4.2: Verificar Java

```bash
# Verificar versão do Java
java -version
# Esperado: openjdk version "17.x.x"

# Se necessário, selecionar Java 17
sudo update-alternatives --config java
```

### Passo 4.3: Instalar Buildozer

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar Buildozer e dependências
pip install buildozer cython

# Verificar instalação
buildozer --version
```

### Passo 4.4: Executar Build

```bash
# Entrar no diretório do app Android
cd android_app

# Primeira build (demora ~30 minutos)
# Baixa Android SDK, NDK e dependências
buildozer android debug

# Builds subsequentes são mais rápidas (~5-10 min)
```

### Passo 4.5: Localizar o APK

```bash
# O APK será gerado em:
ls -la bin/

# Nome do arquivo:
# tcgtool-2.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

---

## 5. Instalação no Dispositivo

### Opção A: Via ADB (Recomendado)

**Passo 5A.1: Habilitar Depuração USB no Android**
1. Vá em **Configurações** > **Sobre o telefone**
2. Toque 7 vezes em **Número da versão** (ativa Opções do desenvolvedor)
3. Volte para **Configurações** > **Opções do desenvolvedor**
4. Ative **Depuração USB**

**Passo 5A.2: Conectar e Instalar**
```bash
# Verificar se dispositivo está conectado
adb devices
# Esperado: Lista seu dispositivo

# Instalar APK
adb install android_app/bin/tcgtool-2.0.0-arm64-v8a_armeabi-v7a-debug.apk

# Se já existe versão anterior:
adb install -r android_app/bin/tcgtool-2.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Opção B: Via Transferência de Arquivo

**Passo 5B.1: Transferir APK**
1. Conecte o dispositivo via cabo USB
2. Copie o arquivo `.apk` da pasta `android_app/bin/` para o dispositivo
3. Ou envie via Google Drive, email, etc.

**Passo 5B.2: Instalar no Dispositivo**
1. Abra um gerenciador de arquivos no Android
2. Navegue até o APK
3. Toque no arquivo para instalar
4. Se solicitado, permita instalação de "fontes desconhecidas"
5. Toque em **Instalar**

### Opção C: Via QR Code (WiFi)

```bash
# Iniciar servidor HTTP no diretório do APK
cd android_app/bin
python -m http.server 8000

# No navegador do celular (mesma rede WiFi):
# http://IP_DO_COMPUTADOR:8000/tcgtool-2.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

---

## 6. Verificação da Instalação

### 6.1: Checklist de Funcionalidades

Após instalar, verifique:

- [ ] App abre sem erros
- [ ] Tela inicial (Home) carrega
- [ ] Navegação entre telas funciona
- [ ] Tela de Import aceita texto
- [ ] My Decks salva e lista decks
- [ ] Deck Editor permite edição
- [ ] Meta decks são exibidos
- [ ] Idioma pode ser alterado (PT/EN)

### 6.2: Teste em Samsung Galaxy Z Fold 6

- [ ] App funciona com tela fechada (Cover Screen)
- [ ] App funciona com tela aberta (Main Screen)
- [ ] Layout se adapta ao abrir/fechar
- [ ] Não há cortes ou sobreposições de UI

### 6.3: Ver Logs do App (Debug)

```bash
# Conectar via ADB e ver logs
adb logcat | grep python

# Filtrar apenas erros
adb logcat *:E | grep python
```

---

## 7. Solução de Problemas

### Problema: "No module named 'distutils'"

**Causa:** Python 3.12+ removeu distutils

**Solução:**
```bash
# Opção 1: Instalar setuptools
pip install setuptools

# Opção 2: Usar Python 3.10/3.11 (recomendado)
python3.10 -m venv venv
source venv/bin/activate
```

### Problema: "SDK/NDK not found"

**Solução:**
```bash
cd android_app
rm -rf .buildozer
buildozer android debug
```

### Problema: Build falha com erro de Cython

**Solução:**
```bash
pip install "Cython<3.0" --force-reinstall
rm -rf android_app/.buildozer
cd android_app && buildozer android debug
```

### Problema: App fecha imediatamente no Android

**Diagnóstico:**
```bash
adb logcat | grep -E "(python|kivy|Error)"
```

**Soluções comuns:**
1. Verificar se todas as dependências estão no `requirements`
2. Limpar e refazer build
3. Verificar arquitetura do dispositivo (arm64/arm32)

### Problema: Tela branca no Samsung Fold

**Solução:**
1. Configurações > Apps > TCG Tool
2. Permitir "Redimensionável em multi-janela"
3. Reiniciar o app

### Problema: Erro de permissão ao instalar APK

**Solução:**
1. Configurações > Apps > Fontes desconhecidas
2. Permitir instalação do gerenciador de arquivos usado

### Problema: "Recipe for X failed" durante build

**Solução:**
```bash
# Limpar completamente e recomeçar
cd android_app
rm -rf .buildozer
rm -rf ~/.buildozer
buildozer android debug
```

---

## Comandos Úteis

```bash
# Executar testes unitários
python -m pytest tests/ -v

# Verificar sintaxe Python
python -m py_compile android_app/main.py

# Limpar cache Python
find . -type d -name __pycache__ -exec rm -rf {} +

# Ver tamanho do APK
ls -lh android_app/bin/*.apk

# Desinstalar app do dispositivo
adb uninstall com.pokemon.tcgmeta

# Capturar screenshot do dispositivo
adb exec-out screencap -p > screenshot.png
```

---

## Próximos Passos

Após a instalação bem-sucedida:

1. **Importe seu primeiro deck** - Use a tela Import com texto do TCG Live
2. **Explore os meta decks** - Veja os top 8 decks competitivos
3. **Compare matchups** - Analise vantagens e desvantagens
4. **Configure idioma** - Escolha entre Português e Inglês

---

*Documento atualizado em 2026-02-02*
*Versão: 2.0.0*
*Autor: Bruno Strumendo*
