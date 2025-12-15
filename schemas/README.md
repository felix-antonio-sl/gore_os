# GORE OS - KODA Schemas

Este directorio contiene los esquemas JSON Schema para validación de artefactos KODA (Knowledge-Oriented Document Architecture).

## 📄 Archivos

### `koda-schema.json`

Esquema de validación para todos los artefactos de conocimiento KODA en el proyecto GORE OS.

**Propósito**: Proporcionar validación automática de la estructura y contenido de los archivos YAML que documentan el conocimiento del sistema.

**Uso**: Los archivos KODA YAML incluyen una directiva en la primera línea que referencia este esquema:

```yaml
# yaml-language-server: $schema=../schemas/koda-schema.json
```

## 🏗️ Estructura KODA

Los artefactos KODA siguen una estructura estándar:

### Secciones Obligatorias

1. **Manifest**: Información de identificación y control
   - `URN`: Identificador único (formato: `urn:knowledge:org:project:id:name`)
   - `Version`: Versión semántica (formato: `X.Y.Z`)
   - `Status`: Estado del documento (`Draft`, `Review`, `Approved`, `Published`, `Deprecated`, `Archived`)
   - `Classification`: Clasificación (`Strategic`, `Tactical`, `Operational`, `Reference`, `Template`)
   - `Stability`: Estabilidad (`Stable`, `Evolving`, `Experimental`, `Deprecated`)

2. **Metadata**: Metadatos descriptivos
   - `Title`: Título del artefacto
   - `Description`: Descripción detallada
   - `Domain`: Dominio principal
   - `Subdomain`: Subdominio (opcional)
   - `Author`: Autor o equipo
   - `Created`: Fecha de creación (YYYY-MM-DD)
   - `Updated`: Fecha de actualización (YYYY-MM-DD)
   - `Ctx`: Contexto de uso
   - `LLM_Parsing_Instructions`: Instrucciones para LLMs
   - `Tags`: Etiquetas para búsqueda

### Secciones Opcionales

3. **Referencias**: Enlaces a otros artefactos
   - `Internas`: Referencias dentro del proyecto
   - `Externas`: Referencias a recursos externos

4. **Contenido específico del dominio**: Varía según el tipo de artefacto

## 🔍 Validación

Los IDEs compatibles con YAML Language Server (como VS Code, Windsurf, Cursor) utilizarán automáticamente este esquema para:

- ✅ Validar la estructura del documento
- ✅ Proporcionar autocompletado
- ✅ Mostrar errores de validación en tiempo real
- ✅ Sugerir valores válidos para enumeraciones

## 📚 Artefactos KODA en GORE OS

Los artefactos KODA en este proyecto incluyen:

- **kb_goreos_000_*.yml**: Documentos fundacionales y visión estratégica
- **kb_goreos_001_*.yml**: Arquitectura general del sistema
- **kb_goreos_1XX_*.yml**: Especificaciones de dominios funcionales
- **kb_goreos_2XX_*.yml**: Modelos de datos y esquemas
- **kb_goreos_3XX_*.yml**: Catálogos de procesos
- **kb_goreos_4XX_*.yml**: Matrices de roles y permisos
- **kb_goreos_5XX_*.yml**: Integraciones externas
- **kb_goreos_6XX_*.yml**: Diseños de UI
- **kb_goreos_7XX_*.yml**: Planes de migración
- **kb_goreos_8XX_*.yml**: Roadmaps de implementación
- **kb_goreos_9XX_*.yml**: Estrategias de testing

## 🔗 Referencias

- [JSON Schema Specification](https://json-schema.org/)
- [YAML Language Server](https://github.com/redhat-developer/yaml-language-server)
- [KODA Framework Documentation](../../docs/)

---

**Versión del esquema**: 1.0.0  
**Última actualización**: 2024-12-14
