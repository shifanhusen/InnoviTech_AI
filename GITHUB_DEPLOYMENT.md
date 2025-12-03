# GitHub Auto-Deployment Setup Guide

This guide will help you set up automatic deployment to your Ubuntu server whenever you push to GitHub.

## 📋 Prerequisites

- Ubuntu server with Docker and Docker Compose installed
- Server is already running Ollama with LLaMA model
- SSH access to your server
- GitHub account

---

## Part 1: Prepare Your Ubuntu Server

### 1.1 Connect to Your Server

```bash
ssh your-username@your-server-ip
```

### 1.2 Clone the Repository (First Time)

```bash
# Navigate to your preferred directory
cd /home/$USER

# Clone the repository (you'll do this after creating the GitHub repo)
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git ai-assistant

# Enter the project directory
cd ai-assistant
```

### 1.3 Set Up Environment Files

```bash
# Backend environment
cp backend/.env.example backend/.env
nano backend/.env
```

Update the following in `backend/.env`:
```env
OLLAMA_BASE_URL=http://ollama:11434
REDIS_HOST=redis
SESSION_TTL_SECONDS=600
MAX_HISTORY_MESSAGES=20
CORS_ORIGINS=*
PORT=5001
```

```bash
# Frontend environment
cp frontend/.env.example frontend/.env
nano frontend/.env
```

Update `frontend/.env`:
```env
VITE_API_BASE_URL=http://YOUR-SERVER-IP
# OR if you have a domain:
# VITE_API_BASE_URL=https://yourdomain.com
```

### 1.4 Generate SSH Key for GitHub Actions

```bash
# Generate a new SSH key (press Enter for all prompts to use defaults)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# Display the public key - you'll need this later
cat ~/.ssh/github_actions_deploy.pub

# Add the public key to authorized_keys
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys

# Display the private key - you'll need this for GitHub Secrets
cat ~/.ssh/github_actions_deploy
```

**IMPORTANT:** Copy both keys:
- **Public key** (`github_actions_deploy.pub`) - Already added to authorized_keys
- **Private key** (`github_actions_deploy`) - You'll add this to GitHub Secrets

### 1.5 Test Initial Deployment Manually

```bash
cd /home/$USER/ai-assistant

# Build and start services
docker compose up -d

# Check if LLaMA model exists in your Ollama
docker exec ai-assistant-ollama ollama list

# If the model isn't there, pull it (if your Ollama is external, skip this)
# docker exec ai-assistant-ollama ollama pull llama3.1:8b

# Check services are running
docker compose ps

# Test backend health
curl http://localhost:5001/api/health

# Test nginx
curl http://localhost/api/health
```

---

## Part 2: Create GitHub Repository

### 2.1 Initialize Git Repository Locally

Open PowerShell in your project directory:

```powershell
cd 'c:\Users\shifa\source\InnoviTech AI'

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Production-ready AI Assistant"
```

