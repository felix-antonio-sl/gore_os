import { Schema } from "@effect/schema";

export const FondoId = Schema.String.pipe(Schema.brand("FondoId"));
export type FondoId = Schema.Schema.Type<typeof FondoId>;

export const ViaEvaluacionId = Schema.String.pipe(Schema.brand("ViaEvaluacionId"));
export type ViaEvaluacionId = Schema.Schema.Type<typeof ViaEvaluacionId>;

export const Fondo = Schema.Struct({
  id: FondoId,
  nombre: Schema.String,
  codigo: Schema.String,
  descripcion: Schema.String,
  // Reglas de negocio básicas
  requiereAportePropio: Schema.Boolean,
});

export type Fondo = Schema.Schema.Type<typeof Fondo>;

export const ViaEvaluacion = Schema.Struct({
  id: ViaEvaluacionId,
  nombre: Schema.String,
  codigo: Schema.String,
  fondoId: FondoId, // Relación estricta
});

export type ViaEvaluacion = Schema.Schema.Type<typeof ViaEvaluacion>;

// Constantes conocidas (Valores semilla)
export const FONDOS = {
  FNDR: { id: "FNDR" as FondoId, nombre: "Fondo Nacional de Desarrollo Regional", codigo: "FNDR" },
  FRIL: { id: "FRIL" as FondoId, nombre: "Fondo Regional de Iniciativa Local", codigo: "FRIL" },
  FNDR_8: { id: "FNDR_8" as FondoId, nombre: "Fondo 8% (Comunidad)", codigo: "FNDR_8" },
} as const;
