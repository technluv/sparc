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
    echo "Starting Fun project installation..."

    # Check prerequisites
    echo "Checking prerequisites..."

    if ! command_exists python3; then
        handle_error "Python 3 is not installed"
    fi

    if ! command_exists npm; then
        handle_error "npm is not installed"
    fi

    # Backend setup
    echo "Setting up backend..."
    cd "$(dirname "$0")/src/backend" || handle_error "Backend directory not found"
    python3 -m venv venv || handle_error "Failed to create virtual environment"

    # Activate virtual environment based on OS
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate || handle_error "Failed to activate virtual environment"
    else
        source venv/bin/activate || handle_error "Failed to activate virtual environment"
    fi

    # Install backend dependencies
    echo "Installing backend dependencies..."
    pip install -r requirements.txt || handle_error "Failed to install backend dependencies"
    echo -e "${GREEN}Backend dependencies installed successfully${NC}"

    # Deactivate virtual environment
    deactivate

    # Frontend setup
    echo "Setting up frontend..."
    cd ../frontend || handle_error "Frontend directory not found"

    # Install frontend dependencies
    echo "Installing frontend dependencies..."
    npm install || handle_error "Failed to install frontend dependencies"
    echo -e "${GREEN}Frontend dependencies installed successfully${NC}"

    cd ../..

    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo "To start the backend:"
    echo "  1. cd src/backend"
    echo "  2. source venv/bin/activate (or 'venv\Scripts\activate' on Windows)"
    echo "  3. uvicorn app:app --reload"
    echo ""
    echo "To start the frontend:"
    echo "  1. cd src/frontend"
    echo "  2. npm run dev"
}

# Check if script is being sourced or executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    main "$@"
fi
