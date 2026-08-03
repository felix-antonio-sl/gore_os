# HANDOFF

Estado: continuidad histórica pendiente; runtime actual `NOT_RUN`

## Pendiente material

- Decidir si el perímetro del API requiere un control adicional compatible con
  autenticación Bearer; no modificar exposición sin una intervención autorizada.
- Incorporar una meta KPI solo cuando backend y modelo de datos declaren su fuente.
- Resolver la relación de “Mi Trabajo” por el identificador de dominio correcto.
- Corregir datos históricos y deuda de lint únicamente en cortes separados.

## Al retomar

1. Revalida Git, configuración redactada y runtime antes de afirmar disponibilidad.
2. Elige un solo pendiente y reproduce su comportamiento actual.
3. Conserva secretos y credenciales exclusivamente fuera del repo y del transcript.

## Riesgos

El worktree contiene evidencia y herramientas de auditoría ajenas a esta migración. No
las prepares, borres ni publiques por rutina. Un build histórico verde no prueba el
estado actual ni autoriza despliegue.