### 2.2 Create GitHub Repository

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name:** `ai-assistant` (or your preferred name)
   - **Description:** "Production-ready AI Assistant with LLaMA 3.1, Redis memory, and web scraping"
   - **Visibility:** Private or Public (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### 2.3 Push Code to GitHub

GitHub will show you commands. Use these in PowerShell:

```powershell
# Add the remote repository
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Part 3: Configure GitHub Secrets

### 3.1 Navigate to Repository Settings

1. Go to your GitHub repository
2. Click **Settings** (top right)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### 3.2 Add Required Secrets

Add each of these secrets by clicking "New repository secret":

#### Secret 1: SERVER_HOST
- **Name:** `SERVER_HOST`
- **Value:** Your Ubuntu server IP address or domain
  ```
  123.45.67.89
  ```

#### Secret 2: SERVER_USERNAME
- **Name:** `SERVER_USERNAME`
- **Value:** Your SSH username on the server
  ```
  ubuntu
  ```
  or
  ```
  root
  ```

#### Secret 3: SSH_PRIVATE_KEY
- **Name:** `SSH_PRIVATE_KEY`
- **Value:** The ENTIRE private key from your server (from step 1.4)
  ```
  -----BEGIN OPENSSH PRIVATE KEY-----
  b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
  ... (many lines) ...
  -----END OPENSSH PRIVATE KEY-----
  ```
  
**IMPORTANT:** Copy the ENTIRE key including the BEGIN and END lines!

#### Secret 4: PROJECT_PATH
- **Name:** `PROJECT_PATH`
- **Value:** Full path to your project on the server
  ```
  /home/ubuntu/ai-assistant
  ```

#### Secret 5: SERVER_PORT (Optional)
- **Name:** `SERVER_PORT`
- **Value:** SSH port (only if you changed it from default 22)
  ```
  22
  ```

### 3.3 Verify Secrets

After adding all secrets, you should see:
- ✅ SERVER_HOST
- ✅ SERVER_USERNAME
- ✅ SSH_PRIVATE_KEY
- ✅ PROJECT_PATH
- ✅ SERVER_PORT (optional)

---

## Part 4: Test Automatic Deployment

### 4.1 Make a Test Change

In your local project, make a small change:

```powershell
# Edit README.md or any file
echo "# Test deployment" >> TEST.md

# Commit and push
git add .
git commit -m "Test: Trigger auto-deployment"
git push origin main
```

### 4.2 Watch the Deployment

1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see "Deploy to Ubuntu Server" workflow running
4. Click on the workflow run to see live logs
5. Wait for it to complete (usually 2-5 minutes)

### 4.3 Verify Deployment on Server

SSH to your server and check:

```bash
ssh your-username@your-server-ip

cd /home/$USER/ai-assistant

# Check if latest code is pulled
git log -1

# Check running containers
docker compose ps

# Check logs
docker compose logs -f --tail=50
```

### 4.4 Test the Application

Open your browser:
```
http://YOUR-SERVER-IP
```

Or with domain:
```
https://yourdomain.com
```

Send a test message to verify everything works!

---

## Part 5: Configure Ollama Connection

Since your Ollama is already running on the Ubuntu server, you have two options:

### Option A: Use System Ollama (Recommended)

If Ollama is already running on your server (not in Docker), update `docker-compose.yml`:

```yaml
# In docker-compose.yml, update backend service:
services:
  backend:
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434  # For Docker Desktop
      # OR on Linux:
      - OLLAMA_BASE_URL=http://172.17.0.1:11434  # Docker bridge network
```

Or add to backend/.env:
```env
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

### Option B: Use Docker Ollama

If you want Ollama in Docker, the current setup is fine. Just ensure the model is pulled:

```bash
docker exec ai-assistant-ollama ollama pull llama3.1:8b
```

---

## Part 6: Workflow Customization

### 6.1 Change When Deployment Happens

Edit `.github/workflows/deploy.yml`:

```yaml
# Deploy on push to main and develop branches
on:
  push:
    branches:
      - main
      - develop

# Or deploy only on tags
on:
  push:
    tags:
      - 'v*'
```

### 6.2 Add Deployment Notifications (Optional)

Add Slack/Discord notifications:

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Deployment ${{ job.status }}"
      }
```

### 6.3 Skip Deployment for Specific Commits

Add `[skip ci]` to commit message:

```bash
git commit -m "Update README [skip ci]"
```

---

## Part 7: Troubleshooting

### Issue: SSH Connection Failed

**Solution 1:** Check SSH key format
```bash
# On server, verify public key is in authorized_keys
cat ~/.ssh/authorized_keys | grep github-actions

# Verify private key format (should start with BEGIN OPENSSH PRIVATE KEY)
cat ~/.ssh/github_actions_deploy
```

**Solution 2:** Test SSH connection manually
```bash
# On your local machine
ssh -i path/to/private_key your-username@your-server-ip
```

**Solution 3:** Check firewall
```bash
# On server
sudo ufw status
sudo ufw allow 22/tcp
```

### Issue: Permission Denied

**Solution:** Ensure user has Docker permissions
```bash
# On server
sudo usermod -aG docker $USER
# Logout and login again
```

### Issue: Health Check Failed

**Solution 1:** Check backend logs
```bash
docker compose logs backend
```

**Solution 2:** Verify environment variables
```bash
docker compose exec backend env | grep OLLAMA
```

**Solution 3:** Test Ollama connection
```bash
curl http://localhost:11434/api/tags
```

### Issue: Port Already in Use

**Solution:** Check what's using the port
```bash
# Check port 80
sudo netstat -tulpn | grep :80

