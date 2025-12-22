import { Hono } from 'hono';
import { HealthCheckSchema } from '@gore-os/core';

const app = new Hono();

app.get('/', (c) => {
  const response = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'api'
  };
  
  // Validating with shared schema from core package
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
