# C1 - Contexto del Sistema GORE_OS

## Abstract
GORE_OS es la plataforma central de gestión para el Gobierno Regional, actuando como el sistema nervioso digital que orquesta procesos administrativos, financieros y territoriales.

## Diagrama de Contexto (Nivel 1)

```mermaid
C4Context
    title Diagrama de Contexto del Sistema GORE_OS

    %% Actores
    Person(ciudadano, "Ciudadano", "Beneficiario de programas y servicios regionales")
    Person(funcionario, "Funcionario GORE", "Usuario interno gestor de procesos")
    Person(proveedor, "Proveedor", "Empresas que contratan con el GORE")

    %% Sistema Central
    System(gore_os, "GORE_OS", "Plataforma Integral de Gestión Regional (ERP + BPM + GIS)")

    %% Sistemas Externos
    System_Ext(cgr, "SIAPER / CGR", "Sistema de Contraloría General de la República")
    System_Ext(dipres, "SIGFE / DIPRES", "Sistema de Gestión Financiera del Estado")
    System_Ext(mercadopublico, "MercadoPúblico", "Plataforma de Compras Públicas")
    System_Ext(banco, "BancoEstado", "Servicios Financieros y Pagos")
    System_Ext(claveunica, "ClaveÚnica", "Identidad Digital del Estado")

    %% Relaciones
    Rel(ciudadano, gore_os, "Solicita beneficios, consulta estado", "HTTPS/Web")
    Rel(funcionario, gore_os, "Gestiona trámites, aprueba flujos", "HTTPS/Intranet")
    Rel(proveedor, gore_os, "Gestiona contratos y pagos", "HTTPS/Portal")

    Rel(gore_os, claveunica, "Autentica usuarios", "OIDC")
    Rel(gore_os, cgr, "Remite actos administrativos", "Interoperabilidad")
    Rel(gore_os, dipres, "Sincroniza ejecución presupuestaria", "API/Archivos")
    Rel(gore_os, mercadopublico, "Consulta órdenes de compra", "API")
    Rel(gore_os, banco, "Ordena transferencias", "H2H")
```

## Fronteras del Sistema

### In Scope
- Gestión de Cartera de Inversiones (FNDR)
- Administración Financiera y Contable (en espejo con SIGFE)
- Gestión Documental y Firma Electrónica
- Planificación Territorial (GIS)
- Gestión de Personas y Cometidos

### Out of Scope
- Validación de identidad (delegado a ClaveÚnica)
- Custodia de fondos (delegado a BancoEstado)
- Toma de razón legal (delegado a CGR)
