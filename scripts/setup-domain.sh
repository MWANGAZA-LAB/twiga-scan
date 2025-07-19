#!/bin/bash

# Domain and DNS Setup Script for Twiga Scan
set -e

echo "🌐 Setting up domain and DNS configuration for Twiga Scan..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if domain is provided
if [ -z "$1" ]; then
    print_error "Please provide a domain name"
    echo "Usage: $0 <domain-name>"
    echo "Example: $0 twiga-scan.com"
    exit 1
fi

DOMAIN=$1
WWW_DOMAIN="www.$DOMAIN"
API_DOMAIN="api.$DOMAIN"

print_status "Setting up DNS for domain: $DOMAIN"

# Create DNS configuration file
cat > dns-config.txt << EOF
# DNS Configuration for $DOMAIN
# Add these records to your DNS provider

# A Records (replace with your server IP)
$DOMAIN.          A       YOUR_SERVER_IP
$WWW_DOMAIN.      A       YOUR_SERVER_IP
$API_DOMAIN.      A       YOUR_SERVER_IP

# CNAME Records (if using CDN)
# www.$DOMAIN.    CNAME   $DOMAIN.

# MX Records (for email)
$DOMAIN.          MX      10 mail.$DOMAIN.

# TXT Records
$DOMAIN.          TXT     "v=spf1 include:_spf.google.com ~all"
$DOMAIN.          TXT     "google-site-verification=YOUR_VERIFICATION_CODE"

# CAA Records (for SSL certificates)
$DOMAIN.          CAA     0 issue "letsencrypt.org"
$DOMAIN.          CAA     0 issue "pki.goog"

# SRV Records (if needed)
# _sip._tcp.$DOMAIN.    SRV     0 5 5060 sip.$DOMAIN.
EOF

print_status "DNS configuration saved to dns-config.txt"

# Create Nginx configuration
cat > nginx-domain.conf << EOF
# Nginx configuration for $DOMAIN
server {
    listen 80;
    server_name $DOMAIN $WWW_DOMAIN $API_DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN $WWW_DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://frontend-service:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name $API_DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Backend API
    location / {
        proxy_pass http://backend-service:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

print_status "Nginx configuration saved to nginx-domain.conf"

# Create Let's Encrypt setup script
cat > setup-ssl.sh << EOF
#!/bin/bash
# Let's Encrypt SSL Certificate Setup

echo "🔒 Setting up SSL certificates for $DOMAIN..."

# Install certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d $DOMAIN -d $WWW_DOMAIN -d $API_DOMAIN

# Test renewal
sudo certbot renew --dry-run

echo "✅ SSL certificates configured successfully!"
echo "Certificates will auto-renew every 60 days"
EOF

chmod +x setup-ssl.sh

print_status "SSL setup script saved to setup-ssl.sh"

# Create deployment checklist
cat > deployment-checklist.md << EOF
# Deployment Checklist for $DOMAIN

## Pre-deployment
- [ ] Update DNS records (see dns-config.txt)
- [ ] Configure domain registrar
- [ ] Set up SSL certificates (run setup-ssl.sh)
- [ ] Update Kubernetes secrets with domain-specific values
- [ ] Configure environment variables

## DNS Records to Add
\`\`\`
$DOMAIN.          A       YOUR_SERVER_IP
$WWW_DOMAIN.      A       YOUR_SERVER_IP  
$API_DOMAIN.      A       YOUR_SERVER_IP
\`\`\`

## SSL Certificate
- Domain: $DOMAIN, $WWW_DOMAIN, $API_DOMAIN
- Provider: Let's Encrypt
- Auto-renewal: Enabled

## Environment Variables
\`\`\`
CORS_ORIGINS=https://$DOMAIN,https://$WWW_DOMAIN
DOMAIN=$DOMAIN
API_DOMAIN=$API_DOMAIN
\`\`\`

## Post-deployment
- [ ] Test all endpoints
- [ ] Verify SSL certificates
- [ ] Check monitoring and alerts
- [ ] Run load tests
- [ ] Update documentation
EOF

print_status "Deployment checklist saved to deployment-checklist.md"

print_status "🎉 Domain setup configuration completed!"
echo ""
echo "Next steps:"
echo "1. Update DNS records using dns-config.txt"
echo "2. Run setup-ssl.sh to get SSL certificates"
echo "3. Follow deployment-checklist.md"
echo "4. Update your Kubernetes configuration"
echo ""
echo "Your domains will be:"
echo "  🌐 Main: https://$DOMAIN"
echo "  🌐 WWW: https://$WWW_DOMAIN"
echo "  🔌 API: https://$API_DOMAIN" 