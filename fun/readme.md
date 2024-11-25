# Fun Project

## Overview
This project follows the SPARC framework methodology, demonstrating proper project organization and documentation practices.

## Requirements
- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher

## Installation
Run the installation script:
```bash
./fun install
```

This will:
- Set up Python virtual environment
- Install backend dependencies
- Install frontend dependencies

## Project Structure
- Architecture/ - System design and component relationships
- Completion/ - Implementation status and final details
- Pseudocode/ - Logic and process representations
- Refinement/ - Development iterations and improvements
- Specification/ - Project requirements and specifications
- src/
  - backend/ - Python FastAPI backend
  - frontend/ - React frontend

## Running the Project
### Backend
```bash
cd src/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app:app --reload
```

### Frontend
```bash
cd src/frontend
npm run dev
```

## Documentation
Each component includes detailed documentation following SPARC framework guidelines.

## Contributing
Follow SPARC framework practices when contributing to this project.
