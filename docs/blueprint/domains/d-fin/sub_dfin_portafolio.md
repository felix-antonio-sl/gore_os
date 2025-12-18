# D-FIN Subdominio: Portafolio Estratégico

> Parte de: [D-FIN](../domain_d-fin.md) | [GORE_OS Blueprint](../../vision_general.md)  
> Función: Gestión estratégica del portafolio de inversiones como Banca Regional

---

## Paradigma: Banca de Inversión Regional

> El GORE opera como gestor integral del desarrollo regional: capta oportunidades, administra capital público para generar retorno en desarrollo, cultiva relaciones con ejecutores, y evalúa continuamente resultados e impacto.

---

## Captación de Oportunidades

### Fuentes
- ERD/Brechas - Estrategia Regional de Desarrollo
- Diagnósticos territoriales y sectoriales
- Demanda ciudadana - OIRS, cabildos
- Compromisos de Gobernador, CORE
- Fondos disponibles - Convocatorias sectoriales
- Emergencias declaradas (Glosa 02, Inciso 4)
- Propuestas de ejecutores

### Embudo de Oportunidades

```text
DETECTADA (100%) → CALIFICADA (60%) → PRIORIZADA (35%) → EN CULTIVO (20%) → CONVERTIDA (15%)
```

---

## PuntajeImpacto

Puntuación 0-100 que mide el retorno territorial esperado de una IPR.

| Dimensión     | Peso | Indicadores Clave                           |
| ------------- | ---- | ------------------------------------------- |
| Social        | 30%  | Beneficiarios, equidad, vulnerabilidad      |
| Económico     | 30%  | Empleos, productividad, encadenamientos     |
| Ambiental     | 25%  | Sostenibilidad, huella carbono, resiliencia |
| Institucional | 15%  | Gobernanza, transparencia, capacidad local  |

---

## Funcionalidades del Portafolio

- **Panel de Portafolio**: Visión consolidada por eje ERD, riesgo y retorno
- **Teoría de Cambio**: Hipótesis causal y supuestos clave por IPR
- **Análisis de Diversificación**: Alertas de concentración por eje, territorio o ejecutor
- **Proyectos Emblemáticos**: Seguimiento priorizado Ñuble 250
- **Simulador de Escenarios**: Proyección de impacto ante reasignación

---

## Alertas 360° por Ciclo

| Fase           | Tipo de Alerta           | Destinatario | Umbral                |
| -------------- | ------------------------ | ------------ | --------------------- |
| Formulación    | Documentación incompleta | Formulador   | 15 días sin avance    |
| Evaluación     | RS/ITF pendiente         | Analista     | 10 días sin respuesta |
| Financiamiento | Sesión CORE próxima      | Jefe DIPIR   | 5 días antes          |
| Ejecución      | Hito atrasado            | Supervisor   | 7 días de atraso      |
| Rendición      | Vencimiento SISREC       | Ejecutor/UCR | 30/15/7 días          |

### SaludIPR

Indicador 0-100 que consolida:
- Puntaje avance
- Puntaje rendiciones
- Puntaje riesgo
- Puntaje observaciones

---

## Entidades de Datos

| Entidad          | Atributos Clave                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| `Oportunidad`    | id, fuente, descripcion, estado_embudo, fecha_deteccion, ipr_vinculada_id                              |
| `FaseEmbudo`     | id, nombre, orden, criterios_avance                                                                    |
| `TeoriaCambio`   | id, ipr_id, hipotesis, supuestos_clave[], riesgos_logicos[]                                            |
| `PuntajeImpacto` | id, ipr_id, puntaje_social, puntaje_economico, puntaje_ambiental, puntaje_institucional, puntaje_total |
| `SaludIPR`       | id, ipr_id, puntaje_avance, puntaje_rendicion, puntaje_riesgo, salud_total                             |
| `AlertaCiclo`    | id, ipr_id, fase_ciclo, tipo_alerta, fecha_emision, estado                                             |

---

## KPIs

| Indicador                       | Fórmula                     | Meta |
| ------------------------------- | --------------------------- | ---- |
| Tasa conversión oportunidades   | Convertidas / Detectadas    | ≥15% |
| PuntajeImpacto promedio cartera | Promedio IPR en ejecución   | ≥70  |
| Diversificación por eje         | Ningún eje >35% presupuesto | ≤35% |
| Proyectos emblemáticos %        | Emblemáticos según plan     | ≥80% |
| Salud promedio cartera          | Promedio SaludIPR activas   | ≥75  |

---

## Referencias

- **ERD 2024-2030:** Estrategia Regional de Desarrollo Ñuble
- **Ñuble 250:** Proyectos Emblemáticos del Programa de Gobierno

---

*Subdominio parte de D-FIN | GORE_OS Blueprint Integral v5.5*
