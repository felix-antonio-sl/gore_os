# C2 - Contenedores de GORE_OS

## Abstract
La arquitectura de GORE_OS se descompone en contenedores dockerizados que separan responsabilidades de interfaz, lógica de negocio, persistencia y procesamiento asíncrono.

## Diagrama de Contenedores (Nivel 2)

```mermaid
C4Container
    title Diagrama de Contenedores - GORE_OS

    %% Actores
    Person(user, "Usuario", "Navegador Web / Móvil")

    %% Proxy y Frontend
    Container(proxy, "Reverse Proxy", "Caddy", "Terminación TLS, Routing, Compresión")
    Container(web, "Web App", "React + Vite", "SPA para interacción de usuario (Dashboard, Trámites)")

    %% Backend y Core
    Container(api, "API Server", "Bun + Hono + tRPC", "Manejo de peticiones síncronas, validación y orquestación")
    Container(worker, "Async Worker", "Bun + BullMQ", "Procesamiento de tareas pesadas (ETL, Reportes, Notificaciones)")

    %% Persistencia y Servicios
    ContainerDb(db, "Database", "PostgreSQL + PostGIS", "Almacenamiento relacional y geoespacial")
    ContainerDb(redis, "Cache & Queue", "Redis", "Colas de mensajes y caché de sesión")
    Container(idp, "Identity Provider", "Keycloak", "Gestión de sesiones, SSO y federación")
    ContainerDb(storage, "Object Storage", "MinIO / S3", "Almacenamiento de documentos y blobs")

    %% Relaciones
    Rel(user, proxy, "Navega", "HTTPS")
    Rel(proxy, web, "Sirve estáticos", "HTTP")
    Rel(proxy, api, "API Calls", "HTTP/JSON")

    Rel(web, api, "RPC Calls (Typed)", "tRPC")
    Rel(api, db, "Lee/Escribe (ORM)", "TCP/5432")
    Rel(api, redis, "Encola Jobs", "TCP/6379")
    Rel(api, idp, "Valida Tokens", "OIDC")
    Rel(api, storage, "Sube/Descarga docs", "S3 API")

    Rel(worker, redis, "Consume Jobs", "TCP/6379")
    Rel(worker, db, "Procesa Datos", "TCP/5432")
    Rel(worker, storage, "Genera Reportes", "S3 API")
```

## Definición de Contenedores

| Contenedor     | Tecnología            | Responsabilidad Principal                                     | Patrón de Diseño    |
| -------------- | --------------------- | ------------------------------------------------------------- | ------------------- |
| **Web App**    | React, Vite, Tailwind | Interfaz de usuario reactiva, gestión de estado local         | Component-Based UI  |
| **API Server** | Bun, Hono, tRPC       | Punto de entrada, validación (Zod), orquestación de servicios | RPC, Layered Arch   |
| **Worker**     | Bun, Effect-TS        | Procesos background, integraciones lentas, ETL                | Job Queue, Pipeline |
| **Database**   | PostgreSQL 16         | Fuente de verdad, integridad referencial, queries espaciales  | Relacional, ACID    |
| **IDP**        | Keycloak              | Autenticación, autorización, gestión de usuarios              | OAuth2 / OIDC       |

## Decisiones Clave

1.  **Bun como Runtime Unificado**: Utilizamos Bun tanto para el API como para los Workers para maximizar rendimiento y simplificar el toolchain (sin necesidad de ts-node o compilación compleja).
2.  **tRPC para Comunicación**: Eliminamos la necesidad de documentar APIs REST/GraphQL internamente al usar tRPC, garantizando tipado end-to-end entre Web y API.
3.  **PostGIS Nativo**: El componente territorial es *core* para el GORE, por lo que PostGIS está integrado en la DB principal y no como servicio separado.
