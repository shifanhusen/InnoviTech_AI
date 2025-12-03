#!/bin/bash

# SSL Certificate Setup Script for Ubuntu VPS
# This script helps set up HTTPS using Certbot with Nginx

set -e

echo "=================================================="
echo "AI Assistant - SSL Certificate Setup"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Prompt for domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "Domain name is required!"
    exit 1
fi

read -p "Enter your email address for Let's Encrypt: " EMAIL

if [ -z "$EMAIL" ]; then
    echo "Email address is required!"
    exit 1
fi

echo ""
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""
read -p "Continue? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Step 1: Installing Certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

echo ""
echo "Step 2: Stopping Nginx temporarily..."
docker compose stop nginx

echo ""
echo "Step 3: Obtaining SSL certificate..."
certbot certonly --standalone \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --preferred-challenges http

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SSL certificate obtained successfully!"
    
    echo ""
    echo "Step 4: Updating Nginx configuration..."
    
    # Create SSL config from template
    cp nginx/conf.d/ssl.conf.example nginx/conf.d/ssl.conf
    sed -i "s/yourdomain.com/$DOMAIN/g" nginx/conf.d/ssl.conf
    
    # Remove default HTTP-only config
    # mv nginx/conf.d/default.conf nginx/conf.d/default.conf.backup
    
    echo ""
    echo "Step 5: Starting services..."
    docker compose up -d
    
    echo ""
    echo "Step 6: Setting up certificate renewal..."
    
    # Add renewal cron job
    (crontab -l 2>/dev/null || true; echo "0 3 * * * certbot renew --quiet --post-hook 'docker compose restart nginx'") | crontab -
    
    echo ""
    echo "=================================================="
    echo "✓ HTTPS Setup Complete!"
    echo "=================================================="
    echo ""
    echo "Your site is now accessible at:"
    echo "  https://$DOMAIN"
    echo "  https://www.$DOMAIN"
    echo ""
    echo "Certificate renewal is set up to run automatically."
    echo "You can manually test renewal with: certbot renew --dry-run"
    echo ""
else
    echo ""
    echo "✗ Failed to obtain SSL certificate."
    echo "Please check your domain DNS settings and try again."
    echo ""
    docker compose start nginx
    exit 1
fi
