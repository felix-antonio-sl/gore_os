# HANDOFF

Estado: desarrollo activo enfocado en la bandeja de trabajo. El contrato vigente
del incremento está en [docs/GORE_OS_Bandeja_Trabajo.md](docs/GORE_OS_Bandeja_Trabajo.md).

## Pendiente material

- Decidir si el perímetro del API requiere un control adicional compatible con
  autenticación Bearer; no modificar exposición sin una intervención autorizada.
- Incorporar una meta KPI solo cuando backend y modelo de datos declaren su fuente.
- Consumir el candidato verificado desde una release fija, sin source bind ni
  recarga automática del checkout de desarrollo. La instalación y su salud se
  comprueban de forma independiente.
- Corregir datos históricos y deuda de lint únicamente en cortes separados.

## Al retomar

1. Revalida Git, configuración redactada y runtime antes de afirmar disponibilidad.
2. Elige un solo pendiente y reproduce su comportamiento actual.
3. Conserva secretos y credenciales exclusivamente fuera del repo y del transcript.

## Riesgos

El worktree contiene evidencia y herramientas de auditoría ajenas a esta migración. No
las prepares, borres ni publiques por rutina. Un build histórico verde no prueba el
estado actual ni autoriza despliegue.
