import { describe, it, expect } from 'vitest';
import * as Schema from '@effect/schema/Schema';
import { Effect, Either } from 'effect';
import { CreateConvenioInput, Convenio } from '../domain/d_fin/convenio';

// 1. Simulación de Entrada (Input de API / Formulario)
const rawInput = {
    nombre: "Convenio MOP - Caminos Rurales",
    ministerio: "MOP",
    regionId: "550e8400-e29b-41d4-a716-446655440000", // UUID válido
    montoTotal: 1500000000, // 1.500 millones
    fechaFirma: "2025-03-15", // String fecha
    vigenciaAnios: 5
};

// 2. Capa de Negocio (Service Layer)
// Recibe input validado -> Aplica lógica -> Retorna Entidad
const createConvenioService = (input: CreateConvenioInput) => {
    return Effect.succeed({
        ...input,
        id: "c6a79810-7f9a-4f3e-8c6a-123456789abc", // ID generado por DB
        estado: "BORRADOR",
        createdAt: new Date(),
        updatedAt: new Date()
    }); // Retorna un Effect que tiene éxito con la entidad completa
};

describe('Recorrido Vertical: Entidad Convenio', () => {
    it('debe completar el ciclo Entrada -> Validación -> Procesamiento -> Salida', async () => {
        // PASO A: Decodificación y Validación (Frontera)
        // Transformamos el JSON crudo al tipo estricto del dominio
        const decodeEffect = Schema.decodeUnknown(CreateConvenioInput)(rawInput);
        
        // Ejecutamos la decodificación
        const decodedInput = await Effect.runPromise(decodeEffect);
        
        console.log("✅ Input Validado:", decodedInput);
        expect(decodedInput.nombre).toBe(rawInput.nombre);
        // Effect Schema convierte automáticamente string date a Date object si así se define
        expect(decodedInput.fechaFirma).toBeInstanceOf(Date); 

        // PASO B: Ejecución de Lógica de Negocio
        const serviceEffect = createConvenioService(decodedInput);
        const convenioCreado = await Effect.runPromise(serviceEffect);

        console.log("✅ Entidad Creada:", convenioCreado);

        // PASO C: Verificación de Salida (Contrato de Entidad)
        const isConvenioValido = Schema.is(Convenio)(convenioCreado);
        expect(isConvenioValido).toBe(true);
        expect(convenioCreado.estado).toBe("BORRADOR");
    });

    it('debe rechazar entradas invalidas en la frontera', async () => {
        const inputInvalido = { ...rawInput, montoTotal: -100 }; // Monto negativo prohibido
        
        const program = Schema.decodeUnknown(CreateConvenioInput)(inputInvalido);
        const exit = await Effect.runPromiseExit(program);

        expect(exit._tag).toBe("Failure");
        console.log("🛡️ Entrada rechazada correctamente (Monto negativo)");
    });
});
