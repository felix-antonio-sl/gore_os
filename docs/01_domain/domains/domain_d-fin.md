# D-FIN: Dominio de Financiamiento

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Núcleo (Dimensión Táctica)  
> **Función GORE:** FINANCIAR  

---

## Propósito

Gestión integral 360° del ciclo de vida de las inversiones públicas regionales, integrando cuatro perspectivas:

1. **Captación de Oportunidades** - Identificar y priorizar necesidades de desarrollo
2. **Gestión de Capital** - Maximizar el retorno en desarrollo regional
3. **Gestión de Ejecutores** - Administrar relaciones y capacidades institucionales
4. **Evaluación Continua** - Asegurar calidad y resultados (ex ante, ex durante, ex post)

> **Visión:** El GORE opera como gestor integral del desarrollo regional: capta oportunidades de intervención, administra capital público para generar retorno en desarrollo, cultiva relaciones con ejecutores, y evalúa continuamente resultados e impacto.

---

## Módulos

### 1. Captación de Oportunidades

**Fuentes de Captación:**

- ERD/Brechas - Brechas identificadas en Estrategia Regional
- Diagnósticos - Estudios territoriales, sectoriales, comunales
- Demanda ciudadana - OIRS, cabildos, consultas públicas
- Compromisos - Compromisos de Gobernador, CORE, autoridades
- Ejecutores - Propuestas de municipios, servicios, universidades
- Fondos disponibles - Convocatorias sectoriales, cofinanciamientos
- Emergencias - Situaciones de emergencia declarada

**Embudo de Oportunidades:**

```
DETECTADA (100%) → CALIFICADA (60%) → PRIORIZADA (35%) → EN NURTURING (20%) → CONVERTIDA (15%)
```

**Funcionalidades:**

- Registro de oportunidades desde múltiples fuentes
- Dashboard de embudo con métricas de conversión
- Calificación asistida (checklist de criterios)
- Alertas de oportunidades en ventana de tiempo
- Vinculación automática con brechas ERD

### 2. Capital Base

**Fuentes de Capital Regional:**

| Fuente | Descripción |
|--------|-------------|
| FNDR | Fondo Nacional Desarrollo Regional (principal) |
| FRPD | Fondo Regional Productividad y Desarrollo (Royalty) |
| Sectoriales | Transferencias de ministerios (consolidables) |
| Propios | Ingresos propios, patentes, multas |
| SIC | Saldo Inicial de Caja (arrastre) |

### 3. Portafolio IPR

**Taxonomía IPR:**

```
IPR (Término paraguas)
├── IDI (Iniciativa de Inversión) - Gasto de capital: obras, activos (S.31, S.33)
│   └── Requiere RS/AD de MDSF, Registro obligatorio en BIP
└── PPR (Programa Público Regional) - Gasto corriente/mixto (S.24)
    └── Requiere RF de DIPRES/SES (Glosa 06), Metodología Marco Lógico
```

**Roles de Actores en IPR:**

- POSTULANTE, FORMULADOR, PATROCINADOR, EVALUADOR, APROBADOR
- UNIDAD_FINANCIERA, UNIDAD_TECNICA, ENTIDAD_EJECUTORA, CONTRAPARTE, BENEFICIARIO

**Estados de IPR:**

- EN_CARTERA → EN_EVALUACION → APROBADA_RS → PRIORIZADA_ARI → EN_PRESUPUESTO
- EN_LICITACION → EN_EJECUCION → TERMINADA → CERRADA
- (SUSPENDIDA, CANCELADA)

### 4. Selector de Mecanismos

**IDI (Iniciativas de Inversión - S.31/S.33):**

| Código | Nombre | Tope UTM | Eval. | Ejecutor |
|--------|--------|----------|-------|----------|
| SNI | IDI General | Sin tope | RS MDSF | Público |
| FRIL | Fondo Reg.Inf.Local | 4.545 | GORE | Municipios |
| FRPD | Royalty (I+D+i) | Variable | Bifurc. | Habilitados |
| C33 | Circular 33 | Regla30% | GORE | Público |
| IRAL | Inv.Reg.Asig.Local | 7.000 | GORE | GORE |

**PPR (Programas Públicos Regionales - S.24):**

| Código | Nombre | Eval. | Ejecutor |
|--------|--------|-------|----------|
| G06 | PPR Glosa 06 | RF DIPRES | GORE directo |
| PPRT | PPR Transferencia | GORE | Entidad púb. |
| S8% | Subvención 8% | GORE | ONG/OSC/Muni |

### 5. Presupuesto Regional

**Ciclo Presupuestario:**

```
ENE-MAR: Ejecución año n
ABR-JUN: ARI (mayo)
JUL-SEP: Ley Presupuesto (agosto)
OCT-DIC: Aprobación CORE (diciembre)
ENE-DIC (n+1): Ejecución año n+1
```

