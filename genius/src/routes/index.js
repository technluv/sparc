const express = require('express');
const { logger } = require('../utils/logger');
const { isConnected } = require('../database');

// Create router instance
const router = express.Router();

// Middleware to check database status
const checkDatabase = (req, res, next) => {
  if (!isConnected()) {
    logger.warn('Database not connected. Returning mock data.');
  }
  next();
};

// Basic routes
router.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to ENGINUS API',
    status: 'operational',
    database: isConnected() ? 'connected' : 'not connected'
  });
});

// Project routes
router.get('/projects', checkDatabase, (req, res) => {
  if (!isConnected()) {
    return res.json({ 
      message: 'Mock project data',
      data: [
        { id: 1, name: 'Sample Project 1', status: 'active' },
        { id: 2, name: 'Sample Project 2', status: 'pending' }
      ]
    });
  }
  res.json({ message: 'List of projects' });
});

router.post('/projects', checkDatabase, (req, res) => {
  if (!isConnected()) {
    return res.json({ 
      message: 'Mock project creation',
      data: { id: 3, ...req.body, status: 'created' }
    });
  }
  res.json({ message: 'Create new project' });
});

// Document routes
router.get('/documents', checkDatabase, (req, res) => {
  if (!isConnected()) {
    return res.json({ 
      message: 'Mock document data',
      data: [
        { id: 1, name: 'Sample Document 1.pdf', type: 'pdf' },
        { id: 2, name: 'Sample Document 2.doc', type: 'doc' }
      ]
    });
  }
  res.json({ message: 'List of documents' });
});

router.post('/documents', checkDatabase, (req, res) => {
  if (!isConnected()) {
    return res.json({ 
      message: 'Mock document upload',
      data: { id: 3, ...req.body, status: 'uploaded' }
    });
  }
  res.json({ message: 'Upload new document' });
});

// Report routes
router.get('/reports', checkDatabase, (req, res) => {
  if (!isConnected()) {
    return res.json({ 
      message: 'Mock report data',
      data: [
        { id: 1, name: 'Monthly Report', type: 'performance' },
        { id: 2, name: 'Status Report', type: 'status' }
      ]
    });
  }
  res.json({ message: 'List of reports' });
});

router.post('/reports', checkDatabase, (req, res) => {
  if (!isConnected()) {
    return res.json({ 
      message: 'Mock report generation',
      data: { id: 3, ...req.body, status: 'generated' }
    });
  }
  res.json({ message: 'Generate new report' });
});

// Setup routes function
function setupRoutes(app) {
  app.use('/api', router);
  logger.info('Routes initialized');
}

module.exports = { setupRoutes };
