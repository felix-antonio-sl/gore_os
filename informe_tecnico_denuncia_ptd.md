# INFORME TÉCNICO
## Observaciones Críticas al Plan de Transformación Digital (Res. Ex. N° 02034)

---

**RESERVADO – USO INTERNO**

| Campo                       | Valor                                                                   |
| --------------------------- | ----------------------------------------------------------------------- |
| **Destinatario Principal**  | Sr. Oscar Manuel Crisóstomo Llanos, Gobernador Regional de Ñuble        |
| **Destinatario Secundario** | Honorable Consejo Regional de Ñuble (CORE)                              |
| **Copia a**                 | Administrador/a Regional, Jefe/a Unidad de Control, Auditoría Interna   |
| **Origen**                  | Asesoría Técnica – Administración Regional                              |
| **Materia**                 | Observaciones técnicas a Resolución Exenta N° 02034 de fecha 05.12.2025 |
| **Fecha**                   | 18 de diciembre de 2025                                                 |
| **Clasificación**           | Documento Técnico – No constituye Acto Administrativo                   |

---

## I. ANTECEDENTES

### 1.1 Del Acto Observado

Con fecha 05 de diciembre de 2025, mediante Resolución Exenta N° 02034, se aprobó el "Plan de Transformación Digital, Sistema de Transformación Digital (PMG-MEI 2025)" del Servicio Administrativo del Gobierno Regional de Ñuble.

Dicho plan fue elaborado por DIPLADE en conjunto con DAF para dar cumplimiento al requisito técnico establecido en el Decreto Exento N° 432/2024 del Ministerio de Hacienda, en el marco del Programa de Mejoramiento de la Gestión (PMG).

### 1.2 Del Proceso de Modernización Institucional en Curso

Paralelamente, este Gobierno Regional ha estado desarrollando un **proceso de modernización y ordenamiento de sus funciones operativas**, con un enfoque integral que abarca la gestión financiera, jurídica, territorial y de recursos institucionales.

Este proceso contempla:
- Una visión de largo plazo (5 años) con niveles de madurez progresivos
- Un modelo de integración de sistemas que conecta SIGFE, BIP, SISREC y otros sistemas obligatorios
- Un componente específico de gobernanza digital para cumplimiento de la Ley 21.180
- Arquitectura técnica unificada con capacidades de interoperabilidad

### 1.3 De la Presente Observación

Tras analizar en detalle el contenido del Plan de Transformación Digital aprobado, se han identificado **inconsistencias críticas** que, de no ser abordadas, podrían afectar la coherencia institucional, generar duplicación de esfuerzos y comprometer el cumplimiento normativo del GORE.

---

## II. MARCO COMPARATIVO: DOS ENFOQUES EN PARALELO

Antes de detallar las observaciones específicas, es necesario establecer un marco comparativo entre el Plan TDE aprobado (PTD) y el proceso de modernización institucional que viene desarrollando el GORE:

| Criterio                    | PTD (Res. Ex. 02034)                | Proceso de Modernización Institucional |
| --------------------------- | ----------------------------------- | -------------------------------------- |
| **Origen**                  | Requisito externo PMG-MEI 2025      | Iniciativa estratégica institucional   |
| **Horizonte**               | 4 años (2026-2029)                  | 5 años con madurez progresiva          |
| **Alineación ERD**          | ❌ Sin referencias                   | ✅ Alineado con ejes ERD 2024-2030      |
| **Arquitectura técnica**    | ❌ No definida                       | ✅ Modelo de integración documentado    |
| **Sistemas obligatorios**   | ❌ No incluidos (SIGFE, BIP, SISREC) | ✅ Integración como prioridad P0        |
| **Gobernanza de datos**     | ⏳ Postergada a 2029                 | ✅ Componente estructural desde inicio  |
| **Interoperabilidad**       | Iniciativa aislada                  | Principio arquitectónico transversal   |
| **Modelo de gobernanza**    | 15 iniciativas en silos             | Funciones integradas con dependencias  |
| **Cumplimiento Ley 21.180** | Parcial y tardío                    | Componente prioritario                 |

> [!WARNING]
> **Conclusión del marco comparativo:** El PTD aborda la transformación digital desde un enfoque de **cumplimiento normativo mínimo** (checkbox compliance), mientras que el proceso de modernización institucional propone una **transformación estructural integrada**.

---

## III. OBSERVACIONES TÉCNICAS

### 3.1 Desconexión Estratégica con Instrumentos Institucionales Vigentes

> [!CAUTION]
> **Hallazgo Crítico N° 1:** El Plan de Transformación Digital (PTD) no hace referencia alguna a:
> - La Estrategia Regional de Desarrollo (ERD) 2024-2030
> - El proceso de modernización operativa en desarrollo
> - Los Objetivos Estratégicos Institucionales (OEI) 2025-2026

**Fundamentación:**

