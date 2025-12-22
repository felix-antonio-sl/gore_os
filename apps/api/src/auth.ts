import { createMiddleware } from 'hono/factory';
import { createRemoteJWKSet, jwtVerify, JWTPayload } from 'jose';

// JWKS URI from Keycloak (internal Docker network)
// Note: From the API container, Keycloak is accessible as 'auth:8080'
const KEYCLOAK_REALM = 'gore_os';
const JWKS_URI = `http://auth:8080/realms/${KEYCLOAK_REALM}/protocol/openid-connect/certs`;

// Cache the JWKS
const jwks = createRemoteJWKSet(new URL(JWKS_URI));

export interface AuthPayload extends JWTPayload {
  preferred_username?: string;
  realm_access?: {
    roles: string[];
  };
  sub: string;
}

export const authMiddleware = createMiddleware<{
  Variables: {
    user: AuthPayload | null;
  };
}>(async (c, next) => {
  const authHeader = c.req.header('Authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    c.set('user', null);
    return next();
  }

  const token = authHeader.substring(7);

  try {
    const { payload } = await jwtVerify(token, jwks, {
      // We accept localhost issuer since the token is issued by Keycloak accessed via localhost on the browser
      // In production, this should be the public Keycloak URL
      issuer: [
        `http://localhost:8080/realms/${KEYCLOAK_REALM}`,
        `http://auth:8080/realms/${KEYCLOAK_REALM}`,
      ],
    });

    c.set('user', payload as AuthPayload);
  } catch (error) {
    console.error('JWT verification failed:', error);
    c.set('user', null);
  }

  return next();
});

// Helper to require authentication
export const requireAuth = createMiddleware<{
  Variables: {
    user: AuthPayload;
  };
}>(async (c, next) => {
  const user = c.get('user');
  
  if (!user) {
    return c.json({ error: 'Unauthorized' }, 401);
  }

  return next();
});
