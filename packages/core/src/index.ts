import { z } from 'zod';

export const HealthCheckSchema = z.object({
  status: z.literal('ok'),
  timestamp: z.string(),
  service: z.string()
});

export type HealthCheck = z.infer<typeof HealthCheckSchema>;

export const LogSchema = z.object({
  id: z.string().uuid().optional(),
  message: z.string().min(1),
  createdAt: z.string().optional()
});

export type Log = z.infer<typeof LogSchema>;

export * from "./domain/d_fin/convenio";
export * from "./domain/d_fin/ipr";
export * from "./domain/d_fin/fondos";
export * from "./domain/d_fin/types";

