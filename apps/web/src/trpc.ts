import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@gore-os/api/src/trpc';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const trpc: ReturnType<typeof createTRPCReact<AppRouter>> = createTRPCReact<AppRouter>();
