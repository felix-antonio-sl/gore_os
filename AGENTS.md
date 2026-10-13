# AGENTS.md

## Misión

Desarrollar GORE_OS como sistema Story-First sobre FastAPI, Next.js y PostgreSQL. Cierra comportamiento vertical real desde historia y reglas de dominio hasta persistencia e interfaz.

## Orientación

- Lee `README.md`, `docs/README.md` y, si existe, el README del componente afectado.
- Identifica la historia, categoría y transición de estado antes de tocar código.
- Conserva la trazabilidad Story-First; no implementes UI, endpoint o tabla sin su comportamiento y autoridad claros.

## Arquitectura y datos

- Backend en FastAPI, frontend en `web/` y PostgreSQL como autoridad transaccional.
- Usa SQL parametrizado y las abstracciones existentes; no introduzcas ORM.
- Las transiciones de estado pasan por funciones/triggers de base de datos, no por actualizaciones directas.
- Preserva la univocidad de categorías y los invariantes entre API y DB.
- Reutiliza componentes de interfaz compartidos; no dupliques patrones locales.
- Las migraciones deben ser explícitas, revisables y compatibles con los datos existentes.

## Verificación

Ejecuta primero la prueba focal sobre la base ya preparada; añade controles por
la superficie afectada. Preparar una base no es un paso rutinario de toda revisión.

```bash
docker compose exec api pytest <ruta-o-k>
```

Si el cambio requiere recrear el esquema, identifica una base de prueba exclusiva
del encargo y su propietario. No recrees `goreos_test` compartida por conveniencia.
La preparación exige contenedor y nombre explícitos y rechaza el borrado con
conexiones abiertas; nunca usa `FORCE` ni termina sesiones ajenas:

```bash
./scripts/setup_test_db.sh <contenedor> <base_exclusiva_test> [usuario]
docker compose exec -e TEST_DB_NAME=<base_exclusiva_test> api pytest <ruta-o-k>
```

Para frontend añade lint/build cuando corresponda. Para cambios de journey,
verifica el flujo observable además de la suite. Conserva datos y trabajo
concurrente; un recurso ocupado requiere otra base o esperar a su propietario.

## Seguridad y entrega

- No expongas secretos ni datos reales en fixtures, logs o documentación.
- Preserva trabajo ajeno y evita limpiar el amplio worktree por rutina.
- Una suite verde no autoriza despliegue ni valida una decisión institucional.
