# Modelo de Datos GORE_OS

## Estructura

```text
model/
├── model/
├── stories/    # 819 historias de usuario
├── roles/      # 410 roles institucionales
├── entities/   # 139 entidades del modelo de datos
├── processes/  # 84 procesos BPMN
├── GLOSARIO.yml    # Terminología autorizada
└── README.md       # Este archivo
├── GLOSARIO.yml    # Terminología autorizada
└── README.md       # Este archivo
```

## Regla de Derivación Estructural

> **A1**: Toda Entity traza a al menos una Story de origen.
> **A2**: Todo artefacto de solución habilita (no describe) Stories.
> **A3**: Los Módulos emergen de la agrupación de Stories.
> **A4**: Derivación unidireccional: Stories → Entities → Artefactos → Módulos.

## Ciudadanos de Primera Clase

1. **Story**: Punto de partida; especifica el valor y los requerimientos
2. **Entity**: Modelo de datos; esquemas de información del sistema
3. **Role**: Actor que ejecuta las stories
4. **Process**: Perspectiva temporal/dinámica de las stories

## Referencia

- Ver [MANIFESTO.md](../MANIFESTO.md) para identidad y principios
- Ver [architecture/](../architecture/) para stack tecnológico
