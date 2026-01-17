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
    Container(proxy, "Reverse Proxy", "Nginx", "Terminación TLS, Routing, Static Files")
    Container(web, "Flask App", "Python + Flask", "SSR con Jinja2 + HTMX. Lógica de negocio y presentación.")

    %% Backend y Core
    Container(worker, "Celery Worker", "Python + Celery", "Procesamiento de tareas pesadas (ETL, Reportes, Correos)")
    Container(scheduler, "Celery Beat", "Python + Celery", "Planificador de tareas periódicas")

    %% Persistencia y Servicios
    ContainerDb(db, "Database", "PostgreSQL + PostGIS", "Almacenamiento relacional y geoespacial")
    ContainerDb(redis, "Cache & Broker", "Redis", "Colas de mensajes (Celery) y caché de sesión")
    Container(idp, "Identity Provider", "ClaveÚnica", "Autenticación externa delegada")
    ContainerDb(storage, "Object Storage", "MinIO / S3", "Almacenamiento de documentos y blobs")

    %% Relaciones
    Rel(user, proxy, "Navega", "HTTPS")
    Rel(proxy, web, "Proxies requests", "uWSGI/HTTP")
    Rel(web, db, "Lee/Escribe (SQLAlchemy)", "TCP/5432")
    Rel(web, redis, "Encola Jobs / Cache", "TCP/6379")
    Rel(web, idp, "Valida Tokens", "OIDC/OAuth")
    Rel(web, storage, "Sube/Descarga docs", "S3 API")

    Rel(worker, redis, "Consume Jobs", "TCP/6379")
    Rel(worker, db, "Procesa Datos", "TCP/5432")
    Rel(worker, storage, "Genera Reportes", "S3 API")
    Rel(scheduler, redis, "Dispara Tareas", "TCP/6379")
```

## Definición de Contenedores

| Contenedor    | Tecnología              | Responsabilidad Principal                                    | Patrón de Diseño  |
| ------------- | ----------------------- | ------------------------------------------------------------ | ----------------- |
| **Flask App** | Python, Flask, Gunicorn | Orquestación de peticiones, SSR (Jinja2), Endpoints HTMX     | MVC / App Factory |
| **Worker**    | Python, Celery          | Procesos background, integraciones lentas, ETL               | Distributed Queue |
| **Database**  | PostgreSQL 16           | Fuente de verdad, integridad referencial, queries espaciales | Relacional, ACID  |
| **Redis**     | Redis                   | Broker de mensajería y almacenamiento de sesiones volátiles  | Key-Value Store   |
| **IDP**       | ClaveÚnica              | Autenticación externa, gestión de usuarios                   | OAuth2 / OIDC     |

## Decisiones Clave

1. **Python como Lenguaje Único**: Unificamos backend y scripting en Python para aprovechar el ecosistema de ciencia de datos y geoespacial (Pandas, GeoPandas) nativo en el gobierno.
2. **Server-Side Rendering (Hypermedia)**: Eliminamos la complejidad del `JSON-over-the-wire` (React) en favor de `HTML-over-the-wire` (HTMX), simplificando la gestión de estado y reduciendo la latencia percibida.
3. **PostGIS Nativo**: El componente territorial es *core* para el GORE, por lo que PostGIS está integrado en la DB principal y no como servicio separado.
