#!/bin/bash

# Initial setup script for AI Assistant on Ubuntu VPS

set -e

echo "=================================================="
echo "AI Assistant - Initial Setup"
echo "=================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p nginx/conf.d
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p backend/app
mkdir -p frontend/dist

echo "✓ Directories created"
echo ""

# Copy environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo "✓ Please edit backend/.env with your settings"
fi

if [ ! -f frontend/.env ]; then
    echo "Creating frontend .env file..."
    cp frontend/.env.example frontend/.env
    echo "✓ Please edit frontend/.env with your settings"
fi

echo ""
echo "Building Docker images..."
docker compose build

echo ""
echo "=================================================="
echo "Setup complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and frontend/.env with your configuration"
echo "2. Start the services: docker compose up -d"
echo "3. Pull the Ollama model: docker exec -it ai-assistant-ollama ollama pull llama3.1:8b"
echo "4. (Optional) Set up HTTPS: sudo bash scripts/setup-ssl.sh"
echo ""
echo "Access the application at: http://localhost (or your domain)"
echo ""
