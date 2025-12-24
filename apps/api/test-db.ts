
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import { finipr } from './src/db/schema/fin';
import { desc } from 'drizzle-orm';
// import * as dotenv from 'dotenv';
// dotenv.config();

console.log('DATABASE_URL:', process.env.DATABASE_URL);

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://gore:gore_secret@localhost:5432/gore_os',
});

const db = drizzle(pool);

async function main() {
  try {
    console.log('Connecting...');
    const result = await db.select().from(finipr).orderBy(desc(finipr.fecha_rs)).limit(5);
    console.log('Success! Retrieved', result.length, 'rows.');
    console.log('First row:', result[0]);
  } catch (error) {
    console.error('Query Failed:', error);
  } finally {
    await pool.end();
  }
}

main();
