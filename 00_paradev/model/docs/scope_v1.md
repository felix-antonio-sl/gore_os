# Scope GORE_OS v1.0

## Dominios Incluidos (Core)

Los siguientes dominios están en scope para la versión 1.0:

| Dominio             | Código | Descripción                           |
| ------------------- | ------ | ------------------------------------- |
| Finanzas            | D-FIN  | Presupuesto, IPR, inversión pública   |
| Ejecución           | D-EJE  | Convenios, estados de pago, garantías |
| Gobierno            | D-GOV  | CORE, gobernador, consejeros          |
| Planificación       | D-PLAN | ERD, ARI, convenios de programación   |
| Territorial         | D-LOC  | Comunas, provincias, PROT             |
| Normativo           | D-NORM | Actos administrativos, lobby          |
| Digital             | D-DIG  | Interoperabilidad, firma electrónica  |
| Organizacional      | D-ORG  | Funcionarios, divisiones, cargos      |
| Salud Institucional | D-SAL  | POA, OKR, intervenciones              |
| Sistema             | D-SYS  | Documentos, actores, eventos          |
| Convergencia        | D-CONV | Participación ciudadana, cabildos     |

## Dominios Diferidos (v2.0+)

| Dominio        | Código | Razón de Diferimiento                |
| -------------- | ------ | ------------------------------------ |
| Desarrollo     | D-DEV  | No es core institucional GORE        |
| Operaciones TI | D-OPS  | Infraestructura manejada por SUBDERE |
| Evolución      | D-EVOL | IA y mejora continua para v3.0       |

## Entidades Legacy Depreciadas

Las siguientes 55 entidades del modelo `old_entities` no serán migradas:

### D-DEV (17 entidades)
- `ENT-DEV-ADR`, `ENT-DEV-BRANCH`, `ENT-DEV-COMMIT`, `ENT-DEV-EPIC`
- `ENT-DEV-PIPELINE`, `ENT-DEV-PULLREQUEST`, `ENT-DEV-RELEASE`
- `ENT-DEV-REPOSITORIO`, `ENT-DEV-SPRINT`, `ENT-DEV-STORY`
- `ENT-DEV-TEST-CASE`, `ENT-DEV-TEST-SUITE`, etc.

### D-OPS (18 entidades)
- `ENT-OPS-AMBIENTE`, `ENT-OPS-BACKUP`, `ENT-OPS-DESPLIEGUE`
- `ENT-OPS-METRICA`, `ENT-OPS-TICKET`, etc.

### D-EVOL (20 entidades)
- `ENT-EVOL-AGENTE_IA`, `ENT-EVOL-CAPACIDAD`, `ENT-EVOL-DEUDA-TECNICA`
- `ENT-EVOL-NIVEL-MADUREZ`, etc.

---

*Documento generado por Arquitecto-GORE v0.1.0 | 2025-12-22*