El artículo 16 de la Ley N° 19.175 (LOC GORE) establece que los gobiernos regionales deben "diseñar, elaborar, aprobar y aplicar las políticas, planes, programas y proyectos de desarrollo para la región, **coherentes con la estrategia regional**".

Un plan de transformación digital que no se alinea con la ERD ni con los instrumentos de planificación institucional carece de la coherencia exigida por la normativa.

**Evidencia documental:**
- El PTD cita exclusivamente el Decreto N° 432/2024 (Ministerio de Hacienda) como marco de referencia.
- No existe ninguna referencia a la ERD, al PROT, ni a los OEI del GORE.

### 3.2 Diagnóstico Alarmante No Abordado Estructuralmente

El propio PTD reconoce brechas críticas en su diagnóstico:

| Subdimensión                       | Resultado | Nivel de Alarma |
| ---------------------------------- | --------- | --------------- |
| Interoperabilidad (PISEE)          | **0%**    | 🔴 Crítico       |
| Expediente Electrónico             | **8%**    | 🔴 Crítico       |
| Autenticación Digital (ClaveÚnica) | **8%**    | 🔴 Crítico       |
| Gobernanza de Datos                | **0%**    | 🔴 Crítico       |
| Analítica e Inteligencia           | **0%**    | 🔴 Crítico       |
| Calidad de Datos                   | **0%**    | 🔴 Crítico       |

> [!WARNING]
> **Hallazgo Crítico N° 2:** Las iniciativas propuestas en el PTD no atacan las causas raíz de estas brechas. Son intervenciones superficiales que postergan la gobernanza de datos hasta el año 2029.

**Implicancia normativa:**

La Ley N° 21.180 (Transformación Digital del Estado) establece la obligación de implementar el expediente electrónico y la interoperabilidad como requisitos de funcionamiento, no como metas a largo plazo. Un resultado de 8% en expediente electrónico y 0% en interoperabilidad **constituye un incumplimiento vigente** que el PTD no resuelve con la urgencia requerida.

### 3.3 Errores Materiales en Cronogramas

Se detectaron inconsistencias graves en las fechas de las iniciativas:

**PTD-D1-05 (Expediente Electrónico):**
- Línea 315 del documento: "Desplegar la solución en el ambiente de producción" → **Fecha inicio: 01-03-2026**
- Línea 299 del documento: "Estudiar la norma técnica de documentos y expedientes" → **Fecha inicio: 01-03-2027**

> [!CAUTION]
> **Hallazgo Crítico N° 3:** El cronograma indica un despliegue en producción (marzo 2026) **un año antes** de que se inicie el estudio de la norma técnica (marzo 2027). Esto es lógicamente imposible y evidencia una elaboración apresurada sin revisión técnica.

### 3.4 Ausencia de Arquitectura de Integración

El PTD presenta 15 iniciativas como proyectos independientes, sin:

- Modelo de datos unificado
- Arquitectura de integración (APIs, bus de servicios, PISEE)
- Dependencias formales entre iniciativas
- Secuencia lógica de implementación
- Identificación de sistemas a integrar (SIGFE, BIP, SISREC, DocDigital)

> [!WARNING]
> **Hallazgo Crítico N° 4:** La ausencia de arquitectura garantiza que las 15 iniciativas se conviertan en **15 silos tecnológicos adicionales**, agravando el problema de fragmentación que el GORE busca resolver.

### 3.5 Omisiones Materiales

El PTD **no contempla** iniciativas para:

| Sistema/Capacidad                     | Relevancia                               | Presente en PTD |
| ------------------------------------- | ---------------------------------------- | --------------- |
| Integración SIGFE                     | Obligatoria (contabilidad gubernamental) | ❌ No            |
| Integración BIP/SNI                   | Obligatoria (inversión pública)          | ❌ No            |
| Integración SISREC                    | Obligatoria (rendiciones CGR)            | ❌ No            |
| Portafolio IPR unificado              | Crítica para gestión                     | ❌ No            |
| Dashboard de ejecución presupuestaria | Crítica para control                     | ❌ No            |
| Expediente electrónico para convenios | Obligatoria (Ley 21.180)                 | ❌ No            |
| Ciberseguridad operativa              | Obligatoria (Ley 21.663 ANCI)            | ❌ No            |

---

## IV. ANÁLISIS DE RIESGOS

### 4.1 Riesgo de Incumplimiento Normativo

| Norma             | Obligación                        | Estado Actual   | Riesgo    |
| ----------------- | --------------------------------- | --------------- | --------- |
| Ley 21.180 (TDE)  | Expediente electrónico            | 8% cumplimiento | 🔴 Alto    |
| Ley 21.180 (TDE)  | Interoperabilidad vía PISEE       | 0% cumplimiento | 🔴 Crítico |
| DS 7/2020         | Autenticación con ClaveÚnica      | 8% cumplimiento | 🔴 Alto    |
| Ley 21.663 (ANCI) | Ciberseguridad de infraestructura | No abordado     | 🟠 Medio   |

