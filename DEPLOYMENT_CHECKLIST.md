# Deployment Checklist

Use this checklist to ensure a successful deployment of the AI Assistant system.

## Pre-Deployment

### VPS Setup
- [ ] Ubuntu 24.04 VPS provisioned
- [ ] Minimum 4GB RAM (8GB recommended)
- [ ] 20GB+ disk space available
- [ ] SSH access configured
- [ ] Root or sudo access available
- [ ] Domain name purchased (if using HTTPS)
- [ ] DNS A records configured (if using domain)

### Local Preparation
- [ ] Repository cloned locally
- [ ] Reviewed README.md
- [ ] Reviewed DEPLOYMENT.md
- [ ] Understood architecture (ARCHITECTURE.md)
- [ ] Docker Hub account created (for CI/CD)
- [ ] GitHub repository created

## Initial VPS Configuration

### System Updates
- [ ] Connected to VPS via SSH
- [ ] Updated package lists: `sudo apt-get update`
- [ ] Upgraded packages: `sudo apt-get upgrade -y`
- [ ] Installed basic tools: `curl git wget htop nano ufw`
- [ ] Rebooted if kernel updated

### User Management
- [ ] Created non-root user (optional but recommended)
- [ ] Added user to sudo group
- [ ] Configured SSH key authentication
- [ ] Tested SSH login with new user
- [ ] Disabled root SSH login (optional, for security)

### Firewall Configuration
- [ ] Installed UFW: `sudo apt-get install ufw`
- [ ] Allowed SSH: `sudo ufw allow OpenSSH`
- [ ] Allowed HTTP: `sudo ufw allow 80/tcp`
- [ ] Allowed HTTPS: `sudo ufw allow 443/tcp`
- [ ] Enabled firewall: `sudo ufw enable`
- [ ] Verified rules: `sudo ufw status`

## Docker Installation

- [ ] Removed old Docker versions (if any)
- [ ] Added Docker GPG key
- [ ] Added Docker repository
- [ ] Installed Docker Engine
- [ ] Installed Docker Compose plugin
- [ ] Verified installation:
  - [ ] `docker --version`
  - [ ] `docker compose version`
- [ ] Added user to docker group: `sudo usermod -aG docker $USER`
- [ ] Logged out and back in
- [ ] Tested Docker: `docker run hello-world`

## Application Setup

### Repository
- [ ] Cloned repository to VPS: `git clone <repo-url>`
- [ ] Changed to project directory: `cd ai-assistant`
- [ ] Verified all files present

### Directory Structure
- [ ] Created necessary directories:
  ```bash
  mkdir -p nginx/conf.d
  mkdir -p certbot/conf
  mkdir -p certbot/www
  ```

### Backend Configuration
- [ ] Copied env template: `cp backend/.env.example backend/.env`
- [ ] Edited backend/.env:
  - [ ] Set `OLLAMA_BASE_URL` (default: `http://ollama:11434`)
  - [ ] Set `REDIS_HOST` (default: `redis`)
  - [ ] Set `SESSION_TTL_SECONDS` (default: 600)
  - [ ] Set `CORS_ORIGINS` (production domain or `*`)
  - [ ] Reviewed other settings
- [ ] Saved backend/.env

### Frontend Configuration
- [ ] Copied env template: `cp frontend/.env.example frontend/.env`
- [ ] Edited frontend/.env:
  - [ ] Set `VITE_API_BASE_URL` to production URL
    - With domain: `https://yourdomain.com`
    - Without domain: `http://your-vps-ip`
- [ ] Saved frontend/.env

### Nginx Configuration
- [ ] Reviewed nginx/nginx.conf
- [ ] Edited nginx/conf.d/default.conf:
  - [ ] Updated `server_name` with domain or IP
  - [ ] Verified proxy_pass settings
  - [ ] Checked paths to static files
- [ ] Saved configuration

## Docker Deployment

### Build Images
- [ ] Ran: `sudo docker compose build`
- [ ] Build completed without errors
- [ ] Checked built images: `sudo docker images`

### Start Services
- [ ] Started services: `sudo docker compose up -d`
- [ ] Checked status: `sudo docker compose ps`
- [ ] Verified all containers are "Up"

### Service Health Checks
- [ ] Redis healthy: `sudo docker exec -it ai-assistant-redis redis-cli ping`
  - Expected: `PONG`
- [ ] Ollama healthy: `curl http://localhost:11434/api/tags`
  - Expected: JSON response (may be empty initially)
- [ ] Backend healthy: `curl http://localhost:5001/api/health`
  - Expected: `{"status":"ok"}`
- [ ] Nginx healthy: `curl http://localhost/api/health`
  - Expected: `{"status":"ok"}`

### Logs Review
- [ ] Checked all logs: `sudo docker compose logs`
- [ ] No critical errors found
- [ ] Backend started successfully
- [ ] Nginx started successfully
- [ ] Redis connected
- [ ] Ollama ready (or starting)

