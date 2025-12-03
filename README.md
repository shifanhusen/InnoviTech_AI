# AI Assistant - Full Stack Application

A production-ready AI assistant system powered by LLaMA 3.1 (8B) via Ollama, with a FastAPI backend, React frontend, Redis-based conversation memory, and web scraping capabilities.

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?logo=typescript)](https://www.typescriptlang.org/)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [HTTPS Setup](#-https-setup)
- [CI/CD](#-cicd)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## ✨ Features

- **🤖 AI-Powered Chat**: Conversational AI using LLaMA 3.1 8B model via Ollama
- **💾 Session Memory**: Redis-based conversation history with 10-minute auto-expiry
- **🌐 Web Scraping**: Live information retrieval using BeautifulSoup (no paid APIs)
- **🔄 RESTful API**: Backend API consumable by any application (Flutter, PHP, etc.)
- **📱 Modern UI**: Responsive React interface with TypeScript
- **🔒 Production Ready**: Nginx reverse proxy with HTTPS support via Certbot
- **🐳 Containerized**: Full Docker orchestration with docker-compose
- **🚀 CI/CD**: GitHub Actions workflow for automated builds and deployments

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS (443) / HTTP (80)
┌───────────────────────────▼─────────────────────────────────┐
│                      Nginx (Reverse Proxy)                   │
│  - Serves React frontend (static files)                     │
│  - Proxies /api/* to FastAPI backend                        │
│  - SSL/TLS termination                                       │
└───────────┬─────────────────────────────────────────────────┘
            │
            ├──────────────────┐
            │                  │
┌───────────▼─────────┐  ┌────▼──────────────────────────────┐
│   React Frontend    │  │      FastAPI Backend (5001)       │
│   - Chat UI         │  │  - Chat endpoints                 │
│   - Session mgmt    │  │  - Memory management              │
│   - TypeScript      │  │  - Web scraping                   │
└─────────────────────┘  │  - Ollama integration             │
                         └────┬──────────────┬────────────────┘
                              │              │
                    ┌─────────▼────┐    ┌────▼─────────────┐
                    │ Redis (6379) │    │ Ollama (11434)   │
                    │ - Sessions   │    │ - LLaMA 3.1 8B   │
                    │ - History    │    │ - Inference      │
                    │ - TTL (10m)  │    │                  │
                    └──────────────┘    └──────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Redis** - Session storage with TTL
- **Ollama** - LLaMA model serving
- **BeautifulSoup4** - Web scraping
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **CSS3** - Styling (dark theme)

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy & static file serving
- **Certbot** - SSL/TLS certificates
- **GitHub Actions** - CI/CD pipeline

### AI Model
- **LLaMA 3.1 8B** - Large language model
- **Ollama** - Local model inference

## 📦 Prerequisites

- **Ubuntu 24.04 VPS** (or similar Linux distribution)
- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **4GB+ RAM** (8GB recommended for Ollama)
- **20GB+ Disk Space**
- **(Optional) Domain name** for HTTPS setup

### Installing Docker on Ubuntu 24.04

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker --version
sudo docker compose version

# Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant
```

### 2. Run Setup Script

```bash
chmod +x scripts/setup.sh
sudo bash scripts/setup.sh
```

This script will:
- Check Docker installation
- Create necessary directories
- Copy environment file templates
- Build Docker images

### 3. Configure Environment Variables

#### Backend Configuration
```bash
# Edit backend environment
nano backend/.env
```

Key variables (see `backend/.env.example` for full list):
```env
# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Session Configuration
SESSION_TTL_SECONDS=600  # 10 minutes
MAX_HISTORY_MESSAGES=20
```

#### Frontend Configuration
```bash
# Edit frontend environment
nano frontend/.env
```

```env
# API Base URL (use your domain or localhost)
VITE_API_BASE_URL=http://localhost:5001
```

### 4. Start Services

```bash
# Start all services
sudo docker compose up -d

# Check status
sudo docker compose ps

# View logs
sudo docker compose logs -f
```

### 5. Pull LLaMA Model

```bash
# This will download the LLaMA 3.1 8B model (~4.7GB)
sudo docker exec -it ai-assistant-ollama ollama pull llama3.1:8b

# Verify model is available
sudo docker exec -it ai-assistant-ollama ollama list
```

### 6. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost or http://your-vps-ip
- **API Documentation**: http://localhost/api/health
- **Backend Docs**: http://your-vps-ip:5001/docs

## ⚙️ Configuration

### Environment Variables

#### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `5001` | **Must be 5001** (required) |
| `REDIS_HOST` | `redis` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.1:8b` | Model name |
| `OLLAMA_TIMEOUT` | `120` | Request timeout (seconds) |
| `SESSION_TTL_SECONDS` | `600` | Session expiry time |
| `MAX_HISTORY_MESSAGES` | `20` | Max messages per session |
| `SCRAPE_TIMEOUT` | `10` | Web scraping timeout |
| `SCRAPE_MAX_CHARS` | `5000` | Max scraped content length |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

#### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:5001` | Backend API URL |

### Docker Compose Configuration

The `docker-compose.yml` defines five services:

1. **redis** - Session storage
2. **ollama** - LLaMA model inference
3. **backend** - FastAPI application (port 5001)
4. **frontend** - React application (built into static files)
5. **nginx** - Reverse proxy (ports 80, 443)

To customize resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Conversation Memory

Conversation history is stored in Redis with the following behavior:

- **Storage**: JSON array of message objects per session
- **TTL**: 10 minutes (configurable via `SESSION_TTL_SECONDS`)
- **Capacity**: Last 20 messages kept (configurable via `MAX_HISTORY_MESSAGES`)
- **Expiry**: Automatic cleanup after inactivity
- **Reset**: TTL refreshes on each message

Session key format: `session:{session_id}`

Message format:
```json
[
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": "Hi! How can I help?"}
]
```

### Web Scraping

The scraping service uses BeautifulSoup to extract content from URLs:

- **Library**: BeautifulSoup4 + requests
- **No External APIs**: Direct HTML scraping only
- **Timeout**: 10 seconds (configurable)
- **Max Content**: 5000 characters
- **Cleaning**: Removes scripts, styles, navigation, headers, footers
- **Error Handling**: Returns error message if scraping fails

Usage in UI:
1. Check "Use Web Scraping" checkbox
2. Enter URL to scrape
3. Send message - scraped content will be included in AI context

## 📚 API Documentation

### Base URL
```
http://your-domain/api
```

### Endpoints

#### 1. Health Check
```http
GET /api/health
```

**Response**:
```json
{
  "status": "ok"
}
```

#### 2. Send Chat Message
```http
POST /api/llm/chat
```

**Request Body**:
```json
{
  "session_id": "session_abc123",
  "message": "What is machine learning?",
  "use_scrape": false,
  "scrape_url": null
}
```

**Response**:
```json
{
  "reply": "Machine learning is a subset of artificial intelligence...",
  "session_expired": false
}
```

**With Web Scraping**:
```json
{
  "session_id": "session_abc123",
  "message": "Summarize this article",
  "use_scrape": true,
  "scrape_url": "https://example.com/article"
}
```

#### 3. Reset Session
```http
POST /api/llm/reset
```

**Request Body**:
```json
{
  "session_id": "session_abc123"
}
```

**Response**:
```json
{
  "message": "Session reset successfully",
  "session_id": "session_abc123"
}
```

#### 4. Get Session History (Debug)
```http
GET /api/llm/session/{session_id}
```

**Response**:
```json
{
  "session_id": "session_abc123",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ],
  "message_count": 2
}
```

### Integration Examples

#### Python
```python
import requests

API_URL = "http://your-domain/api/llm/chat"

response = requests.post(API_URL, json={
    "session_id": "my-session-123",
    "message": "Hello, AI!",
    "use_scrape": False
})

data = response.json()
print(data["reply"])
```

#### JavaScript/Node.js
```javascript
const response = await fetch('http://your-domain/api/llm/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    session_id: 'my-session-123',
    message: 'Hello, AI!',
    use_scrape: false
  })
});

const data = await response.json();
console.log(data.reply);
```

#### PHP
```php
<?php
$url = 'http://your-domain/api/llm/chat';
$data = [
    'session_id' => 'my-session-123',
    'message' => 'Hello, AI!',
    'use_scrape' => false
];

$options = [
    'http' => [
        'header'  => "Content-type: application/json\r\n",
        'method'  => 'POST',
        'content' => json_encode($data)
    ]
];

$context  = stream_context_create($options);
$result = file_get_contents($url, false, $context);
$response = json_decode($result);

echo $response->reply;
?>
```

#### cURL
```bash
curl -X POST http://your-domain/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my-session-123",
    "message": "Hello, AI!",
    "use_scrape": false
  }'
```

## 🌐 Deployment

### Production Deployment on VPS

1. **Update Environment Variables**

```bash
# Backend - use production values
nano backend/.env

# Frontend - use production domain
nano frontend/.env
# Set: VITE_API_BASE_URL=https://yourdomain.com
```

2. **Update Nginx Configuration**

```bash
# Edit default.conf with your domain
nano nginx/conf.d/default.conf
# Change: server_name yourdomain.com;
```

3. **Rebuild and Deploy**

```bash
# Rebuild with production configs
sudo docker compose build --no-cache

# Start services
sudo docker compose up -d

# Monitor logs
sudo docker compose logs -f backend
```

4. **Configure Firewall**

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

### Using Pre-built Images from Registry

If you've pushed images to Docker Hub via GitHub Actions:

1. **Update docker-compose.yml**:

```yaml
services:
  backend:
    image: yourusername/ai-assistant-backend:latest
    # Remove 'build' section

  frontend:
    image: yourusername/ai-assistant-frontend:latest
    # Remove 'build' section
```

2. **Pull and Run**:

```bash
sudo docker compose pull
sudo docker compose up -d
```

## 🔒 HTTPS Setup

### Automated Setup with Script

```bash
# Make script executable
chmod +x scripts/setup-ssl.sh

# Run SSL setup
sudo bash scripts/setup-ssl.sh
```

The script will:
1. Install Certbot
2. Obtain SSL certificates from Let's Encrypt
3. Update Nginx configuration for HTTPS
4. Set up automatic certificate renewal

### Manual HTTPS Setup

#### 1. Install Certbot

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

#### 2. Stop Nginx Container

```bash
sudo docker compose stop nginx
```

#### 3. Obtain Certificate

```bash
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

#### 4. Update Nginx Configuration

```bash
# Copy SSL configuration template
cp nginx/conf.d/ssl.conf.example nginx/conf.d/ssl.conf

# Edit with your domain
nano nginx/conf.d/ssl.conf
# Replace 'yourdomain.com' with your actual domain

# Optional: Disable HTTP-only config
mv nginx/conf.d/default.conf nginx/conf.d/default.conf.backup
```

#### 5. Mount Certificates in Docker Compose

Update `docker-compose.yml`:

```yaml
services:
  nginx:
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro
```

#### 6. Restart Services

```bash
sudo docker compose up -d
```

#### 7. Setup Automatic Renewal

```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'docker compose restart nginx'") | crontab -

# Test renewal
sudo certbot renew --dry-run
```

## 🔄 CI/CD

### GitHub Actions Workflow

The repository includes a GitHub Actions workflow that automatically:
- Builds Docker images for backend, frontend, and nginx
- Pushes images to Docker Hub (or GitHub Container Registry)
- Tags images with `latest` and commit SHA

### Setup Instructions

1. **Configure GitHub Secrets**

Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub password/token
- `DOCKER_REPO_BACKEND` - e.g., `username/ai-assistant-backend`
- `DOCKER_REPO_FRONTEND` - e.g., `username/ai-assistant-frontend`
- `DOCKER_REPO_NGINX` - e.g., `username/ai-assistant-nginx`
- `VITE_API_BASE_URL` - Production API URL (optional)

See [.github/GITHUB_SECRETS.md](.github/GITHUB_SECRETS.md) for detailed instructions.

2. **Trigger Workflow**

The workflow runs automatically on:
- Push to `main` branch
- Manual trigger via Actions tab

3. **Deploy Updated Images**

On your VPS:
```bash
# Pull latest images
sudo docker compose pull

# Restart services
sudo docker compose up -d

# Verify deployment
sudo docker compose ps
```

### Using GitHub Container Registry (GHCR)

To use GHCR instead of Docker Hub:

1. No secrets needed (uses automatic `GITHUB_TOKEN`)
2. Edit `.github/workflows/docker-build-push.yml`:
   - Uncomment GHCR login step
   - Comment out Docker Hub login
   - Change image names to `ghcr.io/...`

## 💻 Development

### Local Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 5001
```

Access:
- API: http://localhost:5001
- Interactive docs: http://localhost:5001/docs
- Alternative docs: http://localhost:5001/redoc

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Access: http://localhost:3000

#### Redis (for local development)

```bash
# Run Redis in Docker
docker run -d -p 6379:6379 redis:alpine

# Or install locally
sudo apt-get install redis-server
sudo systemctl start redis
```

#### Ollama (for local development)

```bash
# Option 1: Docker
docker run -d -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama3.1:8b

# Option 2: Native install (Linux)
curl https://ollama.ai/install.sh | sh
ollama serve  # Start server
ollama pull llama3.1:8b  # Download model
```

### Project Structure

```
ai-assistant/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application entry point
│   │   ├── api/             # API routes
│   │   │   ├── routes_chat.py
│   │   │   └── routes_health.py
│   │   ├── core/            # Core configurations
│   │   │   ├── config.py
│   │   │   └── redis_client.py
│   │   ├── models/          # Pydantic models
│   │   │   └── request_models.py
│   │   ├── services/        # Business logic
│   │   │   ├── memory_service.py
│   │   │   ├── ollama_service.py
│   │   │   └── scrape_service.py
│   │   └── utils/           # Utilities
│   │       ├── logger.py
│   │       └── prompt_builder.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/                # React frontend
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   └── Chat.tsx
│   │   └── styles/
│   │       └── main.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env
├── nginx/                   # Nginx configuration
│   ├── nginx.conf
│   └── conf.d/
│       ├── default.conf
│       └── ssl.conf.example
├── scripts/                 # Deployment scripts
│   ├── setup.sh
│   └── setup-ssl.sh
├── .github/                 # CI/CD
│   └── workflows/
│       └── docker-build-push.yml
├── docker-compose.yml
└── README.md
```

### Code Style

#### Python (Backend)
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Format with Black (optional)

```bash
# Install dev dependencies
pip install black flake8 mypy

# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

#### TypeScript (Frontend)
- Follow ESLint rules
- Use TypeScript strict mode
- Component organization: logic → render

```bash
# Lint
npm run lint

# Format (if Prettier is set up)
npm run format
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed

**Symptom**: `Failed to connect to Ollama at http://ollama:11434`

**Solutions**:
```bash
# Check if Ollama container is running
sudo docker compose ps ollama

# Check Ollama logs
sudo docker compose logs ollama

# Restart Ollama
sudo docker compose restart ollama

# Verify Ollama is responding
curl http://localhost:11434/api/tags
```

#### 2. Model Not Found

**Symptom**: `Model llama3.1:8b not found`

**Solution**:
```bash
# Pull the model
sudo docker exec -it ai-assistant-ollama ollama pull llama3.1:8b

# List available models
sudo docker exec -it ai-assistant-ollama ollama list
```

#### 3. Redis Connection Error

**Symptom**: `Failed to connect to Redis`

**Solutions**:
```bash
# Check Redis container
sudo docker compose ps redis

# Test Redis connection
sudo docker exec -it ai-assistant-redis redis-cli ping
# Should return: PONG

# Check Redis logs
sudo docker compose logs redis

# Restart Redis
sudo docker compose restart redis
```

#### 4. Frontend Can't Reach Backend

**Symptom**: Network error in browser console

**Solutions**:
```bash
# Check backend is running
curl http://localhost:5001/api/health

# Verify CORS settings in backend/.env
# Should allow your frontend origin

# Check nginx proxy configuration
sudo docker compose logs nginx

# Restart all services
sudo docker compose restart
```

#### 5. Out of Memory

**Symptom**: Ollama crashes or very slow responses

**Solutions**:
```bash
# Check memory usage
free -h

# Check Docker container memory
sudo docker stats

# Increase swap (if needed)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add to /etc/fstab for persistence
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 6. Port Already in Use

**Symptom**: `Error: port is already allocated`

**Solutions**:
```bash
# Find process using port 5001
sudo lsof -i :5001

# Kill the process
sudo kill -9 <PID>

# Or change port in backend/.env and docker-compose.yml
```

#### 7. SSL Certificate Issues

**Symptom**: Certificate validation errors

**Solutions**:
```bash
# Check certificate expiry
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check Nginx configuration
sudo docker exec -it ai-assistant-nginx nginx -t

# Restart Nginx
sudo docker compose restart nginx
```

### Getting Help

- **Logs**: Always check logs first
  ```bash
  sudo docker compose logs -f [service_name]
  ```

- **Container Status**: Verify all services are healthy
  ```bash
  sudo docker compose ps
  ```

- **Network Issues**: Ensure containers can communicate
  ```bash
  sudo docker network inspect ai-assistant_ai-assistant-network
  ```

### Debug Mode

Enable verbose logging:

**Backend**:
```python
# app/utils/logger.py
logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```typescript
// Add console.log statements in Chat.tsx
console.log('API Response:', data);
```

## 📝 Additional Documentation

- [GitHub Secrets Setup](.github/GITHUB_SECRETS.md) - CI/CD configuration
- [Backend API](http://localhost:5001/docs) - Interactive API documentation (when running)
- [Ollama Documentation](https://github.com/ollama/ollama) - Ollama usage and models
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - FastAPI framework guide

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [Meta](https://ai.meta.com/) for LLaMA models
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework
- [React](https://reactjs.org/) for the UI library
- Community contributors and testers

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/yourusername/ai-assistant/issues)
- Check existing [Discussions](https://github.com/yourusername/ai-assistant/discussions)

---

**Built with ❤️ for the open-source community**
