#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Error handling
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo -e "${RED}\"${last_command}\" command failed with exit code $?.${NC}"' EXIT

# Logger function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $1${NC}"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed. Please install Node.js v14.0.0 or higher."
        exit 1
    fi
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        error "PostgreSQL is not installed. Please install PostgreSQL v12.0 or higher."
        exit 1
    fi
    
    # Check Redis
    if ! command -v redis-cli &> /dev/null; then
        error "Redis is not installed. Please install Redis v6.0 or higher."
        exit 1
    fi
    
    log "System requirements check passed."
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log "Created .env file from template."
        else
            error ".env.example not found."
            exit 1
        fi
    else
        warn ".env file already exists. Skipping..."
    fi
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    # Source environment variables
    if [ -f .env ]; then
        source .env
    else
        error ".env file not found."
        exit 1
    fi
    
    # Create database if it doesn't exist
    psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'enginus'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE enginus"
    
    # Run migrations
    npm run migrate
    
    log "Database setup completed."
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Backend dependencies
    npm install
    
    # Frontend dependencies
    if [ -d "client" ]; then
        cd client
        npm install
        cd ..
    fi
    
    log "Dependencies installed successfully."
}

# Build application
build_application() {
    log "Building application..."
    
    # Build frontend
    if [ -d "client" ]; then
        cd client
        npm run build
        cd ..
    fi
    
    # Build backend
    npm run build
    
    log "Application built successfully."
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start Redis if not running
    if ! pgrep redis-server > /dev/null; then
        redis-server &
        log "Redis server started."
    else
        warn "Redis server already running."
    fi
    
    # Start application
    npm run start &
    
    log "Services started successfully."
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait for services to start
    sleep 5
    
    # Check backend
    if curl -s http://localhost:3000/health > /dev/null; then
        log "Backend health check passed."
    else
        error "Backend health check failed."
        exit 1
    fi
    
    # Check frontend
    if curl -s http://localhost:8080/health > /dev/null; then
        log "Frontend health check passed."
    else
        error "Frontend health check failed."
        exit 1
    fi
    
    log "Health check completed successfully."
}

# Main installation process
main() {
    log "Starting ENGINUS installation..."
    
    check_requirements
    setup_environment
    setup_database
    install_dependencies
    build_application
    start_services
    health_check
    
    log "ENGINUS installation completed successfully!"
}

# Run main function
main
