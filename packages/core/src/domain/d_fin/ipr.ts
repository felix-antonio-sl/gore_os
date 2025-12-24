import { Schema } from "@effect/schema";
import { Option } from "effect";
import { FondoId, ViaEvaluacionId } from "./fondos.ts";
import { MontoPesos } from "./types.ts";

// --- Branded Types ---
export const IPRId = Schema.String.pipe(Schema.brand("IPRId"));
export type IPRId = Schema.Schema.Type<typeof IPRId>;

export const CodigoBIP = Schema.String.pipe(
  Schema.pattern(/^\d+$/), // Solo números por ahora
  Schema.brand("CodigoBIP")
);
export type CodigoBIP = Schema.Schema.Type<typeof CodigoBIP>;

// MontoPesos removed (imported)

// --- Enums ---
export enum EstadoCiclo {
  IDEA = "IDEA",
  PERFIL = "PERFIL",
  DISEÑO = "DISEÑO",
  EJECUCION = "EJECUCION",
  CIERRE = "CIERRE",
}

export enum EtapaActual {
  PREINVERSION = "PREINVERSION",
  SOLICITUD_RS = "SOLICITUD_RS",
  LICITACION = "LICITACION",
  CONTRATO = "CONTRATO",
  RECEPCION = "RECEPCION",
}

// --- Entity Definition ---
export const IPR = Schema.Struct({
  id: IPRId,
  // Use OptionFromNullOr to allow null/value in JSON (easier for DB/API)
  codigoBip: Schema.OptionFromNullOr(CodigoBIP), 
  nombre: Schema.String.pipe(Schema.minLength(5)),
  
  // Clasificación
  fondoId: FondoId,
  viaEvaluacionId: Schema.OptionFromNullOr(ViaEvaluacionId),
  
  // Financiero
  montoTotal: MontoPesos,
  
  // Ciclo de Vida
  estadoCiclo: Schema.Enums(EstadoCiclo),
  etapaActual: Schema.Enums(EtapaActual),
  fechaPostulacion: Schema.Date,
  
  // Relaciones (Solo IDs)
  responsableId: Schema.String, // FK a Funcionario
  comunaId: Schema.String,      // FK a Comuna
});

export type IPR = Schema.Schema.Type<typeof IPR>;

// --- Invariants / Business Rules ---

/**
 * Regla: Una IPR en etapa de EJECUCION debe tener un Código BIP asignado.
 */
export const validateEjecucionRequiresBIP = (ipr: IPR): boolean => {
  if (ipr.estadoCiclo === EstadoCiclo.EJECUCION) {
    return Option.isSome(ipr.codigoBip);
  }
  return true;
};
