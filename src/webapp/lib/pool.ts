import { Pool } from 'pg';

// Initialize a single instance of the pool
const pool = new Pool({
  connectionString: process.env.POSTGRES_URL, // Ensure this variable is set in `.env.local`
  ssl: {
    rejectUnauthorized: false, // Set to false for development; true for production with a proper certificate
  },
});

export default pool;