# DEPLOY.md - Guia de Implantação TCG Tool v3.0

**Autor:** Bruno Strumendo
**Última Atualização:** 2026-02-15

---

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Início Rápido com Docker](#início-rápido-com-docker)
3. [Configuração Manual (Desenvolvimento)](#configuração-manual-desenvolvimento)
4. [Variáveis de Ambiente](#variáveis-de-ambiente)
5. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
6. [Tarefas de Sincronização de Dados](#tarefas-de-sincronização-de-dados)
7. [Serviços Docker Compose](#serviços-docker-compose)
8. [Implantação em Produção](#implantação-em-produção)
9. [Resolução de Problemas](#resolução-de-problemas)

---

## Pré-requisitos

Antes de implantar o TCG Tool v3.0, certifique-se de ter o seguinte instalado:

| Componente | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.10+ | API Backend (FastAPI) |
| **Node.js** | 18+ | Frontend (Next.js) |
| **PostgreSQL** | 16 | Banco de dados principal |
| **Redis** | 7 | Camada de cache |
| **Docker** | 24+ | Containerização (recomendado) |
| **Docker Compose** | 2.20+ | Orquestração multi-container |

### Ferramentas Opcionais

- **Git** - Para controle de versão
- **Make** - Para scripts de automação
- **Nginx** - Para proxy reverso em produção
- **Certbot** - Para certificados SSL/TLS

---

## Início Rápido com Docker

A maneira mais rápida de executar o TCG Tool é usando Docker Compose.

### 1. Clonar o Repositório

```bash
git clone https://github.com/strumendo/tcg-tool.git
cd tcg_tool
```

### 2. Configurar Ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas chaves de API e configuração:

```env
# Obrigatório
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Opcional
POKEMONTCG_API_KEY=your_pokemon_tcg_api_key_here
```

### 3. Iniciar Serviços

```bash
docker-compose up -d
```

Isto iniciará todos os serviços em segundo plano:
- **API Backend**: http://localhost:8000
- **UI Frontend**: http://localhost:3000
- **Docs da API**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Inicializar Banco de Dados

```bash
# Executar migrações
docker-compose exec backend alembic upgrade head

# Seed de dados iniciais (decks meta, sets)
docker-compose exec backend python -m app.db.seed
```

### 5. Sincronizar Dados Externos (Opcional)

```bash
# Sincronizar dados de cartas do TCGdex
docker-compose exec backend python -m app.tasks.sync_cards

# Sincronizar dados de torneios do Limitless
docker-compose exec backend python -m app.tasks.sync_limitless

# Sincronizar notícias do PokeBeach
docker-compose exec backend python -m app.tasks.sync_news
```

### 6. Acessar a Aplicação

- **Frontend**: http://localhost:3000
- **Documentação da API**: http://localhost:8000/docs
- **Documentação Redoc**: http://localhost:8000/redoc

---

## Configuração Manual (Desenvolvimento)

Para desenvolvimento local sem Docker, siga estes passos.

### Configuração do Backend

#### 1. Navegar para o Diretório do Backend

```bash
cd backend
```

#### 2. Criar Ambiente Virtual

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

#### 3. Instalar Dependências

```bash
pip install -e ".[dev]"
```

Isto instala o pacote backend em modo editável com dependências de desenvolvimento.

#### 4. Configurar Ambiente

Criar `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://tcgtool:tcgtool_dev@localhost:5432/tcgtool
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
POKEMONTCG_API_KEY=your_pokemon_tcg_api_key_here
TCGDEX_BASE_URL=https://api.tcgdex.net/v2
POKEMONTCG_BASE_URL=https://api.pokemontcg.io/v2
FRONTEND_URL=http://localhost:3000
DEFAULT_LANGUAGE=pt
LOG_LEVEL=INFO
```

#### 5. Iniciar PostgreSQL e Redis

**PostgreSQL:**
```bash
# Instalar PostgreSQL 16
sudo apt install postgresql-16  # Ubuntu/Debian
brew install postgresql@16      # macOS

# Iniciar serviço
sudo systemctl start postgresql  # Linux
brew services start postgresql@16  # macOS

# Criar banco de dados e usuário
sudo -u postgres psql
```

```sql
CREATE USER tcgtool WITH PASSWORD 'tcgtool_dev';
CREATE DATABASE tcgtool OWNER tcgtool;
GRANT ALL PRIVILEGES ON DATABASE tcgtool TO tcgtool;
\q
```

**Redis:**
```bash
# Instalar Redis 7
sudo apt install redis-server  # Ubuntu/Debian
brew install redis             # macOS

# Iniciar serviço
sudo systemctl start redis  # Linux
brew services start redis   # macOS
```

#### 6. Executar Migrações de Banco de Dados

```bash
alembic upgrade head
```

#### 7. Seed de Dados Iniciais

```bash
python -m app.db.seed
```

#### 8. Iniciar Servidor Backend

```bash
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em http://localhost:8000.

---

### Configuração do Frontend

#### 1. Navegar para o Diretório do Frontend

```bash
cd frontend
```

#### 2. Instalar Dependências

```bash
npm install
```

#### 3. Configurar Ambiente

Criar `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DEFAULT_LANGUAGE=pt
```

#### 4. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

O frontend estará disponível em http://localhost:3000.

---

## Variáveis de Ambiente

### Variáveis de Ambiente do Backend

Lista completa de variáveis de ambiente para `backend/.env`:

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `DATABASE_URL` | Sim | - | String de conexão PostgreSQL (asyncpg) |
| `REDIS_URL` | Sim | - | String de conexão Redis |
| `ANTHROPIC_API_KEY` | Sim | - | Chave API Claude para recursos de IA |
| `POKEMONTCG_API_KEY` | Não | - | Chave API Pokemon TCG (fallback) |
| `TCGDEX_BASE_URL` | Não | `https://api.tcgdex.net/v2` | Endpoint da API TCGdex |
| `POKEMONTCG_BASE_URL` | Não | `https://api.pokemontcg.io/v2` | Endpoint da API Pokemon TCG |
| `FRONTEND_URL` | Não | `http://localhost:3000` | Origem permitida por CORS |
| `DEFAULT_LANGUAGE` | Não | `pt` | Idioma padrão da UI (pt/en) |
| `LOG_LEVEL` | Não | `INFO` | Nível de logging (DEBUG/INFO/WARNING/ERROR) |
| `SECRET_KEY` | Sim (prod) | auto-gerado | Chave secreta JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | `30` | Expiração do token JWT |
| `API_V1_PREFIX` | Não | `/api/v1` | Prefixo de rota da API |
| `CORS_ORIGINS` | Não | `["http://localhost:3000"]` | Origens CORS permitidas |

### Variáveis de Ambiente do Frontend

Lista completa de variáveis de ambiente para `frontend/.env.local`:

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `NEXT_PUBLIC_API_URL` | Sim | - | URL base da API backend |
| `NEXT_PUBLIC_DEFAULT_LANGUAGE` | Não | `pt` | Idioma padrão da UI |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | Não | `false` | Habilitar analytics |
| `NEXT_PUBLIC_APP_VERSION` | Não | `3.0.0` | Versão do app |

---

## Configuração do Banco de Dados

### Migrações com Alembic

TCG Tool usa Alembic para migrações de banco de dados.

#### Criar uma Nova Migração

```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

#### Aplicar Migrações

```bash
alembic upgrade head
```

#### Reverter Migração

```bash
alembic downgrade -1  # Reverter uma versão
```

#### Visualizar Histórico de Migrações

```bash
alembic history
alembic current
```

### Seeding de Dados

O script de seed popula dados iniciais:

```bash
python -m app.db.seed
```

**O que é populado:**
- Decks meta (Top 8 decks competitivos)
- Card sets (série Scarlet & Violet)
- Dados de matchup (taxas de vitória entre decks meta)
- Usuários de amostra (para testes)

### Operações Manuais de Banco de Dados

```bash
# Conectar ao banco de dados
psql -U tcgtool -d tcgtool

# Backup do banco de dados
pg_dump -U tcgtool tcgtool > backup.sql

# Restore do banco de dados
psql -U tcgtool tcgtool < backup.sql
```

---

## Tarefas de Sincronização de Dados

TCG Tool sincroniza dados de APIs externas usando tarefas em background.

### Sincronizar Dados de Cartas (TCGdex)

```bash
python -m app.tasks.sync_cards
```

**O que faz:**
- Busca todas as cartas Pokemon TCG da API TCGdex
- Atualiza imagens de cartas, marcas de regulação, info de sets
- Suporta Inglês e Português
- Faz cache dos resultados no PostgreSQL

**Opções:**
```bash
python -m app.tasks.sync_cards --set sv7  # Sincronizar set específico
python -m app.tasks.sync_cards --full     # Ressincronização completa (lenta)
```

### Sincronizar Dados de Torneios (Limitless)

```bash
python -m app.tasks.sync_limitless
```

**O que faz:**
- Faz scraping de resultados de torneios do Limitless TCG
- Atualiza estatísticas de decks meta
- Popula decklists e dados de jogadores

**Agendamento:**
```bash
# Executar diariamente às 2h via cron
0 2 * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_limitless
```

### Sincronizar Calendário de Torneios (RK9)

```bash
python -m app.tasks.sync_tournaments
```

**O que faz:**
- Busca calendário oficial de torneios do RK9.gg
- Atualiza eventos futuros
- Sincroniza com calendário do dispositivo (Android)

### Sincronizar Feed de Notícias (PokeBeach)

```bash
python -m app.tasks.sync_news
```

**O que faz:**
- Faz scraping de artigos de notícias do PokeBeach
- Faz parse do feed RSS
- Armazena artigos com traduções

### Agendamento Automatizado

Use cron ou timers systemd para automatizar sincronizações:

**Exemplo de crontab:**
```cron
# Sincronizar cartas diariamente às 3h
0 3 * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_cards

# Sincronizar torneios a cada 6 horas
0 */6 * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_limitless

# Sincronizar notícias a cada hora
0 * * * * cd /path/to/tcg_tool/backend && python -m app.tasks.sync_news
```

---

## Serviços Docker Compose

O `docker-compose.yml` define todos os serviços:

### Visão Geral dos Serviços

| Serviço | Imagem | Porta | Propósito |
|---------|--------|-------|-----------|
| `db` | `postgres:16-alpine` | 5432 | Banco de dados PostgreSQL |
| `redis` | `redis:7-alpine` | 6379 | Camada de cache |
| `backend` | `./backend` | 8000 | Aplicação FastAPI |
| `frontend` | `./frontend` | 3000 | Aplicação Next.js |

### Configuração dos Serviços

**PostgreSQL (db):**
```yaml
db:
  image: postgres:16-alpine
  environment:
    POSTGRES_USER: tcgtool
    POSTGRES_PASSWORD: tcgtool_dev
    POSTGRES_DB: tcgtool
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

**Redis:**
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

**Backend:**
```yaml
backend:
  build: ./backend
  env_file: .env
  ports:
    - "8000:8000"
  depends_on:
    - db
    - redis
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```yaml
frontend:
  build: ./frontend
  env_file: .env
  ports:
    - "3000:3000"
  depends_on:
    - backend
  command: npm run dev
```

### Comandos Docker

```bash
# Iniciar todos os serviços
docker-compose up -d

# Visualizar logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Reiniciar serviço
docker-compose restart backend

# Parar todos os serviços
docker-compose down

# Remover volumes (cuidado: deleta dados)
docker-compose down -v

# Reconstruir imagens
docker-compose build --no-cache
```

---

## Implantação em Produção

### Nginx Reverse Proxy

**Instalar Nginx:**
```bash
sudo apt install nginx
```

**Configurar Nginx (`/etc/nginx/sites-available/tcgtool`):**
```nginx
server {
    listen 80;
    server_name tcgtool.example.com;

    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tcgtool.example.com;

    ssl_certificate /etc/letsencrypt/live/tcgtool.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tcgtool.example.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Docs
    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

**Habilitar site:**
```bash
sudo ln -s /etc/nginx/sites-available/tcgtool /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS com Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tcgtool.example.com
```

### Serviços Systemd

**Serviço Backend (`/etc/systemd/system/tcgtool-backend.service`):**
```ini
[Unit]
Description=TCG Tool Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=tcgtool
WorkingDirectory=/opt/tcg_tool/backend
Environment="PATH=/opt/tcg_tool/backend/.venv/bin"
ExecStart=/opt/tcg_tool/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Serviço Frontend (`/etc/systemd/system/tcgtool-frontend.service`):**
```ini
[Unit]
Description=TCG Tool Frontend
After=network.target tcgtool-backend.service

[Service]
Type=simple
User=tcgtool
WorkingDirectory=/opt/tcg_tool/frontend
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Habilitar e iniciar serviços:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tcgtool-backend tcgtool-frontend
sudo systemctl start tcgtool-backend tcgtool-frontend
sudo systemctl status tcgtool-backend
```

### Hardening de Ambiente

**Configurações `.env` de produção:**
```env
# Usar secrets fortes
SECRET_KEY=$(openssl rand -hex 32)

# Desabilitar modo debug
DEBUG=false

# Usar banco de dados de produção
DATABASE_URL=postgresql+asyncpg://tcgtool:STRONG_PASSWORD@localhost:5432/tcgtool_prod

# Restringir CORS
CORS_ORIGINS=["https://tcgtool.example.com"]

# Habilitar headers de segurança
ENABLE_SECURITY_HEADERS=true
```

**Hardening do PostgreSQL:**
```bash
# Editar /etc/postgresql/16/main/pg_hba.conf
# Mudar: host all all 0.0.0.0/0 md5
# Para: host tcgtool tcgtool 127.0.0.1/32 md5
```

**Segurança do Redis:**
```bash
# Editar /etc/redis/redis.conf
requirepass STRONG_PASSWORD
bind 127.0.0.1
```

---

## Resolução de Problemas

### Problemas Comuns

#### 1. Porta Já em Uso

**Erro:**
```
Error: bind: address already in use
```

**Solução:**
```bash
# Encontrar processo usando porta 8000
lsof -i :8000
# ou
sudo netstat -tulpn | grep 8000

# Matar processo
kill -9 <PID>
```

#### 2. Conexão com Banco de Dados Recusada

**Erro:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solução:**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar string de conexão
psql -U tcgtool -d tcgtool  # Deve conectar

# Verificar se DATABASE_URL em .env corresponde
```

#### 3. Erro de Conexão Redis

**Erro:**
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**Solução:**
```bash
# Iniciar Redis
sudo systemctl start redis

# Testar conexão
redis-cli ping  # Deve retornar PONG
```

#### 4. Limites de Taxa da API

**Erro:**
```
HTTPError: 429 Too Many Requests
```

**Solução:**
- Adicionar `POKEMONTCG_API_KEY` ao `.env` para limites maiores
- Reduzir frequência de sincronização
- Usar cache Redis (já habilitado)

#### 5. Build Docker Falha

**Erro:**
```
ERROR [backend 4/5] RUN pip install -e ".[dev]"
```

**Solução:**
```bash
# Limpar cache do Docker
docker-compose build --no-cache

# Verificar versão do Python no Dockerfile
FROM python:3.10-slim  # Deve ser 3.10+
```

#### 6. Conflitos de Migração Alembic

**Erro:**
```
alembic.util.exc.CommandError: Multiple head revisions are present
```

**Solução:**
```bash
# Merge heads
alembic merge heads -m "Merge migration heads"
alembic upgrade head
```

#### 7. Erro de Conexão da API do Frontend

**Erro:**
```
Failed to fetch: TypeError: Failed to fetch
```

**Solução:**
- Verificar `NEXT_PUBLIC_API_URL` em `.env.local`
- Verificar se backend está rodando na porta 8000
- Verificar configurações de CORS no `.env` do backend

#### 8. Problemas de Permissão de Volume Docker

**Erro:**
```
PermissionError: [Errno 13] Permission denied
```

**Solução:**
```bash
# Corrigir ownership
sudo chown -R $USER:$USER postgres_data redis_data

# Ou recriar volumes
docker-compose down -v
docker-compose up -d
```

### Modo Debug

Habilitar logging de debug:

**Backend:**
```env
LOG_LEVEL=DEBUG
```

**Frontend:**
```bash
npm run dev  # Modo de desenvolvimento inclui logs de debug
```

### Verificações de Saúde

```bash
# Saúde do backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Banco de dados
psql -U tcgtool -d tcgtool -c "SELECT version();"

# Redis
redis-cli ping
```

---

## Suporte

Para problemas não cobertos neste guia:

1. Verificar [GitHub Issues](https://github.com/strumendo/tcg-tool/issues)
2. Revisar logs: `docker-compose logs -f`
3. Contato: strumendo@gmail.com

---

**Versão do Documento:** 3.0.0
**Última Atualização:** 2026-02-15
**Autor:** Bruno Strumendo
