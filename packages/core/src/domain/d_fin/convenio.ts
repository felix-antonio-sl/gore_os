import * as Schema from "@effect/schema/Schema";

// Value Objects (Branded Types)
export const ConvenioId = Schema.UUID.pipe(Schema.brand("ConvenioId"));
export type ConvenioId = Schema.Schema.Type<typeof ConvenioId>;

export const MontoPesos = Schema.Number.pipe(
  Schema.int(),
  Schema.nonNegative(),
  Schema.brand("MontoPesos")
);
export type MontoPesos = Schema.Schema.Type<typeof MontoPesos>;

// Entity Definition
export const Convenio = Schema.Struct({
  id: ConvenioId,
  nombre: Schema.String.pipe(Schema.minLength(5)),
  ministerio: Schema.String,
  regionId: Schema.UUID,
  montoTotal: MontoPesos,
  fechaFirma: Schema.Date,
  vigenciaAnios: Schema.Number.pipe(Schema.int(), Schema.positive()),
  estado: Schema.Literal("BORRADOR", "VIGENTE", "CERRADO"),
  // Metadata de auditoría
  createdAt: Schema.Date,
  updatedAt: Schema.Date
});

export type Convenio = Schema.Schema.Type<typeof Convenio>;

// DTOs para creación (Omitiendo campos de sistema)
export const CreateConvenioInput = Convenio.pipe(
  Schema.omit("id", "createdAt", "updatedAt", "estado")
);
export type CreateConvenioInput = Schema.Schema.Type<typeof CreateConvenioInput>;
