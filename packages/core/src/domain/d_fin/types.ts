import { Schema } from "@effect/schema";

export const MontoPesos = Schema.Number.pipe(
  Schema.int(),
  Schema.nonNegative(),
  Schema.brand("MontoPesos")
);
export type MontoPesos = Schema.Schema.Type<typeof MontoPesos>;
