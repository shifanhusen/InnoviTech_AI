# AI Assistant - GitHub Secrets Configuration

This document explains the GitHub Secrets required for the CI/CD workflow.

## Required Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

### Docker Hub Authentication

1. **DOCKER_USERNAME**
   - Your Docker Hub username
   - Example: `johnsmith`

2. **DOCKER_PASSWORD**
   - Your Docker Hub password or access token (recommended)
   - To create an access token:
     - Go to Docker Hub → Account Settings → Security → New Access Token
     - Give it a name like "GitHub Actions"
     - Copy the token

### Docker Repository Names

3. **DOCKER_REPO_BACKEND** (optional)
   - Full repository name for backend image
   - Format: `username/repository-name`
   - Example: `johnsmith/ai-assistant-backend`
   - Default: Falls back to `your-username/ai-assistant-backend`

4. **DOCKER_REPO_FRONTEND** (optional)
   - Full repository name for frontend image
   - Example: `johnsmith/ai-assistant-frontend`

5. **DOCKER_REPO_NGINX** (optional)
   - Full repository name for nginx image
   - Example: `johnsmith/ai-assistant-nginx`

### Frontend Configuration

6. **VITE_API_BASE_URL** (optional)
   - API base URL for production frontend
   - Example: `https://api.yourdomain.com` or `https://yourdomain.com`
   - Default: `http://localhost:5001`

## Alternative: GitHub Container Registry (GHCR)

To use GitHub Container Registry instead of Docker Hub:

1. **No secrets needed** - the workflow can use `${{ secrets.GITHUB_TOKEN }}` (automatically available)

2. **Modify the workflow**:
   - Uncomment the "Log in to GitHub Container Registry" step
   - Comment out the "Log in to Docker Hub" step
   - Change image names to: `ghcr.io/${{ github.repository_owner }}/ai-assistant-backend`

3. **Enable packages**:
   - Go to repository Settings → Actions → General
   - Under "Workflow permissions", select "Read and write permissions"

## Testing the Workflow

After setting up secrets:

1. Push to the `main` branch or manually trigger via Actions tab
2. Check the Actions tab to see the workflow progress
3. Once complete, images will be available in your registry

## Pulling Images on VPS

```bash
# Login to Docker Hub
docker login -u YOUR_USERNAME

# Pull images
docker pull YOUR_USERNAME/ai-assistant-backend:latest
docker pull YOUR_USERNAME/ai-assistant-frontend:latest
docker pull YOUR_USERNAME/ai-assistant-nginx:latest

# Or update docker-compose.yml to use your images and run:
docker compose pull
docker compose up -d
```
