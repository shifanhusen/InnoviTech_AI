# Project Structure

Complete overview of the AI Assistant project structure and file organization.

## Directory Tree

```
ai-assistant/
├── .github/                        # GitHub configuration
│   ├── workflows/
│   │   └── docker-build-push.yml   # CI/CD pipeline for Docker images
│   └── GITHUB_SECRETS.md           # Guide for configuring GitHub Secrets
│
├── backend/                        # FastAPI backend application
│   ├── app/
│   │   ├── api/                    # API endpoints
│   │   │   ├── routes_chat.py      # Chat endpoints (/chat, /reset, /session)
│   │   │   └── routes_health.py    # Health check endpoint
│   │   │
│   │   ├── core/                   # Core configurations
│   │   │   ├── config.py           # Environment-based settings
│   │   │   └── redis_client.py     # Redis connection management
│   │   │
│   │   ├── models/                 # Data models
│   │   │   └── request_models.py   # Pydantic request/response models
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── memory_service.py   # Redis conversation memory management
│   │   │   ├── ollama_service.py   # Ollama API integration
│   │   │   └── scrape_service.py   # Web scraping with BeautifulSoup
│   │   │
│   │   ├── utils/                  # Utilities
│   │   │   ├── logger.py           # Logging configuration
│   │   │   └── prompt_builder.py   # AI prompt construction
│   │   │
│   │   └── main.py                 # FastAPI app entry point
│   │
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend Docker image definition
│   ├── .env.example                # Environment variables template
│   └── .env                        # Environment variables (gitignored)
│
├── frontend/                       # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   └── Chat.tsx            # Main chat component
│   │   │
│   │   ├── styles/
│   │   │   └── main.css            # Global styles (dark theme)
│   │   │
│   │   ├── App.tsx                 # Root component
│   │   ├── main.tsx                # Application entry point
│   │   └── vite-env.d.ts           # TypeScript environment definitions
│   │
│   ├── package.json                # Node dependencies
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tsconfig.node.json          # TypeScript config for Node
│   ├── vite.config.ts              # Vite build tool configuration
│   ├── index.html                  # HTML entry point
│   ├── Dockerfile                  # Frontend Docker image (multi-stage)
│   ├── .env.example                # Environment variables template
│   ├── .env                        # Environment variables (gitignored)
│   └── .gitignore                  # Frontend-specific gitignore
│
├── nginx/                          # Nginx reverse proxy configuration
│   ├── nginx.conf                  # Main Nginx configuration
│   └── conf.d/
│       ├── default.conf            # HTTP configuration
│       └── ssl.conf.example        # HTTPS configuration template
│
├── scripts/                        # Deployment and setup scripts
│   ├── setup.sh                    # Initial setup script
│   └── setup-ssl.sh                # SSL certificate setup script
│
├── docker-compose.yml              # Multi-container orchestration
├── Makefile                        # Convenient command shortcuts
│
├── README.md                       # Main project documentation
├── QUICKSTART.md                   # Quick start guide
├── DEPLOYMENT.md                   # Detailed deployment guide
├── INTEGRATIONS.md                 # API integration examples
├── LICENSE                         # MIT License
└── .gitignore                      # Git ignore rules
```

## Component Descriptions

### Backend (`/backend`)

**Purpose**: FastAPI REST API server that handles chat requests, manages conversation memory, integrates with Ollama for AI inference, and provides web scraping capabilities.

**Key Files**:
- `main.py`: FastAPI application initialization, CORS setup, router registration
- `api/routes_chat.py`: Core chat endpoints with session management
- `services/memory_service.py`: Redis-based conversation history with TTL
- `services/ollama_service.py`: HTTP client for Ollama API
- `services/scrape_service.py`: BeautifulSoup-based web scraping
- `core/config.py`: Centralized configuration using Pydantic Settings

**Port**: 5001 (required)

**Dependencies**:
- FastAPI, Uvicorn (web framework)
- Redis (session storage)
- Requests, BeautifulSoup4 (web scraping)
- Pydantic (data validation)

### Frontend (`/frontend`)

**Purpose**: React-based chat interface with TypeScript, providing a modern, responsive UI for interacting with the AI assistant.

**Key Files**:
- `src/components/Chat.tsx`: Main chat component with message handling, session management, and scraping UI
- `src/styles/main.css`: Dark-themed, responsive CSS
- `vite.config.ts`: Vite build configuration

**Port**: 3000 (dev), built to static files for production

**Features**:
- Real-time chat interface
- Session persistence in localStorage
- Optional web scraping toggle
- Mobile-responsive design
- Typing indicators