## AI Model Setup

### Download LLaMA Model
- [ ] Started download: `sudo docker exec -it ai-assistant-ollama ollama pull llama3.1:8b`
- [ ] Download completed (~4.7GB, may take 5-15 minutes)
- [ ] Verified model: `sudo docker exec -it ai-assistant-ollama ollama list`
  - Expected: `llama3.1:8b` in list

### Test Model
- [ ] Tested model via API: `curl http://localhost:11434/api/generate ...`
- [ ] Model responds (may be slow on first run)

## Application Testing

### Frontend Access
- [ ] Opened browser to `http://your-vps-ip` (or domain)
- [ ] Chat interface loads
- [ ] UI is responsive
- [ ] No console errors in browser

### Basic Chat Test
- [ ] Sent test message: "Hello, what is 2+2?"
- [ ] Received AI response
- [ ] Response makes sense
- [ ] Session persists on page reload

### Memory Test
- [ ] Sent: "My name is Alice"
- [ ] Sent: "What is my name?"
- [ ] AI remembers "Alice"

### Scraping Test (Optional)
- [ ] Enabled "Use Web Scraping"
- [ ] Entered URL: `https://example.com`
- [ ] Sent message: "What is on this page?"
- [ ] Received response mentioning page content

### API Test
- [ ] Ran test script: `python3 scripts/test_api.py`
- [ ] All tests passed

## HTTPS Setup (Production Only)

### Prerequisites
- [ ] Domain configured and pointing to VPS
- [ ] DNS propagation complete (verify with `nslookup yourdomain.com`)
- [ ] Port 80 accessible from internet

### Certificate Obtainment
- [ ] Stopped nginx temporarily: `sudo docker compose stop nginx`
- [ ] Installed Certbot: `sudo apt-get install certbot`
- [ ] Ran Certbot:
  ```bash
  sudo certbot certonly --standalone \
    -d yourdomain.com \
    -d www.yourdomain.com \
    --email your-email@example.com \
    --agree-tos
  ```
- [ ] Certificate obtained successfully
- [ ] Certificate location noted (usually `/etc/letsencrypt/live/yourdomain.com/`)

### Nginx SSL Configuration
- [ ] Copied SSL template: `cp nginx/conf.d/ssl.conf.example nginx/conf.d/ssl.conf`
- [ ] Edited ssl.conf:
  - [ ] Replaced all `yourdomain.com` with actual domain
  - [ ] Verified certificate paths
- [ ] Updated docker-compose.yml volumes (if needed):
  ```yaml
  - /etc/letsencrypt:/etc/letsencrypt:ro
  - /var/www/certbot:/var/www/certbot:ro
  ```
- [ ] Restarted services: `sudo docker compose up -d`

### SSL Verification
- [ ] Accessed `https://yourdomain.com`
- [ ] Certificate valid (green lock)
- [ ] No SSL errors
- [ ] HTTP redirects to HTTPS

### Auto-Renewal Setup
- [ ] Added cron job:
  ```bash
  0 3 * * * certbot renew --quiet --post-hook 'cd /path/to/ai-assistant && docker compose restart nginx'
  ```
- [ ] Tested renewal: `sudo certbot renew --dry-run`

## GitHub CI/CD Setup

### Repository Setup
- [ ] Code pushed to GitHub
- [ ] Repository is public or has Actions enabled

### Secrets Configuration
- [ ] Navigated to: Settings → Secrets and variables → Actions
- [ ] Added secrets:
  - [ ] `DOCKER_USERNAME`
  - [ ] `DOCKER_PASSWORD`
  - [ ] `DOCKER_REPO_BACKEND`
  - [ ] `DOCKER_REPO_FRONTEND`
  - [ ] `DOCKER_REPO_NGINX`
  - [ ] `VITE_API_BASE_URL` (optional)

### Workflow Test
- [ ] Made a small code change
- [ ] Committed and pushed to main
- [ ] Workflow triggered automatically
- [ ] All jobs completed successfully
- [ ] Images pushed to Docker Hub
- [ ] Verified images on Docker Hub

### Deploy from CI
- [ ] SSH to VPS
- [ ] Pulled latest images: `sudo docker compose pull`
- [ ] Restarted services: `sudo docker compose up -d`
- [ ] Verified update applied

## Monitoring Setup

### Log Rotation
- [ ] Configured Docker log limits:
  ```json
  # /etc/docker/daemon.json
  {
    "log-driver": "json-file",
    "log-opts": {
      "max-size": "10m",
      "max-file": "3"
    }
  }
  ```
- [ ] Restarted Docker: `sudo systemctl restart docker`

### Monitoring Commands Tested
- [ ] `sudo docker compose ps` - Shows container status
- [ ] `sudo docker compose logs -f` - Follows logs
- [ ] `sudo docker stats` - Shows resource usage
- [ ] `df -h` - Shows disk usage
- [ ] `free -h` - Shows memory usage
- [ ] `htop` - Interactive process viewer

