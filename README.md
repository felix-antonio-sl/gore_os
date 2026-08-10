# GORE_OS

Sistema Story-First para la gestión institucional del Gobierno Regional de Ñuble,
con FastAPI, Next.js y PostgreSQL.

## Ejecutar

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
- [docs/README.md](docs/README.md) — catálogo de documentación vigente e histórica.
- [model/README.md](model/README.md) — modelo semántico y fuentes de datos.
