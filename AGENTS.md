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

Prepara la base de pruebas con el circuito existente y ejecuta primero la prueba focal:

```bash
./scripts/setup_test_db.sh
docker compose exec api pytest <ruta-o-k>
npm --prefix web run lint
npm --prefix web run build
```

Amplía según el riesgo. Para cambios de journey, verifica el flujo observable además de la suite.

## Seguridad y entrega

- No expongas secretos ni datos reales en fixtures, logs o documentación.
- Preserva trabajo ajeno y evita limpiar el amplio worktree por rutina.
- Una suite verde no autoriza despliegue ni valida una decisión institucional.
