# Deployment Guide

This guide provides step-by-step instructions for deploying the AI Assistant application to a production Ubuntu 24.04 VPS.

## Table of Contents

1. [VPS Requirements](#vps-requirements)
2. [Initial Server Setup](#initial-server-setup)
3. [Docker Installation](#docker-installation)
4. [Application Deployment](#application-deployment)
5. [HTTPS Configuration](#https-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Backup & Recovery](#backup--recovery)

## VPS Requirements

### Minimum Specifications
- **OS**: Ubuntu 24.04 LTS
- **RAM**: 4GB (8GB recommended)
- **CPU**: 2 cores (4 cores recommended)
- **Disk**: 20GB SSD (50GB recommended)
- **Network**: 100 Mbps connection

### Recommended Providers
- DigitalOcean ($20-40/month for adequate specs)
- Linode
- Vultr
- AWS EC2
- Google Cloud Platform

## Initial Server Setup

### 1. Connect to VPS

```bash
ssh root@your-vps-ip
```

### 2. Update System

```bash
apt-get update && apt-get upgrade -y
apt-get install -y curl git wget htop nano ufw
```

### 3. Create Non-Root User

```bash
# Create user
adduser appuser
usermod -aG sudo appuser

# Switch to user
su - appuser
```

### 4. Configure Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

### 5. Set Up SSH Key Authentication (Recommended)

On your local machine:
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
ssh-copy-id appuser@your-vps-ip
```

Test connection:
```bash
ssh appuser@your-vps-ip
```

## Docker Installation

### Install Docker & Docker Compose

```bash
# Install dependencies
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
exit
# Then reconnect via SSH
```

### Verify Installation

```bash
docker --version
docker compose version
```

## Application Deployment

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant
```

### 2. Configure Environment

```bash
# Backend configuration
cp backend/.env.example backend/.env
nano backend/.env
```

Update these values:
```env
# Set your domain or VPS IP
CORS_ORIGINS=https://yourdomain.com,http://your-vps-ip

# Adjust resources if needed
OLLAMA_TIMEOUT=120
SESSION_TTL_SECONDS=600
```

```bash
# Frontend configuration
cp frontend/.env.example frontend/.env
nano frontend/.env
```

```env
# Use your domain or VPS IP
VITE_API_BASE_URL=https://yourdomain.com
# or
VITE_API_BASE_URL=http://your-vps-ip
```

### 3. Update Nginx Configuration

```bash
nano nginx/conf.d/default.conf
```

Change `server_name`:
```nginx
server_name yourdomain.com www.yourdomain.com;
# or for IP-only access:
server_name your-vps-ip;
```

### 4. Build and Start Services

```bash
# Build images
sudo docker compose build

# Start services
sudo docker compose up -d

# Check status
sudo docker compose ps
```

All services should show "Up" status.

### 5. Pull LLaMA Model

```bash
# This downloads ~4.7GB, may take a few minutes
sudo docker exec -it ai-assistant-ollama ollama pull llama3.1:8b

# Verify
sudo docker exec -it ai-assistant-ollama ollama list
```

### 6. Verify Deployment

```bash
# Check logs
sudo docker compose logs -f

# Test backend
curl http://localhost:5001/api/health

# Test full stack
curl http://localhost/api/health
```

Open browser: `http://your-vps-ip`

## HTTPS Configuration

### Prerequisites
- Domain name pointing to your VPS IP
- DNS A records configured:
  - `yourdomain.com` → `your-vps-ip`
  - `www.yourdomain.com` → `your-vps-ip`

Wait for DNS propagation (can take 5-60 minutes):
```bash
# Verify DNS
nslookup yourdomain.com
dig yourdomain.com
```

### Option 1: Automated Setup (Recommended)

```bash
cd ~/ai-assistant
chmod +x scripts/setup-ssl.sh
sudo bash scripts/setup-ssl.sh
```

Follow the prompts and enter:
- Your domain name
- Your email address

### Option 2: Manual Setup

#### Step 1: Install Certbot

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

#### Step 2: Stop Nginx

```bash
cd ~/ai-assistant
sudo docker compose stop nginx
```

#### Step 3: Obtain Certificate

```bash
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  --preferred-challenges http
```

#### Step 4: Configure Nginx for HTTPS

```bash
# Copy SSL template
cp nginx/conf.d/ssl.conf.example nginx/conf.d/ssl.conf

# Edit with your domain
nano nginx/conf.d/ssl.conf
```

Replace all instances of `yourdomain.com` with your actual domain.

#### Step 5: Update Docker Compose

```bash
nano docker-compose.yml
```

Ensure these volumes are present under the `nginx` service:
```yaml
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
  - /var/www/certbot:/var/www/certbot:ro
```

#### Step 6: Restart Services

```bash
sudo docker compose up -d
```

#### Step 7: Test HTTPS

Open browser: `https://yourdomain.com`

Verify SSL certificate:
```bash
curl -vI https://yourdomain.com 2>&1 | grep -i ssl
```

#### Step 8: Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job
(crontab -l 2>/dev/null || true; echo "0 3 * * * certbot renew --quiet --post-hook 'cd ~/ai-assistant && docker compose restart nginx'") | crontab -

# Verify cron job
crontab -l
```

## Monitoring & Maintenance

### Check Service Status

```bash
cd ~/ai-assistant
sudo docker compose ps
sudo docker compose logs -f [service_name]
```

### Resource Monitoring

```bash
# System resources
htop

# Docker stats
sudo docker stats

# Disk usage
df -h
sudo docker system df
```

### Restart Services

```bash
# Restart all
sudo docker compose restart

# Restart specific service
sudo docker compose restart backend

# Rebuild and restart
sudo docker compose up -d --build
```

### Update Application

```bash
cd ~/ai-assistant

# Pull latest code
git pull origin main

# Rebuild and restart
sudo docker compose build
sudo docker compose up -d

# Clean old images
sudo docker image prune -a -f
```

### View Logs

```bash
# All services
sudo docker compose logs -f

# Specific service
sudo docker compose logs -f backend

# Last 100 lines
sudo docker compose logs --tail=100 backend

# Follow new logs only
sudo docker compose logs -f --tail=0
```

### Database/Session Management

```bash
# Access Redis CLI
sudo docker exec -it ai-assistant-redis redis-cli

# Check memory usage
INFO memory

# List all session keys
KEYS session:*

# View specific session
GET session:abc123

# Clear all sessions
FLUSHDB

# Exit
exit
```

## Backup & Recovery

### Backup Strategy

#### 1. Backup Redis Data

```bash
# Create backup directory
mkdir -p ~/backups/redis

# Backup Redis dump
sudo docker exec ai-assistant-redis redis-cli BGSAVE
sudo docker cp ai-assistant-redis:/data/dump.rdb ~/backups/redis/dump-$(date +%Y%m%d-%H%M%S).rdb
```

#### 2. Backup Ollama Models

```bash
mkdir -p ~/backups/ollama

# Backup Ollama data
sudo docker run --rm -v ai-assistant_ollama_data:/data -v ~/backups/ollama:/backup alpine tar czf /backup/ollama-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
```

#### 3. Backup Configuration

```bash
mkdir -p ~/backups/config

# Backup environment files
cp ~/ai-assistant/backend/.env ~/backups/config/backend.env
cp ~/ai-assistant/frontend/.env ~/backups/config/frontend.env
cp -r ~/ai-assistant/nginx ~/backups/config/
```

#### 4. Automated Backup Script

Create `~/backup-ai-assistant.sh`:

```bash
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR/{redis,ollama,config}

# Redis backup
docker exec ai-assistant-redis redis-cli BGSAVE
sleep 5
docker cp ai-assistant-redis:/data/dump.rdb $BACKUP_DIR/redis/dump-$DATE.rdb

# Ollama backup
docker run --rm -v ai-assistant_ollama_data:/data -v $BACKUP_DIR/ollama:/backup alpine tar czf /backup/ollama-$DATE.tar.gz -C /data .

# Config backup
cp ~/ai-assistant/backend/.env $BACKUP_DIR/config/backend-$DATE.env
cp ~/ai-assistant/frontend/.env $BACKUP_DIR/config/frontend-$DATE.env

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
chmod +x ~/backup-ai-assistant.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null || true; echo "0 2 * * * ~/backup-ai-assistant.sh >> ~/backup.log 2>&1") | crontab -
```

### Recovery

#### Restore Redis

```bash
sudo docker compose stop redis
sudo docker cp ~/backups/redis/dump-TIMESTAMP.rdb ai-assistant-redis:/data/dump.rdb
sudo docker compose start redis
```

#### Restore Ollama

```bash
sudo docker compose stop ollama
cd ~/backups/ollama
tar xzf ollama-TIMESTAMP.tar.gz -C /tmp/ollama-restore
sudo docker run --rm -v ai-assistant_ollama_data:/data -v /tmp/ollama-restore:/restore alpine sh -c "cp -r /restore/* /data/"
sudo docker compose start ollama
```

#### Restore Configuration

```bash
cp ~/backups/config/backend-TIMESTAMP.env ~/ai-assistant/backend/.env
cp ~/backups/config/frontend-TIMESTAMP.env ~/ai-assistant/frontend/.env
sudo docker compose restart
```

## Troubleshooting Deployment Issues

### Port Already in Use

```bash
# Find process using port 80
sudo lsof -i :80
sudo netstat -tulpn | grep :80

# Kill process
sudo kill -9 <PID>

# Or stop Apache/Nginx if installed
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker resources
sudo docker system prune -a -f --volumes

# Remove old logs
sudo journalctl --vacuum-time=3d
```

### Service Won't Start

```bash
# Check logs
sudo docker compose logs [service]

# Check system resources
free -h
df -h

# Restart Docker daemon
sudo systemctl restart docker
```

### DNS Issues

```bash
# Test DNS resolution
nslookup yourdomain.com
dig yourdomain.com

# Update DNS servers
sudo nano /etc/resolv.conf
# Add: nameserver 8.8.8.8
```

## Performance Optimization

### 1. Enable Docker Logging Limits

Create `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:
```bash
sudo systemctl restart docker
```

### 2. Optimize Redis

```bash
# Connect to Redis
sudo docker exec -it ai-assistant-redis redis-cli

# Set memory limit
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru
CONFIG REWRITE
```

### 3. Enable Gzip in Nginx

Already configured in `nginx.conf`, verify it's working:
```bash
curl -H "Accept-Encoding: gzip" -I https://yourdomain.com
```

Should see: `Content-Encoding: gzip`

## Security Best Practices

1. **Keep system updated**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Enable automatic security updates**:
   ```bash
   sudo apt-get install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **Configure firewall properly**:
   ```bash
   sudo ufw status verbose
   ```

4. **Use strong passwords** for all accounts

5. **Regularly backup** data and configurations

6. **Monitor logs** for suspicious activity:
   ```bash
   sudo tail -f /var/log/auth.log
   ```

7. **Keep Docker images updated**:
   ```bash
   sudo docker compose pull
   sudo docker compose up -d
   ```

---

**Deployment complete! Your AI Assistant is now running in production. 🚀**
