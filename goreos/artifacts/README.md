# GORE OS - Prisma Schema Artifacts

Este directorio contiene los **artefactos de diseño del esquema de base de datos** para GORE OS, utilizando Prisma ORM.

## 📁 Archivos

### `schema.prisma`
Esquema principal de Prisma que define:
- **Modelos de datos** para todas las entidades del sistema
- **Enumeraciones** (enums) para tipos y estados
- **Relaciones** entre entidades
- **Índices** para optimización de consultas
- **Extensiones PostgreSQL** (PostGIS, UUID-OSSP)

**Nota importante**: Este esquema está configurado para **Prisma ORM v7+**, donde la URL de conexión ya no se define en el bloque `datasource`.

### `prisma.config.ts`
Archivo de configuración para Prisma 7 que contiene:
- **URL de conexión a la base de datos** (movida desde `schema.prisma`)
- **Configuración del datasource**

Este archivo utiliza la nueva API de Prisma 7:
```typescript
import { defineConfig, env } from 'prisma/config';

export default defineConfig({
  datasource: {
    url: env('DATABASE_URL'),
  },
});
```

### `seed.ts`
Script de semilla (seed) para poblar la base de datos con datos iniciales.

## 🔄 Migración a Prisma 7

### Cambios principales

**Antes (Prisma 6.x):**
```prisma
datasource db {
  provider   = "postgresql"
  url        = env("DATABASE_URL")  // ❌ Deprecated en v7
  extensions = [postgis, uuid_ossp]
}
```

**Ahora (Prisma 7+):**

**schema.prisma:**
```prisma
datasource db {
  provider   = "postgresql"
  extensions = [postgis, uuid_ossp]
}
```

**prisma.config.ts:**
```typescript
import { defineConfig, env } from 'prisma/config';

export default defineConfig({
  datasource: {
    url: env('DATABASE_URL'),
  },
});
```

### Beneficios de la migración

1. **Mejor seguridad**: Las cadenas de conexión están separadas del esquema
2. **Mayor flexibilidad**: Configuración diferente por entorno
3. **Soporte para Accelerate**: Opción de usar `accelerateUrl` además de `adapter`

## 🚀 Uso en Implementación

Cuando se implemente este esquema en un proyecto real:

1. **Instalar dependencias:**
   ```bash
   npm install prisma @prisma/client
   npm install -D typescript @types/node
   ```

2. **Configurar variable de entorno:**
   ```bash
   # .env
   DATABASE_URL="postgresql://user:password@localhost:5432/goreos?schema=public"
   ```

3. **Generar cliente Prisma:**
   ```bash
   npx prisma generate
   ```

4. **Ejecutar migraciones:**
   ```bash
   npx prisma migrate dev
   ```

5. **Poblar datos iniciales:**
   ```bash
   npx prisma db seed
   ```

## 📚 Referencias

- [Prisma 7 Data Sources](https://pris.ly/d/config-datasource)
- [Prisma 7 Client Config](https://pris.ly/d/prisma7-client-config)
- [Prisma Config Reference](https://www.prisma.io/docs/orm/reference/prisma-config-reference)

## ⚠️ Nota sobre TypeScript

Los archivos `.ts` en este directorio pueden mostrar errores de TypeScript en el IDE porque **este es un directorio de artefactos de diseño** sin las dependencias de Prisma instaladas. Esto es esperado y normal.

La directiva `// @ts-nocheck` en `prisma.config.ts` suprime estos errores. Los archivos funcionarán correctamente cuando se usen en un proyecto con Prisma 7 instalado.

---

**Generado desde**: `kb_goreos_201_modelo_logico_prisma_koda.yml`  
**Fecha**: 2024-12-14  
**Versión Prisma**: 7.x
