#!/bin/bash

# Twiga Scan Production Deployment Script
set -e

echo "🚀 Starting Twiga Scan Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.example .env
    print_warning "Please edit .env file with your production values before continuing."
    print_warning "Especially update the passwords and secret keys!"
    exit 1
fi

# Load environment variables
source .env

# Generate secure passwords if not set
if [ "$POSTGRES_PASSWORD" = "your_secure_postgres_password" ]; then
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    sed -i "s/your_secure_postgres_password/$POSTGRES_PASSWORD/" .env
    print_status "Generated secure PostgreSQL password"
fi

if [ "$REDIS_PASSWORD" = "your_secure_redis_password" ]; then
    REDIS_PASSWORD=$(openssl rand -base64 32)
    sed -i "s/your_secure_redis_password/$REDIS_PASSWORD/" .env
    print_status "Generated secure Redis password"
fi

if [ "$SECRET_KEY" = "your_super_secret_key_here_make_it_long_and_random" ]; then
    SECRET_KEY=$(openssl rand -base64 64)
    sed -i "s/your_super_secret_key_here_make_it_long_and_random/$SECRET_KEY/" .env
    print_status "Generated secure application secret key"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p ssl
mkdir -p backups

# Set proper permissions
chmod 600 .env
chmod 755 deploy.sh

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check PostgreSQL
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U twiga_user -d twiga_scan > /dev/null 2>&1; then
    print_status "✅ PostgreSQL is healthy"
else
    print_error "❌ PostgreSQL is not healthy"
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli --raw incr ping > /dev/null 2>&1; then
    print_status "✅ Redis is healthy"
else
    print_error "❌ Redis is not healthy"
    exit 1
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Backend API is healthy"
else
    print_error "❌ Backend API is not healthy"
    exit 1
fi

# Check Frontend
if curl -f http://localhost:80 > /dev/null 2>&1; then
    print_status "✅ Frontend is healthy"
else
    print_error "❌ Frontend is not healthy"
    exit 1
fi

# Run database migrations and seed data
print_status "Setting up database..."
docker-compose -f docker-compose.prod.yml exec -T backend python seed_data.py

# Create SSL certificates (self-signed for development)
if [ ! -f ssl/cert.pem ]; then
    print_status "Creating self-signed SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

print_status "🎉 Deployment completed successfully!"

echo ""
echo "📋 Service Information:"
echo "  Frontend: http://localhost:80"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo "  Health Check: http://localhost:8000/health"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "  Update services: docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "🔒 Security Notes:"
echo "  - Change default passwords in .env file"
echo "  - Set up proper SSL certificates for production"
echo "  - Configure firewall rules"
echo "  - Set up monitoring and alerting"
echo ""
print_status "Twiga Scan is now running in production mode! 🦒" 