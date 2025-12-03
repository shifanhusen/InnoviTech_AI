# Makefile for AI Assistant Project

.PHONY: help setup build up down restart logs clean test backend-dev frontend-dev

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)AI Assistant - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Installation & Setup
setup: ## Initial setup (create env files, directories)
	@echo "$(BLUE)Setting up project...$(NC)"
	@mkdir -p nginx/conf.d certbot/conf certbot/www
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; fi
	@if [ ! -f frontend/.env ]; then cp frontend/.env.example frontend/.env; fi
	@echo "$(GREEN)✓ Setup complete$(NC)"
	@echo "$(YELLOW)Next: Edit backend/.env and frontend/.env with your configuration$(NC)"

install-deps: ## Install local development dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	@cd backend && pip install -r requirements.txt
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# Docker commands
build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker compose build
	@echo "$(GREEN)✓ Build complete$(NC)"

build-no-cache: ## Build Docker images without cache
	@echo "$(BLUE)Building Docker images (no cache)...$(NC)"
	@docker compose build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"

up: ## Start all services
	@echo "$(BLUE)Starting services...$(NC)"
	@docker compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@docker compose ps

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	@docker compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	@docker compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

ps: ## Show running containers
	@docker compose ps

# Logs
logs: ## Show logs for all services
	@docker compose logs -f

logs-backend: ## Show backend logs
	@docker compose logs -f backend

logs-frontend: ## Show frontend logs
	@docker compose logs -f frontend

logs-nginx: ## Show nginx logs
	@docker compose logs -f nginx

logs-ollama: ## Show ollama logs
	@docker compose logs -f ollama

logs-redis: ## Show redis logs
	@docker compose logs -f redis

# Ollama commands
ollama-pull: ## Pull LLaMA 3.1 8B model
	@echo "$(BLUE)Pulling LLaMA 3.1 8B model (this may take a while)...$(NC)"
	@docker exec -it ai-assistant-ollama ollama pull llama3.1:8b
	@echo "$(GREEN)✓ Model pulled$(NC)"

ollama-list: ## List available Ollama models
	@docker exec -it ai-assistant-ollama ollama list

ollama-shell: ## Access Ollama container shell
	@docker exec -it ai-assistant-ollama sh

# Redis commands
redis-cli: ## Access Redis CLI
	@docker exec -it ai-assistant-redis redis-cli

redis-flush: ## Clear all Redis data (WARNING: deletes all sessions)
	@echo "$(YELLOW)WARNING: This will delete all session data$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker exec -it ai-assistant-redis redis-cli FLUSHALL; \
		echo "$(GREEN)✓ Redis data cleared$(NC)"; \
	else \
		echo "$(BLUE)Cancelled$(NC)"; \
	fi

# Development commands
backend-dev: ## Run backend in development mode (local)
	@echo "$(BLUE)Starting backend dev server...$(NC)"
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 5001

frontend-dev: ## Run frontend in development mode (local)
	@echo "$(BLUE)Starting frontend dev server...$(NC)"
	@cd frontend && npm run dev

# Testing & Debugging
test-backend: ## Test backend API health
	@echo "$(BLUE)Testing backend API...$(NC)"
	@curl -s http://localhost:5001/api/health | jq

test-nginx: ## Test nginx configuration
	@echo "$(BLUE)Testing nginx configuration...$(NC)"
	@docker exec -it ai-assistant-nginx nginx -t

test-all: test-backend test-nginx ## Run all tests
	@echo "$(GREEN)✓ All tests passed$(NC)"

shell-backend: ## Access backend container shell
	@docker exec -it ai-assistant-backend bash

shell-frontend: ## Access frontend container shell
	@docker exec -it ai-assistant-frontend sh

shell-nginx: ## Access nginx container shell
	@docker exec -it ai-assistant-nginx sh

# Backup & Restore
backup: ## Backup Redis and Ollama data
	@echo "$(BLUE)Creating backup...$(NC)"
	@mkdir -p backups/redis backups/ollama
	@docker exec ai-assistant-redis redis-cli BGSAVE
	@sleep 5
	@docker cp ai-assistant-redis:/data/dump.rdb backups/redis/dump-$$(date +%Y%m%d-%H%M%S).rdb
	@echo "$(GREEN)✓ Backup complete$(NC)"

restore-redis: ## Restore Redis from backup (specify file: make restore-redis FILE=backup.rdb)
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make restore-redis FILE=backup.rdb$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring Redis from $(FILE)...$(NC)"
	@docker compose stop redis
	@docker cp $(FILE) ai-assistant-redis:/data/dump.rdb
	@docker compose start redis
	@echo "$(GREEN)✓ Restore complete$(NC)"

# Cleanup
clean: ## Stop services and remove containers
	@echo "$(BLUE)Cleaning up containers...$(NC)"
	@docker compose down
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-volumes: ## Stop services and remove containers + volumes (WARNING: deletes data)
	@echo "$(YELLOW)WARNING: This will delete all data including Redis sessions and Ollama models$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	else \
		echo "$(BLUE)Cancelled$(NC)"; \
	fi

clean-images: ## Remove all project Docker images
	@echo "$(BLUE)Removing Docker images...$(NC)"
	@docker compose down --rmi all
	@echo "$(GREEN)✓ Images removed$(NC)"

prune: ## Remove unused Docker resources
	@echo "$(BLUE)Pruning Docker resources...$(NC)"
	@docker system prune -f
	@echo "$(GREEN)✓ Prune complete$(NC)"

# SSL/HTTPS
ssl-setup: ## Run SSL setup script
	@echo "$(BLUE)Setting up SSL certificates...$(NC)"
	@bash scripts/setup-ssl.sh

# Deployment
deploy: build up ollama-pull ## Full deployment (build, start, pull model)
	@echo "$(GREEN)✓ Deployment complete$(NC)"
	@echo "$(YELLOW)Access the application at: http://localhost$(NC)"

update: ## Update application (pull latest, rebuild, restart)
	@echo "$(BLUE)Updating application...$(NC)"
	@git pull
	@docker compose build
	@docker compose up -d
	@echo "$(GREEN)✓ Update complete$(NC)"

# Monitoring
stats: ## Show Docker container stats
	@docker stats --no-stream

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(BLUE)Backend Health:$(NC)"
	@curl -s http://localhost:5001/api/health || echo "$(YELLOW)Backend not responding$(NC)"
	@echo ""
	@echo "$(BLUE)Nginx Health:$(NC)"
	@curl -s http://localhost/api/health || echo "$(YELLOW)Nginx not responding$(NC)"

# Documentation
docs: ## Generate API documentation URL
	@echo "$(BLUE)API Documentation available at:$(NC)"
	@echo "$(GREEN)http://localhost:5001/docs$(NC) - Interactive Swagger UI"
	@echo "$(GREEN)http://localhost:5001/redoc$(NC) - ReDoc alternative"

# Quick commands
dev: setup up ollama-pull ## Complete dev setup (setup, start, pull model)
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:5001$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:5001/docs$(NC)"
