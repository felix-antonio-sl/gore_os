"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  CheckSquare,
  AlertTriangle,
  Bell,
  Users,
  KanbanSquare,
  Database,
  FileText,
  Wallet,
  Handshake,
  UserCheck,
  FolderKanban,
  CalendarClock,
  CalendarDays,
  Vote,
  ShieldCheck,
  Layers,
  Receipt,
  GitBranch,
  SearchX,
  BarChart3,
  BookOpen,
  Shield,
  ShieldAlert,
  ClipboardCheck,
  Scale,
  Route,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { GoreMark } from "@/components/gore-mark";
import { NavSection } from "@/components/nav-section";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function NavLink({
  item,
  isActive,
  onClick,
}: {
  item: NavItem;
  isActive: boolean;
  onClick?: () => void;
}) {
  return (
    <Link
      href={item.href}
      aria-current={isActive ? "page" : undefined}
      className={cn(
        "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive
          ? "bg-sidebar-primary text-sidebar-primary-foreground"
          : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
      )}
      onClick={onClick}
    >
      {item.icon}
      {item.label}
    </Link>
  );
}

// ─── Nav Data ─────────────────────────────────────────────────────────────────

const NAV = {
  inicio: { label: "Inicio", href: "/dashboard", icon: <LayoutDashboard className="size-4" /> },
  home: { label: "Home", href: "/dashboard", icon: <LayoutDashboard className="size-4" /> },

  // Comando
  centroMando: { label: "Centro de Mando", href: "/centro-de-mando", icon: <Shield className="size-4" /> },
  riesgos: { label: "Riesgos", href: "/riesgos", icon: <ShieldAlert className="size-4" /> },

  // Gestión IPR
  ipr: { label: "IPR", href: "/ipr", icon: <Building2 className="size-4" /> },
  carteraDiv: { label: "Cartera Divisional", href: "/ipr/cartera", icon: <BarChart3 className="size-4" /> },
  compromisos: { label: "Compromisos", href: "/compromisos", icon: <CheckSquare className="size-4" /> },
  problemas: { label: "Problemas", href: "/problemas", icon: <AlertTriangle className="size-4" /> },
  alertas: { label: "Alertas", href: "/alertas", icon: <Bell className="size-4" /> },

  // Finanzas
  presupuesto: { label: "Presupuesto", href: "/presupuesto", icon: <Wallet className="size-4" /> },
  cicloPpto: { label: "Ciclo Ppto.", href: "/presupuesto/ciclo", icon: <CalendarDays className="size-4" /> },
  convenios: { label: "Convenios", href: "/convenios", icon: <Handshake className="size-4" /> },

  // Institucional
  actos: { label: "Actos", href: "/actos", icon: <FileText className="size-4" /> },
  reuniones: { label: "Reuniones", href: "/reuniones", icon: <CalendarClock className="size-4" /> },
  sesionesCore: { label: "Sesiones CORE", href: "/core-sessions", icon: <Vote className="size-4" /> },
  servicios: { label: "Servicios", href: "/servicios", icon: <BookOpen className="size-4" /> },

  // Mi Trabajo
  miDivision: { label: "Mi División", href: "/mi-division", icon: <FolderKanban className="size-4" /> },
  misCompromisos: { label: "Mis Compromisos", href: "/mis-compromisos", icon: <UserCheck className="size-4" /> },
  misRendiciones: { label: "Mis Rendiciones", href: "/datos?dominio=rendiciones&state=EN_REVISION_RTF", icon: <Receipt className="size-4" /> },
  pendientesVB: { label: "Pendientes V.B.", href: "/actos?estado=EN_REVISION", icon: <Scale className="size-4" /> },
  aprobaciones: { label: "Aprobaciones", href: "/aprobaciones", icon: <ClipboardCheck className="size-4" /> },

  // Admin
  usuarios: { label: "Usuarios", href: "/admin/usuarios", icon: <Users className="size-4" /> },
  divisiones: { label: "Divisiones", href: "/admin/divisiones", icon: <Building2 className="size-4" /> },
  umbrales: { label: "Umbrales", href: "/admin/umbrales", icon: <ShieldCheck className="size-4" /> },
  nivelesSni: { label: "Niveles SNI", href: "/admin/niveles-sni", icon: <Layers className="size-4" /> },
  saludDatos: { label: "Salud de Datos", href: "/admin/salud-datos", icon: <Database className="size-4" /> },
  financingTracks: { label: "Vías Financiamiento", href: "/admin/financing-tracks", icon: <Route className="size-4" /> },
  slas: { label: "Monitoreo SLA", href: "/admin/slas", icon: <ShieldAlert className="size-4" /> },
  auditoria: { label: "Auditoría", href: "/admin/auditoria", icon: <Shield className="size-4" /> },

  // DGI — Monitoreo
  cartera: { label: "Cartera", href: "/cartera", icon: <FolderKanban className="size-4" /> },
  rendiciones: { label: "Rendiciones", href: "/datos?dominio=rendiciones", icon: <Receipt className="size-4" /> },

  // DGI — Mejora Continua
  tablero: { label: "Tablero", href: "/tablero", icon: <KanbanSquare className="size-4" /> },
  procesos: { label: "Procesos", href: "/procesos", icon: <GitBranch className="size-4" /> },
  progreso: { label: "Progreso", href: "/procesos/progreso", icon: <BarChart3 className="size-4" /> },
  cuellosBotella: { label: "Cuellos Botella", href: "/cuellos-de-botella", icon: <SearchX className="size-4" /> },

  // DGI — Coordinación
  coordinacion: { label: "Coordinación", href: "/coordinacion", icon: <Users className="size-4" /> },
  escalamiento: { label: "Escalamiento", href: "/escalamiento", icon: <AlertTriangle className="size-4" /> },
  comiteTD: { label: "Comité TD", href: "/comite-td", icon: <Vote className="size-4" /> },
  calendario: { label: "Calendario", href: "/calendario", icon: <CalendarDays className="size-4" /> },

  // DGI — Análisis
  datos: { label: "Datos", href: "/datos", icon: <Database className="size-4" /> },
  informes: { label: "Informes", href: "/informes", icon: <FileText className="size-4" /> },
} as const;

