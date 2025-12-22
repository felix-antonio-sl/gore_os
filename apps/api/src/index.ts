import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { appRouter } from './trpc';
import { HealthCheckSchema } from '@gore-os/core';
import { authMiddleware, AuthPayload } from './auth';

const app = new Hono<{
  Variables: {
    user: AuthPayload | null;
  };
}>();

app.use('/*', cors());
app.use('/*', authMiddleware);

// tRPC handler using fetch adapter
app.all('/trpc/*', async (c) => {
  const user = c.get('user');
  
  return fetchRequestHandler({
    endpoint: '/trpc',
    req: c.req.raw,
    router: appRouter,
    createContext: () => ({ user }),
  });
});

app.get('/', (c) => {
  const response = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'api'
  };
  
  try {
    const validated = HealthCheckSchema.parse(response);
    return c.json(validated);
  } catch (e) {
    return c.json({ error: 'Validation Failed' }, 500);
  }
});

export default {
  port: 3000,
  fetch: app.fetch,
};
