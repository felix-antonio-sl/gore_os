import { pushSchema } from 'drizzle-kit/api';
import { db } from './db';
import * as schema from './schema';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://gore:gore_secret@db:5432/gore_os',
});

// For simplicity in this test, we'll use a raw SQL command to ensure the table exists
// instead of a complex drizzle-kit push if environment setup is tricky.
const setup = async () => {
    console.log('⏳ Setting up database table...');
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL
            );
        `);
        console.log('✅ Database table ready.');
    } catch (e) {
        console.error('❌ Database setup failed:', e);
    } finally {
        await pool.end();
    }
};

setup();
