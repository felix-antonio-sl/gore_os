# Diccionario de Entidades Compartidas — GORE_OS

Este documento establece los identificadores canónicos para las entidades que son consumidas por múltiples dominios del Blueprint GORE_OS. Se prioriza el uso de identificadores en **español** para la documentación de negocio, manteniendo los alias técnicos cuando sea necesario.

| Identificador Canónico  | Alias Técnicos / Anteriores            | Dominio Propietario (SADV) | Definición                                                                   |
| :---------------------- | :------------------------------------- | :------------------------- | :--------------------------------------------------------------------------- |
| `ExpedienteElectronico` | `ElectronicFile`, `EE`                 | D-NORM                     | Conjunto de documentos electrónicos con un Índice Unitario (IUIe).           |
| `ActoAdministrativo`    | `AdministrativeAct`, `AA`              | D-NORM                     | Documento formal (Resolución, Decreto) que expresa la voluntad del GORE.     |
| `DocumentoElectronico`  | `ElectronicDocument`, `DE`             | D-NORM                     | Unidad mínima de información firmada electrónicamente.                       |
| `Actor`                 | `Actor`, `EntidadRegional`             | D-GOB                      | Cualquier persona, municipio, empresa o servicio que interactúa con el GORE. |
| `IPR`                   | `Iniciativa`, `Proyecto`, `IDI`, `PPR` | D-FIN                      | Intervención Pública Regional. Unidad base de inversión regional.            |
| `ActivoTI`              | `ITAsset`, `RecursoTI`                 | D-TDE                      | Equipamiento, licencias o infraestructura tecnológica.                       |
| `Convenio`              | `Agreement`, `Contract`                | D-NORM / D-EJEC            | Acuerdo formal entre el GORE y un tercero (D-NORM define, D-EJEC opera).     |
| `CDP`                   | `Certificate`, `Disponibilidad`        | D-FIN / D-BACK             | Certificado de Disponibilidad Presupuestaria.                                |
| `H_gore`                | `TacticalHealthScore`                  | D-GESTION                  | Índice de salud táctica de la operación diaria.                              |
| `H_org`                 | `OrganizationalHealthScore`            | D-EVOL                     | Índice de madurez sistémica y evolución.                                     |

---

## Reglas de Uso
1. **Identificadores en Documentación:** Debe usarse el *Identificador Canónico* en todos los diagramas y tablas de referencia.
2. **Tablas de Referencias Cruzadas:** Al citar una entidad de otro dominio, usar el formato `Dominio.Entidad` (p.ej. `D-NORM.ExpedienteElectronico`).
3. **Persistencia y APIs:** Se recomienda que las APIs utilicen el identificador canónico o el `canonical_id` técnico mapeado en el modelo de datos.

---
*Documento parte de GORE_OS Blueprint Integral v5.5*  
*Última actualización: 2025-12-18*