### Nginx (`/nginx`)

**Purpose**: Reverse proxy that serves the React frontend and proxies API requests to the backend, with SSL/TLS support.

**Key Files**:
- `nginx.conf`: Main Nginx configuration with gzip, logging
- `conf.d/default.conf`: HTTP server block for development
- `conf.d/ssl.conf.example`: HTTPS server block template for production

**Configuration**:
- Serves static React files from `/usr/share/nginx/html`
- Proxies `/api/*` requests to `backend:5001`
- Handles SSL/TLS termination
- HTTP to HTTPS redirect (in production)

### Infrastructure

**Docker Compose Services**:

1. **redis** (redis:alpine)
   - Port: 6379
   - Volume: redis_data
   - Purpose: Session storage with TTL

2. **ollama** (ollama/ollama:latest)
   - Port: 11434
   - Volume: ollama_data
   - Purpose: LLaMA 3.1 8B model inference

3. **backend** (custom build)
   - Port: 5001
   - Depends on: redis, ollama
   - Purpose: FastAPI application

4. **frontend** (custom build)
   - Built to static files
   - Purpose: React application

5. **nginx** (nginx:alpine)
   - Ports: 80, 443
   - Depends on: backend, frontend
   - Purpose: Reverse proxy and static file server

### Scripts (`/scripts`)

**setup.sh**:
- Initial VPS setup
- Creates directories
- Copies environment templates
- Builds Docker images

**setup-ssl.sh**:
- Installs Certbot
- Obtains Let's Encrypt certificates
- Configures Nginx for HTTPS
- Sets up auto-renewal

### CI/CD (`.github/workflows`)

**docker-build-push.yml**:
- Triggers on push to main or manual dispatch
- Builds Docker images for backend, frontend, nginx
- Tags with `latest` and git SHA
- Pushes to Docker Hub or GitHub Container Registry
- Provides deployment summary

### Documentation

**README.md**: Comprehensive project documentation
- Architecture overview
- Installation guide
- Configuration reference
- API documentation
- Deployment instructions
- Troubleshooting

**QUICKSTART.md**: 5-minute setup guide
- Minimal steps to get running
- Common issues and fixes
- Essential commands

**DEPLOYMENT.md**: Production deployment guide
- VPS setup
- Docker installation
- HTTPS configuration
- Monitoring and maintenance
- Backup and recovery

**INTEGRATIONS.md**: API integration examples
- Python, JavaScript, PHP, Dart, Go, Ruby examples
- Error handling patterns
- Rate limiting strategies

## Data Flow

### Chat Request Flow

```
User Browser
    │
    ├─> POST /api/llm/chat
    │
    ▼
Nginx (port 80/443)
    │
    ├─> Proxy to backend:5001
    │
    ▼
FastAPI Backend
    │
    ├─> 1. Get conversation history from Redis
    │   └─> Redis (port 6379)
    │
    ├─> 2. Optional: Scrape URL
    │   └─> BeautifulSoup → External Website
    │
    ├─> 3. Build prompt with history + scraped content
    │
    ├─> 4. Send to Ollama
    │   └─> POST http://ollama:11434/api/generate
    │       └─> Ollama processes with LLaMA 3.1
    │
    ├─> 5. Save user + assistant messages to Redis
    │   └─> Redis (with 10min TTL)
    │
    └─> 6. Return response to client
        └─> {"reply": "...", "session_expired": false}
```

### Session Management Flow

```
New Chat
    │
    ├─> Generate session_id (client-side)
    │   └─> Stored in localStorage
    │
    ▼
First Message
    │
    ├─> Redis: No session found (new conversation)
    ├─> Create new Redis key: session:{id}
    └─> Set TTL: 600 seconds (10 minutes)
    │
    ▼
Subsequent Messages
    │
    ├─> Redis: Session exists
    ├─> Append new messages
    ├─> Keep last 20 messages
    └─> Refresh TTL: 600 seconds
    │
    ▼
After 10 Minutes of Inactivity
    │
    └─> Redis: Key expires automatically
        └─> Next message starts fresh session
```

## Environment Variables

### Backend (backend/.env)

| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server bind address |
| PORT | 5001 | Server port (must be 5001) |
| REDIS_HOST | redis | Redis hostname |
| REDIS_PORT | 6379 | Redis port |
| REDIS_DB | 0 | Redis database number |
| OLLAMA_BASE_URL | http://ollama:11434 | Ollama API endpoint |
| OLLAMA_MODEL | llama3.1:8b | Model name |
| OLLAMA_TIMEOUT | 120 | Request timeout (seconds) |
| SESSION_TTL_SECONDS | 600 | Session expiry time |
| MAX_HISTORY_MESSAGES | 20 | Max messages per session |
| SCRAPE_TIMEOUT | 10 | Web scraping timeout |
| SCRAPE_MAX_CHARS | 5000 | Max scraped content length |
| CORS_ORIGINS | * | Allowed CORS origins |

