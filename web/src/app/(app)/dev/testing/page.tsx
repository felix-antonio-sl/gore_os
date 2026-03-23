"use client";

import { useAuth } from "@/lib/auth";
import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { api } from "@/lib/api";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTabParam } from "@/hooks/use-tab-param";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { formatRelativeTime } from "@/lib/format";

// ---------------------------------------------------------------------------
// Checklist definitions per role
// ---------------------------------------------------------------------------

interface CheckItem {
  key: string;
  label: string;
}

interface CheckCategory {
  category: string;
  items: CheckItem[];
}

const GENERAL_CHECKS: CheckItem[] = [
  { key: "login_works", label: "Login exitoso" },
  { key: "notifications_bell", label: "Campana notificaciones visible" },
  { key: "notifications_receive", label: "Recibe notificaciones (si aplica)" },
  { key: "logout_works", label: "Logout funciona" },
];

const ROLE_CHECKLISTS: Record<string, CheckCategory[]> = {
  ANALISTA: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con ModuleFormulacion" },
        { key: "action_items", label: "Action items muestran solo mis IPRs" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "sidebar_sections", label: "Solo Gestion IPR y Mi Trabajo expandidos" },
        { key: "sidebar_no_admin", label: "Sin seccion Administracion" },
        { key: "sidebar_no_dgi", label: "Sin secciones DGI" },
      ],
    },
    {
      category: "IPR",
      items: [
        { key: "ipr_list_scoped", label: "Lista IPR muestra solo mis IPRs asignados" },
        { key: "ipr_create", label: "Puedo crear nueva IPR" },
        { key: "ipr_detail_tabs", label: "IPR detalle muestra 18 tabs" },
        { key: "ipr_satellites", label: "Puedo agregar partes, territorio, hitos" },
      ],
    },
    {
      category: "Compromisos",
      items: [
        { key: "compromisos_work_view", label: "Vista WorkView (agrupado por IPR)" },
        { key: "mis_compromisos", label: "Mis Compromisos accesible" },
      ],
    },
    {
      category: "Seguridad",
      items: [
        { key: "scope_other_ipr", label: "No puedo ver IPR de otra division (403)" },
        { key: "scope_search", label: "Busqueda global solo retorna mis IPRs" },
      ],
    },
  ],

  RTF: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con KPIs" },
        { key: "attention_strip", label: "AttentionStrip muestra rendiciones pendientes" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "sidebar_mi_trabajo", label: "Mi Trabajo expandido con Mis Rendiciones" },
      ],
    },
    {
      category: "Rendiciones",
      items: [
        { key: "rendiciones_filtered", label: "Rendiciones auto-filtradas a EN_REVISION_RTF" },
        { key: "rendicion_review", label: "Puedo visar/observar rendicion" },
      ],
    },
    {
      category: "Seguridad",
      items: [
        { key: "no_create_ipr", label: "No puedo crear IPR" },
        { key: "scope_check", label: "Solo veo IPRs asignados (403 en otros)" },
      ],
    },
  ],

  ASESOR_JURIDICO: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con ModuleJuridico" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "pendientes_vb", label: "Pendientes V.B. visible en sidebar" },
      ],
    },
    {
      category: "Actos",
      items: [
        { key: "actos_filtered", label: "Actos auto-filtrados a EN_REVISION" },
        { key: "acto_vb", label: "Puedo dar V.B. a actos" },
      ],
    },
    {
      category: "Convenios",
      items: [
        { key: "convenios_review", label: "Convenios accesibles para revision juridica" },
      ],
    },
  ],

  JEFE_DIVISION: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con ModuleMyTeam" },
        { key: "team_data", label: "Datos de equipo de mi division" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "sidebar_gestion_finanzas", label: "Gestion IPR y Finanzas expandidos" },
      ],
    },
    {
      category: "IPR",
      items: [
        { key: "ipr_division_scope", label: "Lista IPR muestra solo mi division" },
        { key: "ipr_cartera", label: "Cartera Divisional accesible" },
      ],
    },
    {
      category: "Compromisos",
      items: [
        { key: "compromisos_team_view", label: "Vista TeamView con expandibles" },
        { key: "compromiso_verify", label: "Puedo verificar compromisos" },
      ],
    },
    {
      category: "Seguridad",
      items: [
        { key: "scope_other_div", label: "No puedo ver IPR de otra division (403)" },
      ],
    },
  ],

  JEFE_DEPARTAMENTO: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con ModuleMyTeam" },
      ],
    },
    {
      category: "Aprobaciones",
      items: [
        { key: "aprobaciones_page", label: "Pagina Aprobaciones accesible" },
        { key: "aprobaciones_cdps", label: "CDPs pendientes visibles" },
        { key: "aprobaciones_rendiciones", label: "Rendiciones VISADA_RTF visibles" },
      ],
    },
  ],

  JEFE_UNIDAD: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con ModuleMyTeam" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "sidebar_gestion", label: "Gestion IPR expandido" },
      ],
    },
    {
      category: "IPR",
      items: [
        { key: "ipr_list", label: "Lista IPR de mi unidad accesible" },
      ],
    },
    {
      category: "Compromisos",
      items: [
        { key: "compromisos_view", label: "Compromisos de mi equipo visibles" },
      ],
    },
  ],

  GOBERNADOR: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con KPIs ejecutivos" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "sidebar_all_open", label: "Todas las secciones expandidas (fiscalizacion)" },
        { key: "sidebar_comando", label: "Centro de Mando visible" },
      ],
    },
    {
      category: "Actos",
      items: [
        { key: "actos_pending", label: "PendingQueue muestra actos VISADO" },
        { key: "acto_sign", label: "Puedo firmar actos" },
      ],
    },
    {
      category: "CORE",
      items: [
        { key: "core_sessions", label: "Sesiones CORE accesibles" },
        { key: "core_preside", label: "Puedo presidir sesion" },
      ],
    },
  ],

  ADMIN_SISTEMA: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga correctamente" },
      ],
    },
    {
      category: "Admin",
      items: [
        { key: "admin_tabs", label: "Pagina Admin con 5 tabs" },
        { key: "admin_usuarios", label: "CRUD usuarios funcional" },
        { key: "admin_divisiones", label: "CRUD divisiones funcional" },
        { key: "admin_config", label: "Tab Configuracion (umbrales+SNI+tracks)" },
        { key: "admin_monitoreo", label: "Tab Monitoreo (SLAs+salud datos)" },
        { key: "admin_auditoria", label: "Tab Auditoria funcional" },
      ],
    },
  ],

  ADMIN_REGIONAL: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con KPIs" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "sidebar_all_open", label: "Todas las secciones expandidas" },
      ],
    },
    {
      category: "IPR",
      items: [
        { key: "ipr_list_all", label: "Lista IPR muestra todas las IPRs" },
      ],
    },
    {
      category: "Actos",
      items: [
        { key: "actos_pending", label: "PendingQueue muestra actos VISADO para firma" },
      ],
    },
  ],

  CONSEJERO_REGIONAL: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga con KPIs" },
      ],
    },
    {
      category: "Sidebar",
      items: [
        { key: "sidebar_all_open", label: "Todas las secciones expandidas (fiscalizacion)" },
      ],
    },
    {
      category: "CORE",
      items: [
        { key: "core_vote", label: "Puedo votar en sesion CORE" },
      ],
    },
    {
      category: "Seguridad",
      items: [
        { key: "readonly", label: "No puedo crear/editar recursos (403)" },
      ],
    },
  ],

  SECRETARIO_EJECUTIVO: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_loads", label: "Dashboard carga correctamente" },
      ],
    },
    {
      category: "CORE",
      items: [
        { key: "core_create", label: "Puedo crear nueva sesion CORE" },
        { key: "core_agenda", label: "Puedo gestionar agenda" },
      ],
    },
  ],

  JEFE_DGI: [
    {
      category: "Dashboard",
      items: [
        { key: "dashboard_dgi", label: "Dashboard DGI con KPIs" },
      ],
    },
    {
      category: "Coordinacion",
      items: [
        { key: "coordinacion_tabs", label: "Coordinacion con 3 tabs (Decisiones/Divisiones/Comite TD)" },
        { key: "escalamiento", label: "Escalamientos accesibles" },
        { key: "servicios_manage", label: "Gestion de servicios con drawers" },
      ],
    },
    {
      category: "Monitoreo",
      items: [
        { key: "cartera", label: "Cartera con semaforo salud" },
        { key: "centro_mando", label: "Centro de Mando accesible" },
      ],
    },
  ],

  ESP_CONTROL_GESTION: [
    {
      category: "Monitoreo",
      items: [
        { key: "indicadores", label: "Indicadores con lifecycle y dimensiones" },
        { key: "rendiciones_sla", label: "Rendiciones con SLA progress" },
      ],
    },
    {
      category: "Mejora",
      items: [
        { key: "tablero_kanban", label: "Tablero Kanban funcional" },
        { key: "cuellos_botella", label: "Cuellos de botella accesibles" },
      ],
    },
  ],

  ESP_PROCESOS: [
    {
      category: "Mejora",
      items: [
        { key: "procesos_catalog", label: "Catalogo de procesos" },
        { key: "procesos_detail", label: "Detalle proceso con 5 tabs" },
        { key: "tablero_dmaic", label: "DMAIC 5 fases funcional" },
      ],
    },
  ],

  ESP_TD: [
    {
      category: "Mejora",
      items: [
        { key: "tablero", label: "Tablero Kanban accesible" },
        { key: "sidebar_mejora", label: "Solo Mejora Continua expandida" },
      ],
    },
  ],
};

