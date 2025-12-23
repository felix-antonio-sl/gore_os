import { describe, it, expect } from 'vitest';
import { Effect, Exit } from 'effect';
import * as Schema from '@effect/schema/Schema';

describe('Effect-TS Sanity Check', () => {
    it('should run a basic Effect', async () => {
        const program = Effect.succeed("Hello GORE_OS");
        const result = await Effect.runPromise(program);
        expect(result).toBe("Hello GORE_OS");
    });

    it('should handle failures correctly', async () => {
        const program = Effect.fail("Something went wrong");
        const exit = await Effect.runPromiseExit(program);
        expect(Exit.isFailure(exit)).toBe(true);
    });

    it('should validate schemas', () => {
        const Person = Schema.Struct({
            name: Schema.String,
            age: Schema.Number
        });

        const valid = Schema.decodeUnknownSync(Person)({ name: "Felix", age: 30 });
        expect(valid).toEqual({ name: "Felix", age: 30 });

        expect(() => 
            Schema.decodeUnknownSync(Person)({ name: "Felix", age: "30" })
        ).toThrow();
    });
});
