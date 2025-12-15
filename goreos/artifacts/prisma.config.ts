// @ts-nocheck - Artifact file for Prisma 7 (packages not installed in this design directory)
import { defineConfig, env } from 'prisma/config';

/**
 * GORE OS - Prisma Configuration
 * 
 * This file contains the database connection configuration for Prisma 7+.
 * The datasource URL has been moved here from schema.prisma as per Prisma 7 requirements.
 * 
 * NOTE: TypeScript errors in this file are expected in this artifact-only directory.
 * This configuration will work correctly when used in a project with Prisma ORM v7+ installed.
 * 
 * @see https://pris.ly/d/config-datasource
 * @see https://pris.ly/d/prisma7-client-config
 */
export default defineConfig({
  datasource: {
    url: env('DATABASE_URL'),
  },
});
