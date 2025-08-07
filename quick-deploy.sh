#!/bin/bash

# 🚀 Twiga Scan Quick Deployment Script
# This script automates the deployment process for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists git; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_status "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration before continuing"
    fi
    
    # Create logs directory
    mkdir -p logs
    
    print_success "Environment setup completed"
}

# Function to build and start services
start_services() {
    local environment=${1:-development}
    
    print_status "Starting services in $environment mode..."
    
    if [ "$environment" = "production" ]; then
        docker-compose -f docker-compose.prod.yml up -d --build
    else
        docker-compose up -d --build
    fi
    
    print_success "Services started successfully"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend (basic connectivity)
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend health check failed (may still be starting)"
    fi
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
        print_success "Database is healthy"
    else
        print_error "Database health check failed"
        return 1
    fi
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    echo "=================="
    
    # Docker services
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "=============="
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to view logs
view_logs() {
    local service=${1:-""}
    
    if [ -z "$service" ]; then
        print_status "Showing all logs (Ctrl+C to exit)..."
        docker-compose logs -f
    else
        print_status "Showing $service logs (Ctrl+C to exit)..."
        docker-compose logs -f "$service"
    fi
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    docker-compose restart
    print_success "Services restarted"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "🚀 Twiga Scan Quick Deployment Script"
    echo "====================================="
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [env]     Start services (development|production)"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  status          Show service status and URLs"
    echo "  logs [service]  View logs (all services or specific service)"
    echo "  health          Check service health"
    echo "  setup           Setup environment (create .env, etc.)"
    echo "  cleanup         Stop services and clean up Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start in development mode"
    echo "  $0 start production   # Start in production mode"
    echo "  $0 logs backend       # View backend logs"
    echo "  $0 status             # Show service status"
    echo ""
}

# Main script logic
main() {
    local command=${1:-help}
    local option=${2:-}
    
    case $command in
        start)
            check_prerequisites
            setup_environment
            start_services "$option"
            check_health
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            check_health
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            view_logs "$option"
            ;;
        health)
            check_health
            ;;
        setup)
            check_prerequisites
            setup_environment
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
