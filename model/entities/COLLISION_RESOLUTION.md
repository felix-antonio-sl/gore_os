# Resolución de Colisiones Domain-Free

## Mapeo de Resoluciones Semánticas

| Colisión                    | Origen 1 | Origen 2 | Nuevo ID 1                      | Nuevo ID 2                    | Razón                                      |
| --------------------------- | -------- | -------- | ------------------------------- | ----------------------------- | ------------------------------------------ |
| ACCIDENTE-LABORAL           | BACK     | ORG      | ENT-ACCIDENTE_LABORAL_BACK      | ENT-ACCIDENTE_LABORAL         | BACK es registro, ORG es la entidad master |
| ACTA-CONSEJO                | GOB      | GOV      | ENT-ACTA_CONSEJO                | ENT-ACTA_CORE                 | GOB genérico, GOV específico del CORE      |
| AUDIT-LOG                   | FIN      | TDE      | ENT-AUDIT_LOG_FINANCIERO        | ENT-AUDIT_LOG_TECNICO         | Ámbito financiero vs técnico               |
| CERTIFICADO-RECEPTOR-FONDOS | EJEC     | EJE      | ENT-CERTIFICADO_RECEPTOR_FONDOS | -                             | EJEC y EJE son aliases, usar uno solo      |
| CHECKLIST-CIERRE            | EJE      | SYS      | ENT-CHECKLIST_CIERRE_PROYECTO   | ENT-CHECKLIST_CIERRE_GENERICO | Proyecto vs genérico                       |
| DASHBOARD                   | SYS      | TDE      | ENT-DASHBOARD_SISTEMA           | ENT-DASHBOARD_ANALITICO       | Sistema operativo vs analítico             |
| DESCUENTO-LEGAL             | BACK     | FIN      | ENT-DESCUENTO_LEGAL             | -                             | Consolidar (son el mismo concepto)         |
| ESTRATEGIA-COMUNICACIONAL   | BACK     | PLAN     | ENT-ESTRATEGIA_COMUNICACIONAL   | -                             | Consolidar (mismo concepto)                |
| FONDO-CONCURSABLE           | EJEC     | SOC      | ENT-FONDO_CONCURSABLE           | -                             | Consolidar (mismo concepto)                |
| INDICADOR-GENERO            | PLAN     | SOC      | ENT-INDICADOR_GENERO            | -                             | Consolidar (mismo concepto)                |
| LIQUIDACION-SUELDO          | BACK     | FIN      | ENT-LIQUIDACION_SUELDO          | -                             | Consolidar (mismo concepto)                |
| NOTIFICACION                | SYS      | TDE      | ENT-NOTIFICACION_SISTEMA        | ENT-NOTIFICACION_USUARIO      | Sistema vs usuario                         |
| PLAN-CAPACITACION           | BACK     | ORG      | ENT-PLAN_CAPACITACION           | -                             | Consolidar (mismo concepto)                |
| PLAN-INDUCCION              | BACK     | ORG      | ENT-PLAN_INDUCCION              | -                             | Consolidar (mismo concepto)                |
| REMUNERACION                | BACK     | FIN      | ENT-REMUNERACION                | -                             | Consolidar (mismo concepto)                |
| RENTABILIDAD-SOCIAL         | FIN      | ORM      | ENT-RENTABILIDAD_SOCIAL         | -                             | Consolidar (ORM parece typo)               |

## Acciones

### Mantener Ambos (6 casos)
- ACCIDENTE-LABORAL (back vs master)
- ACTA-CONSEJO vs ACTA-CORE
- AUDIT-LOG (financiero vs técnico)
- CHECKLIST-CIERRE (proyecto vs genérico)
- DASHBOARD (sistema vs analítico)
- NOTIFICACION (sistema vs usuario)

### Fusionar/Consolidar (10 casos)
- CERTIFICADO-RECEPTOR-FONDOS → usar ENT-CERTIFICADO_RECEPTOR_FONDOS (tags: [EJEC, EJE])
- DESCUENTO-LEGAL → ENT-DESCUENTO_LEGAL (tags: [BACK, FIN])
- ESTRATEGIA-COMUNICACIONAL → ENT-ESTRATEGIA_COMUNICACIONAL (tags: [BACK, PLAN])
- FONDO-CONCURSABLE → ENT-FONDO_CONCURSABLE (tags: [EJEC, SOC])
- INDICADOR-GENERO → ENT-INDICADOR_GENERO (tags: [PLAN, SOC])
- LIQUIDACION-SUELDO → ENT-LIQUIDACION_SUELDO (tags: [BACK, FIN])
- PLAN-CAPACITACION → ENT-PLAN_CAPACITACION (tags: [BACK, ORG])
- PLAN-INDUCCION → ENT-PLAN_INDUCCION (tags: [BACK, ORG])
- REMUNERACION → ENT-REMUNERACION (tags: [BACK, FIN])
- RENTABILIDAD-SOCIAL → ENT-RENTABILIDAD_SOCIAL (tags: [FIN])
