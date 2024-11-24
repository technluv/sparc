require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { setupRoutes } = require('./routes');
const { setupDatabase } = require('./database');
const { logger } = require('./utils/logger');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Root route
app.get('/', (req, res) => {
  res.json({
    name: 'ENGINUS API',
    version: '1.0.0',
    description: 'Solar Power Plant Project Management System',
    endpoints: {
      api: '/api',
      health: '/health',
      docs: '/api-docs'
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

// API Documentation endpoint
app.get('/api-docs', (req, res) => {
  res.json({
    openapi: '3.0.0',
    info: {
      title: 'ENGINUS API Documentation',
      version: '1.0.0',
      description: 'API documentation for ENGINUS Solar Power Plant Project Management System'
    },
    servers: [
      {
        url: `http://localhost:${port}`,
        description: 'Development server'
      }
    ],
    paths: {
      '/api': {
        get: {
          summary: 'API Welcome endpoint',
          responses: {
            '200': {
              description: 'Welcome message'
            }
          }
        }
      },
      '/api/projects': {
        get: {
          summary: 'Get all projects',
          responses: {
            '200': {
              description: 'List of projects'
            }
          }
        },
        post: {
          summary: 'Create a new project',
          responses: {
            '200': {
              description: 'Project created successfully'
            }
          }
        }
      }
    }
  });
});

// Setup routes
setupRoutes(app);

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// Handle 404 errors
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: 'The requested resource was not found',
    availableEndpoints: {
      root: '/',
      api: '/api',
      health: '/health',
      docs: '/api-docs'
    }
  });
});

// Initialize services and start server
async function startServer() {
  try {
    // Setup database connection
    await setupDatabase();
    logger.info('Database connection established');

    // Start server
    app.listen(port, () => {
      logger.info(`Server running on port ${port}`);
      logger.info(`API Documentation available at http://localhost:${port}/api-docs`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    // Don't exit process on database connection failure
    logger.info('Starting server without database connection...');
    app.listen(port, () => {
      logger.info(`Server running on port ${port} (without database)`);
      logger.info(`API Documentation available at http://localhost:${port}/api-docs`);
    });
  }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (error) => {
  logger.error('Unhandled Rejection:', error);
  process.exit(1);
});

// Start the server
startServer();
