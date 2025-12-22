import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './schema';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://gore:gore_secret@db:5432/gore_os',
});

export const db = drizzle(pool, { schema });
