# C1 - Contexto del Sistema GORE_OS

> **Alineación TDE:** Principio de Gobierno Integrado (`TDE_CORE_PRI_003`)
> **Visión:** GORE como nodo activo en la red del Estado (GORE 4.0).

## Abstract
GORE_OS es la plataforma central de gestión para el Gobierno Regional, actuando como el sistema nervioso digital que orquesta procesos administrativos, financieros y territoriales. No opera aislado, sino como un nodo interoperable en el ecosistema digital del Estado de Chile.

## Diagrama de Contexto (Nivel 1)

```mermaid
C4Context
    title Diagrama de Contexto del Sistema GORE_OS (TDE Compliant)

    %% Actores
    Person(ciudadano, "Ciudadano / Beneficiario", "Accede a oferta pública regional (Principio 'Centrado en las Personas')")
    Person(funcionario, "Funcionario GORE", "Operador de procesos internos y tomador de decisiones")
    Person(proveedor, "Proveedor Local", "Socio estratégico en la ejecución de inversiones")

    %% Sistema Central
    System(gore_os, "GORE_OS", "Plataforma Integral de Gestión Regional (ERP + BPM + GIS)")

    %% Sistemas Externos (Plataformas Compartidas TDE)
    System_Ext(claveunica, "ClaveÚnica / I-Provider", "Identidad Digital Oficial (DS N°9)")
    System_Ext(docdigital, "DocDigital", "Comunicaciones Oficiales del Estado (DS N°10)")
    System_Ext(pisee, "PISEE / Interoperabilidad", "Red de Interoperabilidad del Estado (DS N°12)")
    
    %% Sistemas Externos (Sectoriales)
    System_Ext(cgr, "SIAPER / CGR", "Sistema de Control Administrativo")
    System_Ext(dipres, "SIGFE / DIPRES", "Sistema de Gestión Financiera Central")
    System_Ext(mercadopublico, "MercadoPúblico", "Compras Públicas")

    %% Relaciones Ciudadano
    Rel(ciudadano, gore_os, "Solicita beneficios (Once-Only)", "Web / App móvil")
    Rel(gore_os, claveunica, "Autentica usuarios", "OIDC Connect")

    %% Relaciones Operativas
    Rel(funcionario, gore_os, "Gestiona ciclo de vida de inversión", "Intranet")
    Rel(gore_os, docdigital, "Envía/Recibe oficios", "API REST")
    Rel(gore_os, pisee, "Consume datos personales/sociales", "SOAP/REST (SRCE)")
    
    %% Relaciones de Control y Financieras
    Rel(gore_os, cgr, "Tramita actos administrativos", "SISTRA/SIAPER")
    Rel(gore_os, dipres, "Reporta ejecución presupuestaria", "Web Services")
    Rel(gore_os, mercadopublico, "Valida órdenes de compra", "API Licita")
```

## Fronteras del Sistema y Responsabilidades

### Responsabilidades GORE_OS (In Scope)
- **Gestión de Cartera de Inversiones (FNDR)**: Ciclo completo desde pre-admisibilidad hasta cierre.
- **Gestión Territorial (Gemelo Digital)**: Planificación basada en mapas (PostGIS) y datos.
- **Administración Interna**: Subvenciones, Personas (Viáticos, Cometidos), Activos.
- **Exposición de APIs de Datos Abiertos**: `TDE-DATOS-ACTIVO-ESTRATEGICO-01`.

### Responsabilidades Delegadas (Out of Scope - Reuse)
- **Identidad**: Delegado 100% a **ClaveÚnica** (no gestionamos passwords de ciudadanos).
- **Comunicaciones Inter-Servicios**: Delegado a **DocDigital**. No construimos un "correo" propio.
- **Pagos Masivos**: Delegado a **TGR/BancoEstado** (integración, no tenencia de fondos).
- **Firma Avanzada**: Consumo de proveedores acreditados o servicio de firma del Estado.

## Principios de Integración
1.  **Once Only**: Antes de pedir un dato al ciudadano (ej. Registro Social de Hogares), GORE_OS lo consulta vía PISEE.
2.  **Digital Default**: Todo documento saliente nace digital (XML/PDF firmado) y se cursa por DocDigital.
