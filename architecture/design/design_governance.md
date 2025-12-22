# Gobernanza del Design System GORE_OS

> **Propósito:** Establecer reglas claras para la evolución, mantenimiento y contribución al sistema de diseño, garantizando que escale sin perder coherencia.

## 1. Versionado Semántico

El Design System sigue [SemVer 2.0.0](https://semver.org/):

- **MAJOR (v2.0.0):** Cambios que rompen compatibilidad visual o de código (ej. renombrar tokens core, cambiar paleta completa).
- **MINOR (v1.1.0):** Nuevos componentes, variantes o tokens que no afectan lo existente.
- **PATCH (v1.0.1):** Correcciones de bugs visuales, mejoras de accesibilidad invisibles, ajustes de documentación.

## 2. Roles y Responsabilidades

| Rol                        | Responsabilidad                                                                 |
| :------------------------- | :------------------------------------------------------------------------------ |
| **Design Lead**            | Aprueba cambios visuales y nuevos patrones. "Guardián de la consistencia".      |
| **Tech Lead**              | Valida la viabilidad técnica y performance de los componentes (React/Tailwind). |
| **Accessibility Champion** | Revisa cumplimiento WCAG 2.2 AA en cada Pull Request.                           |
| **Contributors**           | Desarrolladores/Diseñadores que proponen mejoras o nuevos componentes.          |

## 3. Proceso de Contribución

### 3.1. Proponer un Nuevo Componente
1.  **Revisar Existencia:** Verificar que no exista un componente similar o que se pueda extender uno existente.
2.  **Especificación:** Documentar casos de uso, estados y variantes requeridas.
3.  **Prototipo:** Crear una prueba de concepto (Figma o Código).
4.  **Review:** Solicitar revisión de Design y Tech Lead.

### 3.2. Definition of Done (DoD)
Un componente solo entra al sistema ("Stable") si cumple:
- [ ] Implementado en React + Tailwind (Shadcn compliant).
- [ ] Soporta Modo Claro y Oscuro.
- [ ] Accesible por teclado y Screen Readers (WCAG 2.2).
- [ ] Documentado en `ui_components.md` con Props y Ejemplos.
- [ ] Tests unitarios (si aplica lógica compleja).

## 4. Changelog

### v2.0.0 (Diciembre 2025)
- **Breaking:** Actualización a WCAG 2.2 AA.
- **Feat:** Soporte nativo para Dark Mode.
- **Feat:** Nuevos tokens de animación (`motion`).
- **Refactor:** Definición explícita de Breakpoints responsivos.

### v1.0.0 (Inicial)
- Lanzamiento inicial del sistema.
- Paleta de colores institucional.
- Catálogo base de componentes atómicos.