// ─── Sidebar Component ────────────────────────────────────────────────────────

interface SidebarProps {
  onNavClick?: () => void;
}

export function Sidebar({ onNavClick }: SidebarProps = {}) {
  const { user } = useAuth();
  const pathname = usePathname();

  if (!user) return null;

  const isDgi = user.population === "dgi";

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  const link = (item: NavItem) => (
    <NavLink
      key={item.href}
      item={item}
      isActive={isActive(item.href)}
      onClick={onNavClick}
    />
  );

  const showComando = ["ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA"].includes(user.role_code);
  const showCarteraDiv = ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DGI"].includes(user.role_code);
  const showMiDivision = ["JEFE_DIVISION", "JEFE_DEPARTAMENTO"].includes(user.role_code);
  const showMisCompromisos = ["ANALISTA", "RTF", "ASESOR_JURIDICO", "JEFE_UNIDAD"].includes(user.role_code);
  const showMisRendiciones = user.role_code === "RTF";
  const showPendientesVB = user.role_code === "ASESOR_JURIDICO";
  const showAprobaciones = user.role_code === "JEFE_DEPARTAMENTO";
  const showAdmin = user.role_code === "ADMIN_SISTEMA";

  return (
    <nav className="w-56 h-full flex flex-col bg-sidebar pt-3 pb-4">
      {/* Brand */}
      <div className="px-4 pb-3 mb-1 border-b border-sidebar-border">
        <Link href="/dashboard" className="flex items-center gap-2.5" onClick={onNavClick}>
          <GoreMark className="size-7 shrink-0" />
          <div className="flex flex-col">
            <span className="text-sm font-bold tracking-tight text-sidebar-primary-foreground">
              GORE_OS
            </span>
            <span className="text-[10px] text-sidebar-foreground/50 leading-tight">
              Gobierno Regional de Ñuble
            </span>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <div className="flex flex-col gap-1 px-2 pt-1 flex-1 overflow-y-auto">
        {isDgi ? (
          <>
            {/* Pinned */}
            {link(NAV.home)}

            <NavSection id="dgi-monitoreo" label="Monitoreo" defaultOpen>
              {link(NAV.centroMando)}
              {link(NAV.cartera)}
              {link(NAV.carteraDiv)}
              {link(NAV.alertas)}
              {link(NAV.rendiciones)}
              {link(NAV.riesgos)}
            </NavSection>

            <NavSection id="dgi-mejora" label="Mejora Continua" defaultOpen>
              {link(NAV.tablero)}
              {link(NAV.procesos)}
              {link(NAV.progreso)}
              {link(NAV.cuellosBotella)}
            </NavSection>

            <NavSection id="dgi-coord" label="Coordinación" defaultOpen={false}>
              {link(NAV.coordinacion)}
              {link(NAV.escalamiento)}
              {link(NAV.servicios)}
              {link(NAV.comiteTD)}
              {link(NAV.calendario)}
            </NavSection>

            <NavSection id="dgi-analisis" label="Análisis" defaultOpen={false}>
              {link(NAV.datos)}
              {link(NAV.informes)}
            </NavSection>
          </>
        ) : (
          <>
            {/* Pinned */}
            {link(NAV.inicio)}

            {showComando && (
              <NavSection id="op-comando" label="Comando" defaultOpen>
                {link(NAV.centroMando)}
                {link(NAV.riesgos)}
              </NavSection>
            )}

            <NavSection id="op-gestion" label="Gestión IPR" defaultOpen>
              {link(NAV.ipr)}
              {showCarteraDiv && link(NAV.carteraDiv)}
              {link(NAV.compromisos)}
              {link(NAV.problemas)}
              {link(NAV.alertas)}
            </NavSection>

            <NavSection id="op-finanzas" label="Finanzas" defaultOpen={false}>
              {link(NAV.presupuesto)}
              {link(NAV.cicloPpto)}
              {link(NAV.convenios)}
            </NavSection>

            <NavSection id="op-institucional" label="Institucional" defaultOpen={false}>
              {link(NAV.actos)}
              {link(NAV.reuniones)}
              {link(NAV.sesionesCore)}
              {link(NAV.servicios)}
            </NavSection>

            {(showMiDivision || showMisCompromisos || showMisRendiciones || showPendientesVB || showAprobaciones) && (
              <NavSection id="op-mi-trabajo" label="Mi Trabajo" defaultOpen>
                {showMiDivision && link(NAV.miDivision)}
                {showMisCompromisos && link(NAV.misCompromisos)}
                {showMisRendiciones && link(NAV.misRendiciones)}
                {showPendientesVB && link(NAV.pendientesVB)}
                {showAprobaciones && link(NAV.aprobaciones)}
              </NavSection>
            )}

            {showAdmin && (
              <NavSection id="op-admin" label="Administración" defaultOpen={false}>
                {link(NAV.usuarios)}
                {link(NAV.divisiones)}
                {link(NAV.umbrales)}
                {link(NAV.nivelesSni)}
                {link(NAV.saludDatos)}
                {link(NAV.financingTracks)}
                {link(NAV.slas)}
                {link(NAV.auditoria)}
              </NavSection>
            )}
          </>
        )}
      </div>
    </nav>
  );
}
