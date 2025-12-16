# D-TERR: Dominio de Inteligencia Territorial

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Habilitante  
> **Función:** Proveer información geoespacial e inteligencia territorial  

---

## Propósito

Gestionar la información geoespacial regional y proveer inteligencia territorial para la toma de decisiones.

---

## Módulos

### 1. Infraestructura de Datos Espaciales (IDE)

**Capas Base:**

- División político-administrativa (región, provincias, comunas)
- Localidades y entidades pobladas
- Red vial y conectividad
- Hidrografía
- Áreas protegidas y restricciones

**Capas Temáticas:**

- Zonificación PROT
- Localización de proyectos IPR
- Equipamiento e infraestructura
- Riesgos naturales
- Indicadores socioeconómicos por comuna
- **Seguridad Pública (D-SEG):**
  - Cobertura de cámaras de vigilancia (209 puntos)
  - Incidentes georreferenciados
  - Mapas de calor delictual
  - Zonas de intervención prioritaria

### 2. Observatorio Regional

**Dimensiones de Análisis:**

| Dimensión | Indicadores |
|-----------|-------------|
| Demográficos | Población, migración, envejecimiento |
| Económicos | PIB regional, empleo, empresas |
| Sociales | Pobreza, educación, salud |
| Ambientales | Recursos hídricos, suelos, biodiversidad |

**Funcionalidades:**

- Dashboards de indicadores regionales
- Comparativas intercomunales
- Series de tiempo y tendencias
- Alertas de indicadores críticos
- Informes automáticos para CORE

### 3. Visor Geoespacial

**Funcionalidades:**

- Visor web con capas activables
- Búsqueda por ubicación, proyecto, comuna
- Herramientas de medición y análisis
- Exportación de mapas e informes
- Integración con IDE Chile

**Funcionalidades de Seguridad Pública:**

- Visualización de cámaras activas/inactivas (209 puntos)
- Mapa de calor de incidentes (filtrable por tipo, fecha, comuna)
- Análisis de cobertura visual (zonas ciegas)
- Correlación espacial incidentes vs inversión en seguridad
- Exportación de mapas para Consejo Regional de Seguridad

---

## Entidades de Datos

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `CapaGeoespacial` | id, nombre, tipo, fuente, fecha_actualizacion, geometria_tipo | → Metadato |
| `IndicadorTerritorial` | id, nombre, dimension, formula, periodicidad | → MedicionIndicador[], ObjetivoERD (D-PLAN) |
| `MedicionIndicador` | id, indicador_id, comuna_id, periodo, valor | → IndicadorTerritorial, Comuna |
| `ZonaPROT` | id, codigo, nombre, macrozona_id, geometria, uso_principal | → UsoPermitido[], IPR (D-FIN) |
| `Camara` | id, codigo, tipo, ubicacion (GeoJSON), comuna_id, estado_operativo, radio_cobertura | → CapaGeoespacial |
| `Incidente` | id, timestamp, tipo, prioridad, ubicacion (GeoJSON), camara_origen, estado | → CapaGeoespacial |

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-PLAN** | Validación PROT, indicadores ERD |
| **D-FIN** | Localización geoespacial de IPR |
| **D-EJEC** | Localización de obras en ejecución |
| **D-COORD** | Mapa georreferenciado de actores |
| **D-GESTION** | Indicadores territoriales para H_gore |
| **D-SEG** | Georreferenciación de incidentes, cobertura de cámaras, mapas de calor delictual |
| **D-EVOL** | Analytics geoespacial avanzado |
| **D-GINT (FÉNIX)** | Anomalías territoriales críticas activan intervención Nivel III |

---

*Documento parte de GORE_OS v4.1*