# Kill the process or change ports in docker-compose.yml
```

### Issue: Disk Space Full

**Solution:** Clean up Docker
```bash
docker system prune -a -f
docker volume prune -f
```

### Issue: Git Pull Fails

**Solution:** Ensure server can access GitHub
```bash
# On server, add GitHub to known hosts
ssh-keyscan github.com >> ~/.ssh/known_hosts

# Or use HTTPS instead of SSH
cd /home/$USER/ai-assistant
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
```

---

## Part 8: Security Best Practices

### 8.1 Limit SSH Key Permissions

On your server:
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions_deploy
```

### 8.2 Use a Dedicated Deployment User

```bash
# Create deployment user
sudo adduser github-deploy
sudo usermod -aG docker github-deploy

# Use this user in GitHub Secrets instead of root
```

### 8.3 Restrict SSH Key to Specific Commands

In `~/.ssh/authorized_keys`, prepend to the public key:
```
command="cd /home/ubuntu/ai-assistant && $SSH_ORIGINAL_COMMAND" ssh-ed25519 AAAA...
```

### 8.4 Enable UFW Firewall

```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

---

## Part 9: Monitoring Deployments

### 9.1 View Deployment History

1. Go to GitHub repo → **Actions** tab
2. See all deployment runs
3. Click any run to see detailed logs

### 9.2 Check Server Logs

```bash
# Real-time logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100

# Specific service
docker compose logs backend --tail=50
```

### 9.3 Set Up Log Monitoring

```bash
# Install log monitoring (optional)
sudo apt-get install lnav

# View logs with lnav
docker compose logs | lnav
```

---

## Part 10: Rollback Procedure

If a deployment breaks something:

### Method 1: Rollback via Git

```bash
# On server
cd /home/$USER/ai-assistant

# View recent commits
git log --oneline -10

# Rollback to previous commit
git reset --hard COMMIT_HASH

# Restart services
docker compose down
docker compose up -d
```

### Method 2: Trigger Re-deployment

```bash
# On local machine
git revert HEAD
git push origin main
# This will trigger automatic deployment of the reverted code
```

---

## Part 11: Advanced Configuration

### 11.1 Blue-Green Deployment

Update `deploy.yml` for zero-downtime:

```yaml
# Start new containers with different names
docker compose -p ai-assistant-new up -d

# Run health checks
# If successful, switch traffic
# If failed, rollback

docker compose -p ai-assistant down
docker compose -p ai-assistant-new restart
```

### 11.2 Database Migrations

Add migration step in `deploy.yml`:

```yaml
# Before starting services
echo "Running database migrations..."
docker compose run --rm backend python manage.py migrate
```

### 11.3 Environment-Specific Deployments

Create separate workflows:
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-production.yml`

---

## 📝 Quick Reference

### Common Commands

```bash
# On Server:
cd /home/$USER/ai-assistant
docker compose ps                    # List containers
docker compose logs -f              # Follow logs
docker compose restart              # Restart all
docker compose restart backend      # Restart one service
docker system prune -f              # Clean up

# Local:
git add .
git commit -m "message"
git push origin main                # Triggers deployment

# Check deployment status
# Go to: https://github.com/YOUR-USERNAME/YOUR-REPO/actions
```

### GitHub Secrets Checklist
- ✅ SERVER_HOST
- ✅ SERVER_USERNAME
- ✅ SSH_PRIVATE_KEY
- ✅ PROJECT_PATH
- ✅ SERVER_PORT (optional)

---

## 🎉 Success Checklist

- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] SSH key generated on server
- [ ] GitHub Secrets configured
- [ ] First deployment successful
- [ ] Application accessible via browser
- [ ] LLaMA model working
- [ ] Automatic deployment tested
- [ ] Rollback procedure tested

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [SSH Key Authentication](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

---

**Need Help?**

If you encounter issues:
1. Check the GitHub Actions logs
2. SSH to server and check `docker compose logs`
3. Verify all GitHub Secrets are set correctly
4. Ensure server has enough disk space and memory
5. Check firewall rules

Your deployment should now work automatically on every push to main! 🚀
