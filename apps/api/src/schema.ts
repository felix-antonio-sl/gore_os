import { pgTable, text, timestamp, uuid } from 'drizzle-orm/pg-core';

export const logs = pgTable('logs', {
  id: uuid('id').primaryKey().defaultRandom(),
  message: text('message').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
