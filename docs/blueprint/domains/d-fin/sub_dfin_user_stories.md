# D-FIN Subdominio: User Stories

> Parte de: [D-FIN](../domain_d-fin.md) | [GORE_OS Blueprint](../../vision_general.md)  
> Función: Catálogo de Historias de Usuario del dominio financiero

---

## Catálogo SSOT

El catálogo canónico de User Stories se mantiene en:

**[kb_goreos_us_d-fin.yml](file:///Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories/kb_goreos_us_d-fin.yml)**

- **URN:** `urn:goreos:specs:user-stories:d-fin:1.0.0`
- **Total Stories:** 181+
- **Distribución:** Crítica (98), Alta (62), Media (18+)

---

## Historias por Proceso

### P1: Ingreso y Admisibilidad

| ID             | Título                          | Prioridad | Actor      |
| -------------- | ------------------------------- | --------- | ---------- |
| US-FIN-IPR-001 | Ver convocatorias unificadas    | Crítica   | Formulador |
| US-FIN-IPR-002 | Consultar árbol de decisión     | Crítica   | Formulador |
| US-FIN-IPR-003 | Ver documentos por mecanismo    | Crítica   | Formulador |
| US-FIN-IPR-004 | Cargar postulación digitalizada | Crítica   | Formulador |
| US-FIN-IPR-019 | Evaluar admisibilidad formal    | Crítica   | Analista   |
| US-FIN-GOB-001 | Sesión Pertinencia CDR          | Crítica   | CDR        |

### P2: Evaluación Técnico-Económica

| ID              | Título                         | Prioridad | Actor         |
| --------------- | ------------------------------ | --------- | ------------- |
| US-FIN-IPR-020  | Evaluar Track A (SNI)          | Crítica   | Analista      |
| US-FIN-IPR-021  | Evaluar Track B (G06) - Perfil | Crítica   | Analista      |
| US-FIN-IPR-022  | Evaluar Track B - Diseño MML   | Crítica   | Analista      |
| US-FIN-IPR-023  | Evaluar Track C (Simplificado) | Alta      | Analista      |
| US-FIN-FRIL-003 | Emitir RATE FRIL               | Crítica   | Analista FRIL |

### P3: Financiamiento

| ID              | Título                         | Prioridad | Actor           |
| --------------- | ------------------------------ | --------- | --------------- |
| US-FIN-PPTO-001 | Emitir CDP                     | Crítica   | Analista DAF    |
| US-FIN-PPTO-006 | Emitir CDP validando saldo     | Crítica   | Profesional DAF |
| US-FIN-APR-001  | Presentar distribución al CORE | Crítica   | Gobernador      |

### P5: Ejecución

| ID              | Título                  | Prioridad | Actor    |
| --------------- | ----------------------- | --------- | -------- |
| US-FIN-IPR-011  | Reportar avance mensual | Crítica   | Ejecutor |
| US-FIN-IPR-016  | Registrar adjudicación  | Alta      | Ejecutor |
| US-FIN-GEST-001 | Panel cartera ejecución | Crítica   | Analista |
| US-FIN-GEST-004 | Validar estado de pago  | Crítica   | Analista |

### P7: Cierre y Rendiciones

| ID              | Título                        | Prioridad | Actor            |
| --------------- | ----------------------------- | --------- | ---------------- |
| US-FIN-IPR-012  | Ingresar rendición SISREC     | Crítica   | Ejecutor         |
| US-FIN-REND-001 | Crear proyectos SISREC        | Crítica   | Enc. Rendiciones |
| US-FIN-REND-002 | Revisar rendiciones           | Crítica   | Enc. Rendiciones |
| US-FIN-REND-005 | Verificar elegibilidad Art.18 | Crítica   | Analista         |

---

## Historias por Módulo

### M7: Gestión de Ejecutores

| ID              | Título                             | Prioridad |
| --------------- | ---------------------------------- | --------- |
| US-FIN-EJEC-001 | Actualizar calificación ejecutor   | Alta      |
| US-FIN-EJEC-002 | Ver ranking de ejecutores          | Alta      |
| US-FIN-EJEC-003 | Alertar cuando ejecutor baje a C/D | Alta      |

### M8: Mesa de Ayuda

| ID               | Título                         | Prioridad |
| ---------------- | ------------------------------ | --------- |
| US-FIN-ASIST-001 | Acceder simulador rendiciones  | Alta      |
| US-FIN-ASIST-002 | Agendar capacitación           | Media     |
| US-FIN-ASIST-003 | Registrar consultas frecuentes | Media     |

### M9: Portafolio Estratégico

| ID              | Título                      | Prioridad |
| --------------- | --------------------------- | --------- |
| US-FIN-PORT-001 | Ver Panel de Portafolio     | Crítica   |
| US-FIN-PORT-002 | Registrar Teoría de Cambio  | Alta      |
| US-FIN-PORT-003 | Calcular PuntajeImpacto     | Crítica   |
| US-FIN-PORT-004 | Ver alertas concentración   | Alta      |
| US-FIN-PORT-005 | Marcar Proyecto Emblemático | Alta      |

### M10: Alertas 360°

| ID             | Título                     | Prioridad |
| -------------- | -------------------------- | --------- |
| US-FIN-360-001 | Ver pipeline oportunidades | Crítica   |
| US-FIN-360-005 | Calcular SaludIPR          | Crítica   |
| US-FIN-360-008 | Emitir alertas por fase    | Crítica   |

---

## Matriz de Trazabilidad

| Proceso            | Subproceso  | US Relacionadas         |
| ------------------ | ----------- | ----------------------- |
| P0: Selector       | Decisión    | US-FIN-IPR-001, 002     |
| P1: Ingreso        | Recepción   | US-FIN-IPR-004, GOB-004 |
| P1: Ingreso        | Pertinencia | US-FIN-GOB-001, 002     |
| P2: Evaluación     | Track A-D   | US-FIN-IPR-020-025      |
| P3: Financiamiento | CDP/CORE    | US-FIN-PPTO-001-006     |
| P5: Ejecución      | Seguimiento | US-FIN-GEST-001-008     |
| P7: Cierre         | Rendición   | US-FIN-REND-001-012     |

---

*Subdominio parte de D-FIN | GORE_OS Blueprint Integral v5.5*