### 4.2 Riesgo de Duplicación de Esfuerzos

La ejecución paralela del PTD y del proceso de modernización institucional generará:
- Duplicación de inversiones en desarrollo de software
- Conflictos de gobernanza entre equipos
- Deuda técnica por sistemas incompatibles
- Confusión institucional sobre la hoja de ruta oficial

### 4.3 Riesgo Fiscal

La inversión estimada del PTD (15 iniciativas × ~1.000-5.000 UTM) podría convertirse en gasto ineficiente si los desarrollos no se integran con la arquitectura institucional, requiriendo re-trabajo o descarte de soluciones.

---

## V. FUNDAMENTOS JURÍDICOS

### 5.1 Ley N° 19.175 (LOC GORE)

**Artículo 16:** Los gobiernos regionales deben diseñar planes "coherentes con la estrategia regional y los planes comunales".

**Artículo 24, letra a):** El Gobernador Regional debe "formular las políticas de desarrollo de la región".

Un plan de transformación digital que no se alinea con la ERD vulnera el principio de coherencia estratégica exigido por la LOC.

### 5.2 Ley N° 21.180 (Transformación Digital del Estado)

**Artículo 1°:** "Los órganos de la Administración del Estado deberán realizar sus actuaciones por medios electrónicos..."

**Artículo 19:** "Los órganos de la Administración del Estado deberán utilizar plataformas electrónicas interoperables..."

El PTD no resuelve el incumplimiento actual de estas obligaciones con la urgencia requerida.

### 5.3 Ley N° 21.663 (Ley Marco de Ciberseguridad - ANCI)

Establece obligaciones de ciberseguridad para órganos del Estado que el PTD no aborda de manera explícita ni sistemática.

### 5.4 Principio de Eficiencia (Ley 18.575)

**Artículo 5°:** "Los órganos de la Administración del Estado deberán cumplir sus cometidos coordinadamente y propender a la unidad de acción..."

La existencia de dos hojas de ruta paralelas sin coordinación vulnera este principio.

---

## VI. CONCLUSIONES

1. **El PTD fue elaborado como un instrumento de cumplimiento PMG**, no como una estrategia genuina de transformación digital institucional.

2. **Existe una desconexión total** entre el PTD y los instrumentos estratégicos del GORE (ERD, OEI, proceso de modernización en curso).

3. **El propio diagnóstico del PTD evidencia incumplimientos normativos** (Ley 21.180) que el plan no resuelve con la urgencia requerida.

4. **Los errores materiales en cronogramas** sugieren una elaboración apresurada sin revisión técnica adecuada.

5. **La ausencia de arquitectura de integración** garantiza la creación de nuevos silos tecnológicos.

6. **Ejecutar el PTD sin alineación con el proceso de modernización institucional generará duplicación de esfuerzos**, conflictos de gobernanza y gasto ineficiente.

---

## VII. SOLICITUDES

En mérito de lo expuesto, se solicita al Sr. Gobernador Regional:

### 7.1 Suspensión Cautelar

**PRIMERO:** Instruir la **suspensión temporal de la ejecución** de las iniciativas del Plan de Transformación Digital (Res. Ex. N° 02034) hasta que se complete su alineación con el proceso de modernización institucional en curso.

### 7.2 Comité de Alineación

**SEGUNDO:** Constituir un **Comité Técnico de Alineación TDE** integrado por:
- Administración Regional (coordinación)
- DIPLADE (planificación)
- DAF (recursos)
- Unidad de Informática/TI (ejecución técnica)
- Asesorías externas, si aplica

Con el mandato de:
a) Evaluar cada iniciativa del PTD en el contexto de la arquitectura institucional
b) Reformular cronogramas con coherencia técnica
c) Definir arquitectura de integración única
d) Presentar plan unificado en un plazo de 60 días hábiles

### 7.3 Informe al CORE

**TERCERO:** Remitir copia del presente informe al Consejo Regional para su conocimiento, en el marco de su función fiscalizadora (Art. 36, Ley 19.175).

### 7.4 Evaluación de Responsabilidades

**CUARTO:** Instruir a la Unidad de Control que evalúe si la elaboración del PTD sin coordinación con las iniciativas estratégicas del GORE constituye una falta al deber de coordinación establecido en la Ley 18.575.

---

## VIII. RESERVA

El presente informe constituye una observación técnica interna y no un acto administrativo. Su contenido es **RESERVADO** hasta que el Sr. Gobernador Regional disponga lo contrario.

La difusión no autorizada podría afectar procedimientos administrativos en curso y la imagen institucional del GORE.

---

**ASESORÍA TÉCNICA – ADMINISTRACIÓN REGIONAL**  
**GOBIERNO REGIONAL DE ÑUBLE**
