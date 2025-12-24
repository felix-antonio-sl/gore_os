import { describe, it, expect } from "vitest";
import { Schema } from "@effect/schema";
import { IPR, IPRId, CodigoBIP, EstadoCiclo, EtapaActual, validateEjecucionRequiresBIP } from "../domain/d_fin/ipr.ts";
import { MontoPesos } from "../domain/d_fin/types.ts";
import { FondoId } from "../domain/d_fin/fondos.ts";
import { Option } from "effect";

describe("IPR Core Domain", () => {
    
    it("should validate a correct IPR", () => {
        const rawIPR = {
            id: "uuid-123",
            codigoBip: "4005001",
            nombre: "Construcción Plaza",
            fondoId: "FNDR",
            viaEvaluacionId: null,
            montoTotal: 1000000,
            estadoCiclo: "EJECUCION",
            etapaActual: "CONTRATO",
            fechaPostulacion: new Date().toISOString(),
            responsableId: "func-01",
            comunaId: "com-01"
        };
        
        // Decoding should pass strict checks
        const result = Schema.decodeUnknownSync(IPR)(rawIPR);
        
        expect(result.id).toBe("uuid-123");
        expect(result.montoTotal).toBe(1000000);
    });

    it("should fail validation if Monto is negative", () => {
        const invalidIPR = {
            id: "uuid-bad",
            nombre: "Bad Project",
            fondoId: "FNDR",
            montoTotal: -500, // Error
            estadoCiclo: "IDEA",
            etapaActual: "PREINVERSION",
            fechaPostulacion: new Date().toISOString(),
            responsableId: "func-01",
            comunaId: "com-01"
        };

        expect(() => Schema.decodeUnknownSync(IPR)(invalidIPR)).toThrow();
    });

    it("Invariant: Should require BIP if in EJECUCION", () => {
        const iprIdea = {
             id: "1" as IPRId,
             codigoBip: Option.none(),
             nombre: "Idea Project",
             fondoId: "FNDR" as FondoId,
             viaEvaluacionId: Option.none(),
             montoTotal: 0 as MontoPesos,
             estadoCiclo: EstadoCiclo.IDEA,
             etapaActual: EtapaActual.PREINVERSION,
             fechaPostulacion: new Date(),
             responsableId: "u1",
             comunaId: "c1"
        };
        expect(validateEjecucionRequiresBIP(iprIdea)).toBe(true);

        const iprExecNoBip = {
             ...iprIdea,
             estadoCiclo: EstadoCiclo.EJECUCION
        };
        expect(validateEjecucionRequiresBIP(iprExecNoBip)).toBe(false);
    });
});
