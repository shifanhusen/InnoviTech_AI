# System Architecture Diagrams

Visual representations of the AI Assistant system architecture.

## 1. High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              React Frontend (Chat UI)                    │   │
│  │  • Session Management (localStorage)                     │   │
│  │  • Message Display & Input                               │   │
│  │  • Web Scraping Toggle                                   │   │
│  └──────────────────┬───────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────┘
                      │ HTTPS (443) or HTTP (80)
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Nginx Reverse Proxy                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • Serves static React files (/)                         │   │
│  │  • Proxies API requests (/api/* → backend:5001)         │   │
│  │  • SSL/TLS termination                                   │   │
│  │  • Gzip compression                                      │   │
│  │  • Security headers                                      │   │
│  └──────────────────┬───────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
┌────────▼──────────┐    ┌─────────▼─────────────────────────────┐
│  Static Files     │    │      FastAPI Backend (5001)           │
│  (React Build)    │    │  ┌─────────────────────────────────┐  │
└───────────────────┘    │  │  API Routes                      │  │
                         │  │  • POST /api/llm/chat           │  │
                         │  │  • POST /api/llm/reset          │  │
                         │  │  • GET /api/llm/session/{id}    │  │
                         │  │  • GET /api/health              │  │
                         │  └─────────────┬───────────────────┘  │
                         │                │                       │
                         │  ┌─────────────▼───────────────────┐  │
                         │  │  Services Layer                  │  │
                         │  │  • Memory Service (Redis)        │  │
                         │  │  • Ollama Service (AI)          │  │
                         │  │  • Scrape Service (Web)         │  │
                         │  └──────┬──────────┬────────┬──────┘  │
                         └─────────┼──────────┼────────┼─────────┘
                                   │          │        │
                    ┌──────────────┘          │        └─────────────────┐
                    │                         │                          │
         ┌──────────▼───────────┐  ┌──────────▼──────────┐  ┌───────────▼────────┐
         │   Redis (6379)       │  │  Ollama (11434)     │  │  External Website  │
         │  ┌────────────────┐  │  │  ┌──────────────┐   │  │  (for scraping)    │
         │  │ Session Store  │  │  │  │ LLaMA 3.1 8B │   │  │                    │
         │  │ • Key: session │  │  │  │ Model        │   │  │                    │
         │  │ • TTL: 10 min  │  │  │  │ Inference    │   │  │                    │
         │  │ • Max: 20 msgs │  │  │  └──────────────┘   │  │                    │
         │  └────────────────┘  │  └─────────────────────┘  └────────────────────┘
         └──────────────────────┘
```

## 2. Request Flow Diagram

### Chat Request Flow

```
User → Frontend → Nginx → Backend → Services → External Systems
  1       2        3        4          5              6

1. User Types Message
   ├─> Input: "What is machine learning?"
   └─> Optional: Enable scraping + URL

2. Frontend Sends Request
   ├─> POST /api/llm/chat
   ├─> Headers: Content-Type: application/json
   └─> Body: {
         "session_id": "abc123",
         "message": "What is ML?",
         "use_scrape": false
       }

3. Nginx Processes Request
   ├─> Receives on port 80/443
   ├─> Applies security headers
   ├─> Proxies to backend:5001/api/llm/chat
   └─> Forwards headers

4. Backend API Handler
   ├─> FastAPI receives request
   ├─> Validates with Pydantic
   ├─> Extracts session_id, message
   └─> Calls services

5. Services Processing
   
   5a. Memory Service (Redis)
       ├─> GET session:abc123
       ├─> Retrieve conversation history
       └─> Returns list of messages
   
   5b. Scrape Service (if enabled)
       ├─> Validate URL
       ├─> HTTP GET request
       ├─> Parse HTML (BeautifulSoup)
       ├─> Extract & clean text
       └─> Return content (max 5000 chars)
   
   5c. Prompt Builder
       ├─> System instruction
       ├─> Scraped content (if any)
       ├─> Conversation history
       ├─> Current user message
       └─> Build complete prompt
   
   5d. Ollama Service
       ├─> POST http://ollama:11434/api/generate
       ├─> Body: {
             "model": "llama3.1:8b",
             "prompt": "...",
             "stream": false
           }
       ├─> Wait for response (timeout: 120s)
       └─> Extract generated text
   
   5e. Memory Service (Save)
       ├─> Append user message
       ├─> Append assistant reply
       ├─> Keep last 20 messages
       ├─> SET session:abc123
       └─> EXPIRE 600 seconds

6. Response Flow
   Backend → Nginx → Frontend → User
   
   ├─> Backend returns:
   │   {
   │     "reply": "Machine learning is...",
   │     "session_expired": false
   │   }
   │
   ├─> Nginx forwards response
   │
   ├─> Frontend receives & displays
   │   ├─> Append to message list
   │   ├─> Scroll to bottom
   │   └─> Enable input
   │
   └─> User sees AI response
```

## 3. Data Flow Diagram

### Session Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      NEW USER SESSION                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │  Generate Session ID         │
           │  "session_" + timestamp + id │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │  Store in localStorage       │
           │  Key: ai_assistant_session_id│
           └──────────────┬───────────────┘
                          │
    ┌─────────────────────┴─────────────────────┐
    │                                            │
    ▼                                            ▼
┌─────────────────┐                   ┌──────────────────┐
│ FIRST MESSAGE   │                   │ SESSION TRACKING │
└────────┬────────┘                   └─────────┬────────┘
         │                                      │
         ▼                                      │
┌────────────────────────┐                     │
│ Redis: Key Not Found   │                     │
│ (New Conversation)     │                     │
└────────┬───────────────┘                     │
         │                                      │
         ▼                                      │
┌────────────────────────────────┐             │
│ Create Redis Entry             │             │
│ Key: session:{id}              │             │
│ Value: [                       │             │
│   {role: "user", content: ...},│             │
│   {role: "assistant", ...}     │◄────────────┤
│ ]                              │             │
│ TTL: 600 seconds (10 min)     │             │
└────────┬───────────────────────┘             │
         │                                      │
         │                                      │
    ┌────┴────────────────────────┐            │
    │                              │            │
    ▼                              ▼            ▼
┌─────────────────┐    ┌────────────────────────────────┐
│SUBSEQUENT MSGS  │    │    CONTINUOUS ACTIVITY         │
│ (Within 10 min) │    │                                │
└────────┬────────┘    │  Each message:                 │
         │             │  • Appends to history          │
         ▼             │  • Trims to last 20            │
┌──────────────────┐   │  • Refreshes TTL to 600s      │
│ Redis: Key Found │   │                                │
│ Load History     │   └────────────────────────────────┘
└────────┬─────────┘                  │
         │                            │
         ▼                            │
┌──────────────────────┐              │
│ Append New Messages  │              │
│ • User message       │              │
│ • AI response        │              │
└────────┬─────────────┘              │
         │                            │
         ▼                            │
┌──────────────────────┐              │
│ Keep Last 20 Only    │              │
│ (FIFO)               │              │
└────────┬─────────────┘              │
         │                            │
         ▼                            │
┌──────────────────────┐              │
│ Update Redis         │              │
│ SET session:{id}     │◄─────────────┘
│ EXPIRE 600           │
└──────────────────────┘
         │
         │
   (After 10 min inactivity)
         │
         ▼
┌──────────────────────┐
│ REDIS TTL EXPIRES    │
│ Key automatically    │
│ deleted              │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Next message:        │
│ Fresh conversation   │
│ (No history)         │
└──────────────────────┘
```

## 4. Docker Container Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                         Docker Host (VPS)                          │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           Docker Bridge Network                              │ │
│  │           (ai-assistant-network)                             │ │
│  │                                                              │ │
│  │  ┌────────────────┐    ┌─────────────────┐                 │ │
│  │  │  Nginx         │    │   Backend       │                 │ │
│  │  │  Container     │    │   Container     │                 │ │
│  │  │                │    │                 │                 │ │
│  │  │  Image:        │    │   Image: Custom │                 │ │
│  │  │  nginx:alpine  │    │   Base: python  │                 │ │
│  │  │                │    │   :3.11-slim    │                 │ │
│  │  │  Ports:        │    │                 │                 │ │
│  │  │  • 80:80       │    │   Port: 5001    │                 │ │
│  │  │  • 443:443     │    │                 │                 │ │
│  │  │                │    │   Health:       │                 │ │
│  │  │  Volumes:      │    │   /api/health   │                 │ │
│  │  │  • Static files│    │                 │                 │ │
│  │  │  • Config      │◄───┤   Depends:      │                 │ │
│  │  │  • SSL certs   │    │   • Redis       │                 │ │
│  │  └────────┬───────┘    │   • Ollama      │                 │ │
│  │           │            └────────┬────────┘                 │ │
│  │           │                     │                          │ │
│  │           │                     │                          │ │
│  │           │         ┌───────────┴──────────────┐           │ │
│  │           │         │                          │           │ │
│  │           │   ┌─────▼─────┐          ┌─────────▼──────┐   │ │
│  │           │   │  Redis    │          │    Ollama      │   │ │
│  │           │   │  Container│          │    Container   │   │ │
│  │           │   │           │          │                │   │ │
│  │           │   │  Image:   │          │   Image:       │   │ │
│  │           │   │  redis:   │          │   ollama/      │   │ │
│  │           │   │  alpine   │          │   ollama       │   │ │
│  │           │   │           │          │                │   │ │
│  │           │   │  Port:    │          │   Port: 11434  │   │ │
│  │           │   │  6379     │          │                │   │ │
│  │           │   │           │          │   Model:       │   │ │
│  │           │   │  Volume:  │          │   LLaMA 3.1 8B │   │ │
│  │           │   │  redis_   │          │                │   │ │
│  │           │   │  data     │          │   Volume:      │   │ │
│  │           │   │           │          │   ollama_data  │   │ │
│  │           │   │  Health:  │          │                │   │ │
│  │           │   │  PING     │          │   Health:      │   │ │
│  │           │   └───────────┘          │   /api/tags    │   │ │
│  │           │                          └────────────────┘   │ │
│  │           │                                               │ │
│  │           │   ┌──────────────────────────────┐            │ │
│  │           └───►  Frontend (Build Artifacts)  │            │ │
│  │               │  Copied into Nginx           │            │ │
│  │               └──────────────────────────────┘            │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Host Volumes                           │   │
│  │  • redis_data         (persistent Redis data)            │   │
│  │  • ollama_data        (LLaMA model files ~4.7GB)         │   │
│  │  • certbot/conf       (SSL certificates)                 │   │
│  │  • certbot/www        (ACME challenges)                  │   │
│  │  • nginx/conf.d       (Nginx configs)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
         │
         │ Host Network
         ▼
    Internet
```

## 5. CI/CD Pipeline Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      Developer                                  │
│  • Writes code                                                 │
│  • Commits to Git                                              │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Git Push to main                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                GitHub Actions Triggered                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌────────────────────┐          ┌─────────────────────┐
│ Build Backend Job  │          │ Build Frontend Job  │
│                    │          │                     │
│ 1. Checkout code   │          │ 1. Checkout code    │
│ 2. Setup Buildx    │          │ 2. Setup Buildx     │
│ 3. Login to        │          │ 3. Login to registry│
│    Docker Hub      │          │ 4. Build image:     │
│ 4. Build image:    │          │    • Stage 1: npm   │
│    • python:3.11   │          │      build          │
│    • Install deps  │          │    • Stage 2: nginx │
│    • Copy app      │          │      with static    │
│ 5. Tag:            │          │ 5. Tag:             │
│    • latest        │          │    • latest         │
│    • git-sha       │          │    • git-sha        │
│ 6. Push to hub     │          │ 6. Push to hub      │
└────────┬───────────┘          └──────────┬──────────┘
         │                                  │
         └──────────────┬───────────────────┘
                        │
                        ▼
         ┌──────────────────────────┐
         │  Build Nginx Job         │
         │  (with frontend assets)  │
         │                          │
         │  1. Build frontend       │
         │  2. Copy to nginx        │
         │  3. Add configs          │
         │  4. Build & push         │
         └──────────┬───────────────┘
                    │
                    ▼
         ┌──────────────────────────┐
         │  All Jobs Complete       │
         │                          │
         │  Summary Generated:      │
         │  • Image names & tags    │
         │  • Deploy commands       │
         │  • Links to images       │
         └──────────┬───────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Docker Hub / GHCR                              │
│                                                                 │
│  Images Available:                                              │
│  • username/ai-assistant-backend:latest                        │
│  • username/ai-assistant-frontend:latest                       │
│  • username/ai-assistant-nginx:latest                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Manual Step
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Production VPS                             │
│                                                                 │
│  $ docker compose pull                                          │
│  $ docker compose up -d                                         │
│                                                                 │
│  → Pulls latest images                                          │
│  → Recreates containers                                         │
│  → Application updated!                                         │
└─────────────────────────────────────────────────────────────────┘
```

## 6. Security Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      Security Layers                            │
└────────────────────────────────────────────────────────────────┘

Layer 1: Network Security
┌─────────────────────────────────────────┐
│          Firewall (UFW)                 │
│  • Allow: 22 (SSH)                      │
│  • Allow: 80 (HTTP)                     │
│  • Allow: 443 (HTTPS)                   │
│  • Deny: All other ports                │
└─────────────────┬───────────────────────┘
                  │
Layer 2: SSL/TLS
┌─────────────────▼───────────────────────┐
│       Let's Encrypt Certificates        │
│  • TLS 1.2 & 1.3                        │
│  • Strong ciphers                       │
│  • HSTS enabled                         │
│  • Auto-renewal                         │
└─────────────────┬───────────────────────┘
                  │
Layer 3: Nginx Security Headers
┌─────────────────▼───────────────────────┐
│  • X-Frame-Options: SAMEORIGIN          │
│  • X-Content-Type-Options: nosniff      │
│  • X-XSS-Protection: 1; mode=block      │
│  • CSP: Content Security Policy         │
│  • Referrer-Policy                      │
└─────────────────┬───────────────────────┘
                  │
Layer 4: Application Security
┌─────────────────▼───────────────────────┐
│       FastAPI Backend                   │
│  • CORS: Configured origins             │
│  • Pydantic: Input validation           │
│  • Timeouts: Request limits             │
│  • Error handling: No stack traces      │
└─────────────────┬───────────────────────┘
                  │
Layer 5: Container Security
┌─────────────────▼───────────────────────┐
│       Docker Isolation                  │
│  • Non-root users                       │
│  • Network isolation                    │
│  • Resource limits                      │
│  • Read-only filesystems (where possible)│
└─────────────────┬───────────────────────┘
                  │
Layer 6: Data Security
┌─────────────────▼───────────────────────┐
│         Redis & Secrets                 │
│  • Environment variables (not hardcoded)│
│  • Redis password (if needed)           │
│  • Session isolation                    │
│  • TTL-based cleanup                    │
└─────────────────────────────────────────┘
```

---

These diagrams provide visual understanding of:
1. Overall system architecture
2. Request/response flow
3. Session & data management
4. Container orchestration
5. CI/CD pipeline
6. Security layers

Refer to these when:
- Understanding system design
- Debugging issues
- Planning modifications
- Explaining to team members
- Documentation purposes
