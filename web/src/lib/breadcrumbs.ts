export interface BreadcrumbItem {
  label: string;
  href?: string;
}

const ROUTE_LABELS: Record<string, string> = {
  "/dashboard": "Inicio",
  "/ipr": "IPR",
  "/compromisos": "Compromisos",
  "/problemas": "Problemas",
  "/alertas": "Alertas",
  "/presupuesto": "Presupuesto",
  "/convenios": "Convenios",
  "/reuniones": "Reuniones",
  "/actos": "Actos",
  "/core-sessions": "Sesiones CORE",
  "/admin/usuarios": "Usuarios",
  "/admin/divisiones": "Divisiones",
  "/admin/umbrales": "Umbrales",
  "/admin/niveles-sni": "Niveles SNI",
  "/cartera": "Cartera",
  "/tablero": "Tablero",
  "/procesos": "Procesos",
  "/procesos/progreso": "Progreso",
  "/cuellos-de-botella": "Cuellos de Botella",
  "/coordinacion": "Coordinación",
  "/coordinacion/divisiones": "Divisiones",
  "/escalamiento": "Escalamientos",
  "/servicios": "Servicios",
  "/servicios/solicitar": "Solicitar",
  "/comite-td": "Comité TD",
  "/calendario": "Calendario",
  "/riesgos": "Riesgos",
  "/datos": "Datos",
  "/informes": "Informes",
  "/centro-de-mando": "Centro de Mando",
  "/mis-compromisos": "Mis Compromisos",
  "/aprobaciones": "Aprobaciones",
};

/**
 * Builds breadcrumb items from a pathname.
 * @param pathname Current route pathname (e.g. "/ipr/abc123")
 * @param entityLabel Optional label for the last segment (e.g. "40003456-2" instead of the UUID)
 */
export function buildBreadcrumbs(
  pathname: string,
  entityLabel?: string
): BreadcrumbItem[] {
  const crumbs: BreadcrumbItem[] = [{ label: "Inicio", href: "/dashboard" }];

  // Try progressively longer path prefixes to find matching routes
  const segments = pathname.split("/").filter(Boolean);
  let accumulated = "";

  for (let i = 0; i < segments.length; i++) {
    accumulated += "/" + segments[i];
    const label = ROUTE_LABELS[accumulated];

    if (label) {
      const isLast = i === segments.length - 1;
      crumbs.push({
        label,
        href: isLast ? undefined : accumulated,
      });
    } else if (i === segments.length - 1) {
      // Last segment is a dynamic param (UUID or "nuevo"/"nueva")
      const seg = segments[i];
      if (seg === "nuevo" || seg === "nueva") {
        crumbs.push({ label: "Nuevo" });
      } else {
        crumbs.push({ label: entityLabel ?? seg.slice(0, 8) });
      }
    }
  }

  return crumbs;
}

/* ── Accent color by route ─────────────────────────────── */

const ROUTE_ACCENT: Record<string, string> = {
  "/ipr": "indigo",
  "/compromisos": "amber",
  "/mis-compromisos": "amber",
  "/presupuesto": "emerald",
  "/convenios": "emerald",
  "/actos": "violet",
  "/reuniones": "violet",
  "/core-sessions": "violet",
  "/riesgos": "rose",
  "/alertas": "rose",
  "/problemas": "rose",
  "/datos": "cyan",
  "/informes": "cyan",
  "/cartera": "cyan",
  "/tablero": "cyan",
  "/procesos": "cyan",
  "/cuellos-de-botella": "cyan",
  "/coordinacion": "teal",
  "/escalamiento": "teal",
  "/servicios": "teal",
  "/comite-td": "teal",
  "/calendario": "teal",
  "/centro-de-mando": "indigo",
  "/admin": "violet",
  "/aprobaciones": "emerald",
};

/**
 * Returns the domain accent color for a given route pathname.
 * Falls back to "indigo" if no match.
 */
export function getAccentColorByRoute(
  pathname: string
): "indigo" | "amber" | "emerald" | "violet" | "rose" | "cyan" | "teal" {
  // Try exact match first, then progressively shorter prefixes
  const segments = pathname.split("/").filter(Boolean);
  let accumulated = "";
  for (const seg of segments) {
    accumulated += "/" + seg;
    if (ROUTE_ACCENT[accumulated]) {
      return ROUTE_ACCENT[accumulated] as ReturnType<typeof getAccentColorByRoute>;
    }
  }
  return "indigo";
}
