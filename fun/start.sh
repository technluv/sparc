#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main installation function
main() {
    echo "Starting Fun project..."
    echo "Checking prerequisites..."

    # Check prerequisites
    if ! command_exists python3; then
        handle_error "Python 3 is not installed"
    fi

    if ! command_exists npm; then
        handle_error "npm is not installed"
    fi

    if ! command_exists ffmpeg; then
        handle_error "ffmpeg is not installed. Please install it using your package manager."
    fi

    # Backend setup
    echo "Setting up backend..."
    cd src/backend || handle_error "Backend directory not found"
    
    # Create and activate virtual environment
    echo "Creating Python virtual environment..."
    python3 -m venv venv || handle_error "Failed to create virtual environment"
    
    echo "Activating virtual environment..."
    source venv/bin/activate || handle_error "Failed to activate virtual environment"
    
    # Install backend dependencies
    echo "Installing backend dependencies..."
    pip install -r requirements.txt || handle_error "Failed to install backend dependencies"
    
    # Run backend tests
    echo "Running backend tests..."
    python -m pytest || handle_error "Backend tests failed"
    
    # Start backend server in background
    echo "Starting backend server..."
    uvicorn app:app --reload --port 8000 &
    BACKEND_PID=$!
    
    # Frontend setup
    cd ../frontend || handle_error "Frontend directory not found"
    
    # Install frontend dependencies
    echo "Installing frontend dependencies..."
    npm install || handle_error "Failed to install frontend dependencies"
    
    # Start frontend server
    echo "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    # Print success message
    echo -e "${GREEN}Setup completed successfully!${NC}"
    echo "Backend server running on http://localhost:8000"
    echo "Frontend server running on http://localhost:5173"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    
    # Wait for Ctrl+C
    wait $BACKEND_PID $FRONTEND_PID
}

# Cleanup function
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    deactivate 2>/dev/null
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
