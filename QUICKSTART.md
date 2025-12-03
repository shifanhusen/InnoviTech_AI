# Quick Start Guide

Get your AI Assistant up and running in 5 minutes!

## Prerequisites

✅ Ubuntu 24.04 VPS with:
- 4GB+ RAM
- 20GB+ disk space
- Docker & Docker Compose installed

## Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant
```

## Step 2: Run Setup

```bash
# Option 1: Using Make (recommended)
make setup

# Option 2: Manual setup
chmod +x scripts/setup.sh
sudo bash scripts/setup.sh
```

## Step 3: Configure

### Backend Configuration
```bash
nano backend/.env
```

**Minimum required changes:**
```env
# If using external Ollama (already running)
OLLAMA_BASE_URL=http://your-ollama-host:11434

# If using Docker Ollama (default)
OLLAMA_BASE_URL=http://ollama:11434
```

### Frontend Configuration
```bash
nano frontend/.env
```

```env
# Use your domain or VPS IP
VITE_API_BASE_URL=http://your-vps-ip:5001
```

## Step 4: Start Services

```bash
# Using Make
make deploy

# Or manually
sudo docker compose up -d
```

## Step 5: Download AI Model

```bash
# This downloads ~4.7GB (takes 5-10 minutes)
make ollama-pull

# Or manually
sudo docker exec -it ai-assistant-ollama ollama pull llama3.1:8b
```

## Step 6: Access Application

Open your browser:
- **Frontend**: `http://your-vps-ip`
- **API Docs**: `http://your-vps-ip:5001/docs`

## Verify Installation

```bash
# Check all services are running
make ps

# Test backend
curl http://localhost:5001/api/health

# View logs
make logs
```

Expected output:
```json
{"status": "ok"}
```

## Common Issues

### 1. Services not starting
```bash
# Check logs
make logs

# Restart services
make restart
```

### 2. Port already in use
```bash
# Check what's using port 80
sudo lsof -i :80

# Stop the service (if Apache)
sudo systemctl stop apache2
```

### 3. Out of memory
```bash
# Check memory
free -h

# Add swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 4. Ollama model not found
```bash
# Pull the model again
make ollama-pull

# Verify model is available
make ollama-list
```

## Next Steps

### Enable HTTPS (Recommended for Production)
```bash
# Run SSL setup script
make ssl-setup
```

### Configure CI/CD
1. Push to GitHub
2. Add Docker Hub credentials as GitHub Secrets
3. See [GitHub Secrets Guide](.github/GITHUB_SECRETS.md)

### Monitor Services
```bash
# View stats
make stats

# Check health
make health

# View specific logs
make logs-backend
make logs-ollama
```

## Useful Commands

```bash
# Stop everything
make down

# Start everything
make up

# Restart services
make restart

# View all logs
make logs

# Access Redis CLI
make redis-cli

# Backup data
make backup

# Update application
make update

# Clean everything (WARNING: deletes data)
make clean-volumes
```

## Test the Chat

Using cURL:
```bash
curl -X POST http://localhost:5001/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Hello! What can you help me with?",
    "use_scrape": false
  }'
```

Expected response:
```json
{
  "reply": "Hello! I'm an AI assistant...",
  "session_expired": false
}
```

## Production Checklist

Before going to production:

- [ ] Update `backend/.env` with production settings
- [ ] Update `frontend/.env` with production domain
- [ ] Configure domain DNS (A records)
- [ ] Run SSL setup: `make ssl-setup`
- [ ] Update `nginx/conf.d/default.conf` with your domain
- [ ] Set up firewall: `sudo ufw enable`
- [ ] Configure backups: Set up cron job
- [ ] Set up monitoring (optional)
- [ ] Test all functionality
- [ ] Review security settings

## Getting Help

- 📖 [Full Documentation](README.md)
- 🚀 [Deployment Guide](DEPLOYMENT.md)
- 🔌 [API Integration Examples](INTEGRATIONS.md)
- 🐛 [Troubleshooting](README.md#troubleshooting)

## Support

Need help? Open an issue on GitHub!

---

**That's it! Your AI Assistant is ready to use. 🎉**