// ---------------------------------------------------------------------------
// Bug types
// ---------------------------------------------------------------------------

interface BugReport {
  id: string;
  title: string;
  description?: string;
  severity: string;
  url: string;
  user_email: string;
  role_code: string;
  viewport: string;
  checklist_item?: string;
  screenshot?: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// BugCard component
// ---------------------------------------------------------------------------

/* eslint-disable @next/next/no-img-element */
function BugCard({ bug, onDelete }: { bug: BugReport; onDelete: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false);
  const severityColors: Record<string, string> = {
    CRITICO: "border-l-red-500",
    ALTO: "border-l-amber-500",
    MEDIO: "border-l-blue-500",
    BAJO: "border-l-green-500",
  };
  const severityBadge: Record<string, string> = {
    CRITICO: "bg-red-100 text-red-800",
    ALTO: "bg-amber-100 text-amber-800",
    MEDIO: "bg-blue-100 text-blue-800",
    BAJO: "bg-green-100 text-green-800",
  };

  return (
    <div
      className={`bg-card border border-l-4 ${severityColors[bug.severity] || "border-l-muted"} rounded-lg p-3 cursor-pointer hover:bg-muted/30 transition-colors`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="font-medium text-sm">{bug.title}</div>
          <div className="text-xs text-muted-foreground mt-1">
            {bug.user_email?.split("@")[0]} · {bug.url} · {formatRelativeTime(bug.created_at)}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${severityBadge[bug.severity] || ""}`}>
            {bug.severity}
          </span>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(bug.id); }}
            className="text-muted-foreground hover:text-destructive text-xs"
          >
            ✕
          </button>
        </div>
      </div>
      {expanded && (
        <div className="mt-3 pt-3 border-t space-y-2">
          {bug.description && <p className="text-sm text-muted-foreground">{bug.description}</p>}
          {bug.checklist_item && (
            <div className="text-xs text-muted-foreground">
              <span className="font-medium">Checklist:</span> {bug.checklist_item}
            </div>
          )}
          {bug.screenshot && (
            <img src={bug.screenshot} alt="Screenshot" className="rounded border max-h-48 w-auto" />
          )}
          <div className="text-[10px] text-muted-foreground">
            Rol: {bug.role_code} · Viewport: {bug.viewport}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function TestingPage() {
  const { user } = useAuth();
  const [state, setState] = useState<Record<string, boolean>>({});
  const [allState, setAllState] = useState<Record<string, Record<string, boolean>>>({});
  const [tab, setTab] = useTabParam("tab", "checklist");
  const [bugs, setBugs] = useState<BugReport[]>([]);

  // Load checklist state on mount
  useEffect(() => {
    if (!user?.email) return;
    api
      .get<Record<string, Record<string, boolean>>>("/api/dev/checklist")
      .then((data) => {
        setAllState(data);
        if (data[user.email]) {
          setState(data[user.email]);
        }
      })
      .catch(() => {});
  }, [user?.email]);

  // Fetch bugs
  useEffect(() => {
    api.get<BugReport[]>("/api/dev/bugs").then(setBugs).catch(() => {});
  }, [tab]);

  // Toggle a check item and persist
  const toggle = async (key: string, itemLabel: string) => {
    if (!user) return;
    const newState = { ...state, [key]: !state[key] };
    setState(newState);
    const newAll = { ...allState, [user.email]: newState };
    setAllState(newAll);
    localStorage.setItem("goreos_active_checklist_item", itemLabel);
    await api.post("/api/dev/checklist", { state: newAll }).catch(() => {});
  };

  // Delete a bug
  function handleDeleteBug(id: string) {
    api.delete(`/api/dev/bugs/${id}`).then(() => {
      setBugs((prev) => prev.filter((b) => b.id !== id));
    });
  }

  // Export bugs as JSON
  function handleExport() {
    const blob = new Blob([JSON.stringify(bugs, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `goreos-bugs-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const roleChecklist = ROLE_CHECKLISTS[user?.role_code || ""] || [];
  const allItems: CheckCategory[] = [
    { category: "General", items: GENERAL_CHECKS },
    ...roleChecklist,
  ];
  const totalItems = allItems.reduce((sum, cat) => sum + cat.items.length, 0);
  const checkedItems = Object.values(state).filter(Boolean).length;
  const pct = totalItems > 0 ? Math.round((checkedItems / totalItems) * 100) : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Testing Checklist"
        description={`${user?.email ?? "..."} — ${user?.role_code ?? "..."} — ${checkedItems}/${totalItems} completados`}
        accentColor="amber"
      />

      <div className="px-6">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="checklist">Checklist</TabsTrigger>
            <TabsTrigger value="bugs">Bugs ({bugs.length})</TabsTrigger>
          </TabsList>

          {/* ---- Checklist tab ---- */}
          <TabsContent value="checklist" className="space-y-6 mt-4">
            {/* Progress bar */}
            <div>
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                <span>Progreso</span>
                <span>{pct}%</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-500 transition-all duration-300"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>

            {/* Checklist */}
            <div className="space-y-6">
              {allItems.map((cat) => (
                <div key={cat.category}>
                  <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                    {cat.category}
                  </h3>
                  <div className="space-y-1">
                    {cat.items.map((item) => (
                      <label
                        key={item.key}
                        className="flex items-center gap-3 py-1.5 px-3 rounded hover:bg-muted/50 cursor-pointer select-none"
                      >
                        <input
                          type="checkbox"
                          checked={!!state[item.key]}
                          onChange={() => toggle(item.key, item.label)}
                          className="rounded border-input h-4 w-4 accent-amber-500"
                        />
                        <span
                          className={
                            state[item.key]
                              ? "line-through text-muted-foreground"
                              : ""
                          }
                        >
                          {item.label}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Summary table: all users progress */}
            {Object.keys(allState).length > 0 && (
              <div className="pb-8">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-3">
                  Progreso Global
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                  {Object.entries(allState).map(([email, checks]) => {
                    const done = Object.values(checks).filter(Boolean).length;
                    const total = Object.keys(checks).length;
                    const userPct =
                      total > 0 ? Math.round((done / total) * 100) : 0;
                    return (
                      <div key={email} className="text-xs p-2 rounded border">
                        <div className="font-medium truncate">
                          {email.split("@")[0]}
                        </div>
                        <div className="text-muted-foreground">
                          {done}/{total} ({userPct}%)
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </TabsContent>

          {/* ---- Bugs tab ---- */}
          <TabsContent value="bugs" className="mt-4">
            {/* KPI strip */}
            <div className="grid grid-cols-4 gap-3 mb-6">
              {[
                { label: "Critico", color: "text-red-500", count: bugs.filter((b) => b.severity === "CRITICO").length },
                { label: "Alto", color: "text-amber-500", count: bugs.filter((b) => b.severity === "ALTO").length },
                { label: "Medio", color: "text-blue-500", count: bugs.filter((b) => b.severity === "MEDIO").length },
                { label: "Bajo", color: "text-green-500", count: bugs.filter((b) => b.severity === "BAJO").length },
              ].map((k) => (
                <div key={k.label} className="bg-muted/50 rounded-lg p-3 text-center">
                  <div className={`text-2xl font-bold ${k.color}`}>{k.count}</div>
                  <div className="text-xs text-muted-foreground">{k.label}</div>
                </div>
              ))}
            </div>

            {/* Bug list */}
            {bugs.length === 0 ? (
              <EmptyState
                title="Sin bugs reportados"
                description="Usa el boton de bug para capturar bugs durante el testing"
              />
            ) : (
              <div className="space-y-2">
                {bugs
                  .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                  .map((bug) => (
                    <BugCard key={bug.id} bug={bug} onDelete={handleDeleteBug} />
                  ))}
              </div>
            )}

            {/* Export button */}
            {bugs.length > 0 && (
              <div className="mt-4 flex justify-end">
                <Button variant="outline" size="sm" onClick={handleExport}>
                  Exportar JSON
                </Button>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