### 6. Rendiciones

**Estados de Rendición:**

- PENDIENTE → EN_REVISION → APROBADA
- (OBSERVADA, EN_MORA, RECHAZADA)

**Funcionalidades:**

- Dashboard de rendiciones por estado
- Alertas de vencimiento (30, 15, 7 días)
- Semáforo de mora por ejecutor
- Integración SISREC (envío electrónico CGR)

### 7. Gestión de Ejecutores (SSOT)

**Rating de Ejecutor:**

| Dimensión | Peso | Indicadores |
|-----------|------|-------------|
| Historial rendiciones | 40% | % a tiempo, días mora promedio |
| Capacidad técnica | 25% | Equipo, metodologías, experiencia |
| Ejecución proyectos | 25% | % avance vs plan, sobrecostos |
| Gobernanza | 10% | Transparencia, controles, auditoría |

**Niveles:**

- A (≥85): Ejecutor confiable - Asignación preferente
- B (70-84): Ejecutor estándar - Monitoreo normal
- C (55-69): Ejecutor en observación - Supervisión reforzada
- D (<55): Ejecutor crítico - Restricción nuevas asignaciones

### 8. Evaluación Continua

- **EX ANTE:** Pertinencia, viabilidad, rating ejecutor, riesgo
- **EX DURANTE:** Avance físico/financiero, hitos, alertas
- **EX POST:** Productos, outcomes, impacto IDR, lecciones

### 9. IPR Problemáticas

**Clasificación:**

| Categoría | Criterio |
|-----------|----------|
| ESTANCADA | Sin avance >90 días |
| EN MORA | Rendiciones vencidas >30 días |
| SOBRECOSTO | Incremento >10% sobre RS |
| ATRASO CRÍTICO | Avance físico <50% |
| RIESGO LEGAL | Controversias, incumplimientos |

### 10. Retorno en Desarrollo (IDR)

**Dimensiones:**

- Económico: Empleo, PIB regional, productividad
- Social: Pobreza, acceso servicios, calidad de vida
- Territorial: Conectividad, equidad comunal
- Institucional: Capacidades locales, gobernanza

---

## Entidades de Datos

### Captación de Oportunidades

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Oportunidad` | id, titulo, fuente, estado_embudo, fecha_captacion, monto_estimado | → BrechaERD, Actor, IPR |
| `CalificacionOportunidad` | id, oportunidad_id, criterio, score, evaluador_id | → Oportunidad |
| `ActividadNurturing` | id, oportunidad_id, tipo, estado, resultado | → Oportunidad |
| `BrechaERD` | id, objetivo_erd_id, descripcion, magnitud | → ObjetivoERD |

### Portafolio y Ciclo de Vida

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `IPR` | id, codigo_bip, nombre, naturaleza, mecanismo_id, estado | → Oportunidad, Mecanismo, ObjetivoERD, Convenio[] |
| `ActorIPR` | id, ipr_id, actor_id, rol, fase, activo | → IPR, Actor |
| `RatingEjecutor` | id, actor_id, score_total, nivel (A/B/C/D) | → Actor |
| `EvaluacionIPR` | id, ipr_id, tipo, resultado, observaciones | → IPR |
| `IPRProblematica` | id, ipr_id, categoria, nivel_escalamiento | → IPR |
| `Mecanismo` | id, codigo, nombre, tope_utm, requiere_rs | → IPR[] |
| `Transferencia` | id, convenio_id, monto, fecha_giro, estado | → Convenio, Rendicion[] |
| `Rendicion` | id, transferencia_id, estado, monto_rendido | → Transferencia |
| `IDR` | id, ipr_id, dimension, indicador, valor_logrado | → IPR |

---

## Reglas Especiales por Mecanismo

- **FRIL**: Mínimo $100M, máximo 4.545 UTM (Ñuble); categorías A2/A3 no cuentan en límite 5 proyectos/comuna
- **Circular 33**: Conservación ≤30% costo reposición → sin RS MDSF; ANF requiere 20% aporte propio
- **FRPD**: Bifurcación post-selección: CTCI puro (exento RF) vs Fomento (requiere RF); máx 30% remuneraciones
- **Subvención 8%**: Plazo ejecución 8 meses; 10% puede ser asignación directa excepcional
- **PPR Transfer**: Exento evaluación DIPRES/SES; rendición vía SISREC; máx 5% gastos personal

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-PLAN** | IPR vinculadas a objetivos ERD |
| **D-EJEC** | Convenios (ejecución operativa) |
| **D-COORD** | Actor (entidad base de ejecutores) |
| **D-NORM** | Convenio (SSOT del acto administrativo) |

---

*Documento parte de GORE_OS v3.1*
