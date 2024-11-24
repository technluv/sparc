# ENGINUS Installation Guide

## Prerequisites

Ensure you have the following installed on your system:
- Node.js (v14.0.0 or higher)
- PostgreSQL (v12.0 or higher)
- Redis (v6.0 or higher)
- Docker (optional, for containerized deployment)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/enginus.git
cd enginus
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Configure environment variables
# Edit .env file with your settings:
# - Database credentials
# - Redis connection
# - Cloud storage credentials
# - API keys
```

### 3. Database Setup
```bash
# Create database
psql -U postgres
CREATE DATABASE enginus;

# Run migrations
npm run migrate
```

### 4. Install Dependencies
```bash
# Install backend dependencies
npm install

# Install frontend dependencies
cd client
npm install
cd ..
```

### 5. Build Application
```bash
# Build frontend
cd client
npm run build
cd ..

# Build backend
npm run build
```

### 6. Start Services
```bash
# Start Redis
redis-server

# Start application
npm run start
```

## Docker Installation

### Using Docker Compose
```bash
# Build and start containers
docker-compose up -d

# Check container status
docker-compose ps
```

## Common Issues and Solutions

### Database Connection Issues
1. Check PostgreSQL service status:
```bash
sudo service postgresql status
```
2. Verify database credentials in .env file
3. Ensure PostgreSQL is accepting connections:
```bash
sudo netstat -plunt | grep postgres
```

### Redis Connection Issues
1. Check Redis service status:
```bash
sudo service redis status
```
2. Verify Redis connection in .env file
3. Test Redis connection:
```bash
redis-cli ping
```

### Build Errors
1. Clear node modules and reinstall:
```bash
rm -rf node_modules
npm install
```
2. Clear build cache:
```bash
npm run clean
```

### Permission Issues
1. Check file permissions:
```bash
ls -la
```
2. Fix ownership if needed:
```bash
sudo chown -R $USER:$USER .
```

## Health Check

### Verify Installation
```bash
# Check backend status
curl http://localhost:3000/health

# Check frontend status
curl http://localhost:8080/health
```

### Run Tests
```bash
# Run all tests
npm run test

# Run specific test suite
npm run test:unit
npm run test:integration
```

## Troubleshooting

### Logs
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

### Debug Mode
```bash
# Start in debug mode
DEBUG=enginus:* npm run start
```

### Support
For additional support:
1. Check documentation in `/docs`
2. Submit issues on GitHub
3. Contact support team

## Maintenance

### Backup
```bash
# Backup database
npm run backup:db

# Backup uploaded files
npm run backup:files
```

### Updates
```bash
# Check for updates
npm run check:updates

# Apply updates
npm run update
```

### System Requirements

#### Minimum Requirements
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- Network: 100Mbps

#### Recommended Requirements
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB
- Network: 1Gbps