## Backup Setup

### Backup Script
- [ ] Created backup script (see DEPLOYMENT.md)
- [ ] Made executable: `chmod +x ~/backup-ai-assistant.sh`
- [ ] Tested backup script: `./backup-ai-assistant.sh`
- [ ] Verified backup files created

### Automated Backups
- [ ] Added to crontab:
  ```bash
  0 2 * * * ~/backup-ai-assistant.sh >> ~/backup.log 2>&1
  ```
- [ ] Verified cron job: `crontab -l`

### Backup Verification
- [ ] Backup directory exists: `~/backups/`
- [ ] Redis dumps present
- [ ] Configuration backups present
- [ ] Tested restore procedure

## Security Hardening

### System Security
- [ ] Disabled password authentication (SSH keys only)
- [ ] Changed default SSH port (optional)
- [ ] Installed fail2ban (optional): `sudo apt-get install fail2ban`
- [ ] Configured automatic security updates
- [ ] Reviewed open ports: `sudo netstat -tulpn`

### Application Security
- [ ] Reviewed CORS settings in backend/.env
- [ ] Set strong passwords (if any used)
- [ ] Reviewed exposed ports
- [ ] Checked security headers in nginx config
- [ ] Verified non-root container users

### Data Security
- [ ] Session data encrypted (Redis)
- [ ] Environment files not committed to Git
- [ ] Secrets managed securely
- [ ] SSL certificates protected

## Performance Optimization

### Resource Limits
- [ ] Set container resource limits (if needed)
- [ ] Monitored memory usage
- [ ] Checked disk space: `df -h`
- [ ] Verified swap configured (if low memory)

### Caching
- [ ] Verified gzip enabled in Nginx
- [ ] Confirmed static file caching
- [ ] Tested page load speed

### Database
- [ ] Configured Redis maxmemory (if needed)
- [ ] Set eviction policy
- [ ] Monitored Redis memory: `docker exec -it ai-assistant-redis redis-cli INFO memory`

## Documentation

### Internal Documentation
- [ ] Documented VPS credentials (securely)
- [ ] Noted domain registrar details
- [ ] Recorded SSL certificate details
- [ ] Documented backup location
- [ ] Created runbook for common tasks

### Team Onboarding
- [ ] README.md accessible
- [ ] DEPLOYMENT.md reviewed
- [ ] Access credentials shared (securely)
- [ ] Monitoring access configured

## Post-Deployment

### Validation
- [ ] Application accessible from internet
- [ ] All features working
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Mobile responsiveness verified

### User Acceptance
- [ ] Tested by stakeholders
- [ ] Feedback collected
- [ ] Issues documented
- [ ] Critical issues resolved

### Monitoring
- [ ] Set up uptime monitoring (optional)
- [ ] Configured alerts (optional)
- [ ] Checked resource usage trends
- [ ] Planned capacity upgrades (if needed)

## Maintenance Plan

### Regular Tasks
- [ ] Weekly: Review logs
- [ ] Weekly: Check disk space
- [ ] Weekly: Verify backups
- [ ] Monthly: Update packages
- [ ] Monthly: Review security advisories
- [ ] Quarterly: Test disaster recovery
- [ ] Quarterly: Performance review

### Update Procedure
- [ ] Documented update process
- [ ] Tested update in staging (if available)
- [ ] Scheduled maintenance windows
- [ ] Prepared rollback plan

## Troubleshooting Reference

### Common Issues Documented
- [ ] Port conflicts
- [ ] Memory issues
- [ ] Disk space issues
- [ ] SSL certificate problems
- [ ] Container startup failures
- [ ] Ollama connection issues

### Support Contacts
- [ ] VPS provider support
- [ ] DNS provider support
- [ ] Team member contacts
- [ ] Escalation procedures

## Sign-Off

### Pre-Production
- [ ] All checklist items completed
- [ ] Testing passed
- [ ] Documentation complete
- [ ] Backups configured
- [ ] Monitoring active

### Production Launch
- [ ] Stakeholder approval received
- [ ] Launch date scheduled
- [ ] Communication plan executed
- [ ] Support team briefed
- [ ] Launched successfully

### Post-Launch
- [ ] Monitored for 24 hours
- [ ] No critical issues
- [ ] Performance metrics met
- [ ] User feedback positive
- [ ] Lessons learned documented

---

## Notes

**Deployment Date:** _______________

**Deployed By:** _______________

**VPS IP:** _______________

**Domain:** _______________

**Issues Encountered:**
- 
- 
- 

**Notes:**
- 
- 
- 

---

**Status:** 
- [ ] ✅ Deployment Successful
- [ ] ⚠️ Deployment with Issues
- [ ] ❌ Deployment Failed

**Sign-off:** _______________ Date: _______________
