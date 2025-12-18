# Catálogo Maestro de Sistemas Externos (SYS-CATALOG)

Este catálogo identifica los sistemas externos obligatorios con los que GORE_OS debe interoperar, estableciendo su identificador canónico y su rol dentro de la arquitectura regional.

| ID Sistema         | Nombre Formal   | Institución Propietaria | Dominio Responsable | Propósito en GORE_OS                                             |
| :----------------- | :-------------- | :---------------------- | :------------------ | :--------------------------------------------------------------- |
| **SYS-SIGFE**      | SIGFE v2        | Min. Hacienda (DIPRES)  | D-FIN / D-BACK      | Contabilidad, devengo y pago. Fuente de verdad financiera.       |
| **SYS-BIP**        | BIP-SNI         | MDSF / DIPRES           | D-FIN               | Banco Integrado de Proyectos. Ficha IDI, RS, Monitoreo.          |
| **SYS-SISREC**     | SISREC          | Contraloría (CGR)       | D-FIN / D-EJEC      | Rendición de cuentas de transferencias y proyectos.              |
| **SYS-DOCDIGITAL** | DocDigital      | Min. Segpres            | D-NORM / D-TDE      | Interoperabilidad documental entre órganos del Estado.           |
| **SYS-SIAPER**     | SIAPER-TRA      | Contraloría (CGR)       | D-BACK              | Toma de razón automática de actos de personal.                   |
| **SYS-MERCADOPUB** | Mercado Público | ChileCompra             | D-BACK              | Gestión de compras, licitaciones y catálogo de convenios marco.  |
| **SYS-FIRMAGOB**   | FirmaGob        | Min. Segpres            | D-TDE / D-NORM      | Plataforma de firma electrónica avanzada (FEA) del Estado.       |
| **SYS-PISEE**      | PISEE           | Min. Segpres            | D-TDE               | Bus de Interoperabilidad para consulta de datos ciudadanos.      |
| **SYS-SITIA**      | SITIA           | Sub. Prev. Delito       | D-SEG               | Sistema Integrado de Televigilancia con Inteligencia Artificial. |

---

## Estrategia de Interoperabilidad
1. **Puntajes de Salud (H_gore):** Los sistemas marcados con **P0** (SIGFE, BIP, SISREC) son críticos; su indisponibilidad o desfase de datos penaliza directamente el puntaje de salud táctica.
2. **APIs y Adaptadores:** Cada dominio responsable debe implementar adaptadores que traduzcan los datos de estos sistemas al esquema canónico de GORE_OS.
3. **Carga Masiva (D-OPS):** D-OPS es el responsable operativo de las cargas batch o migraciones históricas desde estos sistemas.

---
*Documento parte de GORE_OS Blueprint Integral v5.5*  
*Última actualización: 2025-12-18*
