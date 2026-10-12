# Web

Interfaz Next.js de la [bandeja de trabajo](../docs/GORE_OS_Bandeja_Trabajo.md)
de GORE_OS. `/dashboard` abre pendientes y enlaza sus lectores y acciones;
los panoramas y módulos autónomos archivados ya no se construyen.

```bash
npm run dev
npm run lint
npm run build
```

Ejecuta los comandos desde `web/`. El contrato de arquitectura y verificación vive
en [AGENTS.md](../AGENTS.md).

Para una prueba aislada, establece `NEXT_PUBLIC_API_URL` al API ficticio antes de
construir la web. Ese valor forma parte del build; cambiarlo al arrancar no modifica
un bundle ya compilado.
