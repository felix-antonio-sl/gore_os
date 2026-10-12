# GORE_OS

Bandeja de trabajo para funcionarios del Gobierno Regional de Ñuble: muestra
pendientes, responsable, estado y siguiente acción según la asignación y el rol.
El desarrollo sigue Story-First sobre FastAPI, Next.js y PostgreSQL.

Tras iniciar sesión, `/dashboard` abre la bandeja. Los detalles y acciones se abren
desde cada pendiente: compromisos, alertas, decisiones,
escalamientos, solicitudes de servicios, riesgos, firmas, rendiciones e IPR.
Las acciones disponibles proceden de la API y las categorías de la base de datos.
Los módulos autónomos anteriores se conservan en Git como historia recuperable.
Este propósito de producto no acredita adopción ni ratificación institucional.

## Ejecutar

Para instalar una revisión fija de API y web, usa la
[receta de producción](docs/GORE_OS_Despliegue.md). Los comandos siguientes son
para desarrollo local.

Con `goreos_db` disponible en la red Docker `visor_model_default` y la red
externa `web` configurada:

```bash
docker compose up -d api web
curl --fail http://localhost:8000/api/health
```

La interfaz queda disponible en <http://localhost:3000> y la documentación del API
en <http://localhost:8000/api/docs>.

Para crear también PostgreSQL desde cero, usa el perfil standalone. El arranque
carga únicamente el schema vigente, los vocabularios de referencia y el territorio
de Ñuble; no carga usuarios ni datos demo:

```bash
docker compose --profile standalone up -d
```

El baseline puede verificarse sin tocar `goreos_db` ni sus volúmenes:

```bash
./scripts/verify_fresh_db.sh
```

## Referencias

- [AGENTS.md](AGENTS.md) — contrato para cambiar y verificar el sistema.
- [Bandeja de trabajo](docs/GORE_OS_Bandeja_Trabajo.md) — recorrido, fuentes,
  autoridad y límites del incremento vigente.
- [Despliegue](docs/GORE_OS_Despliegue.md) — imágenes de la misma revisión,
  configuración privada y recuperación.
- [docs/README.md](docs/README.md) — catálogo de documentación vigente e histórica.
- [model/README.md](model/README.md) — modelo semántico y fuentes de datos.