### Frontend (frontend/.env)

| Variable | Default | Description |
|----------|---------|-------------|
| VITE_API_BASE_URL | http://localhost:5001 | Backend API URL |

## Ports Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Nginx | 80 | HTTP | Main web access |
| Nginx | 443 | HTTPS | Secure web access |
| Backend | 5001 | HTTP | API endpoints |
| Redis | 6379 | TCP | Session storage |
| Ollama | 11434 | HTTP | AI model inference |
| Frontend Dev | 3000 | HTTP | Development server |

## Volume Mounts

| Volume Name | Mount Point | Purpose |
|-------------|-------------|---------|
| redis_data | /data | Redis persistence |
| ollama_data | /root/.ollama | Ollama models storage |
| nginx_conf | /etc/nginx | Nginx configuration |
| nginx_html | /usr/share/nginx/html | Static frontend files |
| certbot_conf | /etc/letsencrypt | SSL certificates |
| certbot_www | /var/www/certbot | ACME challenge |

## Network Architecture

```
┌─────────────────────────────────────────┐
│         Internet / Users                │
└──────────────┬──────────────────────────┘
               │ HTTPS/HTTP
┌──────────────▼──────────────────────────┐
│         VPS Public IP                   │
│  ┌──────────────────────────────────┐   │
│  │    Firewall (UFW)                │   │
│  │  - Allow: 22, 80, 443            │   │
│  └──────────┬───────────────────────┘   │
│             │                            │
│  ┌──────────▼───────────────────────┐   │
│  │   Docker Bridge Network          │   │
│  │   (ai-assistant-network)         │   │
│  │                                  │   │
│  │  ┌─────────┐  ┌────────────┐    │   │
│  │  │ Nginx   │  │  Backend   │    │   │
│  │  │  :80    │  │   :5001    │    │   │
│  │  │  :443   │  └─────┬──────┘    │   │
│  │  └─────┬───┘        │            │   │
│  │        │            │            │   │
│  │        │   ┌────────▼──────┐    │   │
│  │        │   │  Redis :6379  │    │   │
│  │        │   └───────────────┘    │   │
│  │        │                        │   │
│  │        │   ┌─────────────────┐  │   │
│  │        └───► Frontend (static)│  │   │
│  │            └─────────────────┘  │   │
│  │                                 │   │
│  │            ┌─────────────────┐  │   │
│  │            │ Ollama :11434   │  │   │
│  │            └─────────────────┘  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Build Process

### Backend Build
1. Base: python:3.11-slim
2. Install system dependencies
3. Install Python packages from requirements.txt
4. Copy application code
5. Create non-root user
6. Expose port 5001
7. Run uvicorn

### Frontend Build (Multi-stage)
1. **Stage 1 (Build)**:
   - Base: node:20-alpine
   - Install npm dependencies
   - Run `npm run build` (creates `/dist`)

2. **Stage 2 (Serve)**:
   - Base: nginx:alpine
   - Copy built files from stage 1
   - Configure nginx
   - Expose port 80

### CI/CD Build
1. Checkout code
2. Set up Docker Buildx
3. Login to registry
4. Extract metadata (tags, labels)
5. Build multi-arch images
6. Push to registry
7. Clean up

## Security Considerations

**Backend**:
- Non-root user in Docker
- Environment-based secrets
- Input validation with Pydantic
- CORS configuration
- Request timeouts

**Frontend**:
- Static file serving
- CSP headers (Content Security Policy)
- XSS protection headers

**Infrastructure**:
- Firewall (UFW) blocking unused ports
- SSL/TLS encryption
- Security headers in Nginx
- Container isolation
- Regular security updates

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|-----------|
| Frontend | Vite dev server (hot reload) | Static files via Nginx |
| Backend | Local Python (--reload) | Docker container |
| Database | Local Redis | Docker Redis with persistence |
| SSL | None (HTTP only) | Let's Encrypt certificates |
| Logging | DEBUG level | INFO level |
| CORS | Permissive (*) | Restricted to domain |
| Builds | Manual | CI/CD automated |

---

This structure ensures:
- ✅ Clear separation of concerns
- ✅ Easy local development
- ✅ Production-ready deployment
- ✅ Scalable architecture
- ✅ Maintainable codebase
