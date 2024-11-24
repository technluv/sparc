const { Pool } = require('pg');
const { logger } = require('../utils/logger');

let pool = null;

async function setupDatabase() {
  // Skip database setup if environment variables are not configured
  if (!process.env.DB_USER || !process.env.DB_HOST || !process.env.DB_NAME) {
    logger.warn('Database configuration not found. Running without database.');
    return null;
  }

  try {
    pool = new Pool({
      user: process.env.DB_USER,
      host: process.env.DB_HOST,
      database: process.env.DB_NAME,
      password: process.env.DB_PASSWORD,
      port: process.env.DB_PORT,
      // Add connection timeout
      connectionTimeoutMillis: 5000,
      // Add retry logic
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });

    // Test connection
    await pool.query('SELECT NOW()');
    logger.info('Database connection successful');
    return pool;
  } catch (error) {
    logger.warn('Database connection failed:', error.message);
    return null;
  }
}

function getPool() {
  if (!pool) {
    return {
      query: async () => {
        throw new Error('Database not connected');
      }
    };
  }
  return pool;
}

// Check if database is connected
function isConnected() {
  return pool !== null;
}

module.exports = {
  setupDatabase,
  getPool,
  isConnected
};
