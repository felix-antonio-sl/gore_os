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
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { GoreMark } from "@/components/gore-mark";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const operationalNav: NavItem[] = [
  { label: "Inicio", href: "/dashboard", icon: <LayoutDashboard className="size-4" /> },
  { label: "IPR", href: "/ipr", icon: <Building2 className="size-4" /> },
  { label: "Compromisos", href: "/compromisos", icon: <CheckSquare className="size-4" /> },
  { label: "Problemas", href: "/problemas", icon: <AlertTriangle className="size-4" /> },
  { label: "Alertas", href: "/alertas", icon: <Bell className="size-4" /> },
  { label: "Presupuesto", href: "/presupuesto", icon: <Wallet className="size-4" /> },
  { label: "Ciclo Ppto.", href: "/presupuesto/ciclo", icon: <CalendarDays className="size-4" /> },
  { label: "Convenios", href: "/convenios", icon: <Handshake className="size-4" /> },
  { label: "Reuniones", href: "/reuniones", icon: <CalendarClock className="size-4" /> },
  { label: "Actos", href: "/actos", icon: <FileText className="size-4" /> },
  { label: "Sesiones CORE", href: "/core-sessions", icon: <Vote className="size-4" /> },
];

const adminOnlyNav: NavItem[] = [
  { label: "Usuarios", href: "/admin/usuarios", icon: <Users className="size-4" /> },
  { label: "Divisiones", href: "/admin/divisiones", icon: <Building2 className="size-4" /> },
  { label: "Umbrales", href: "/admin/umbrales", icon: <ShieldCheck className="size-4" /> },
  { label: "Niveles SNI", href: "/admin/niveles-sni", icon: <Layers className="size-4" /> },
];

const dgiNav: NavItem[] = [
  { label: "Home", href: "/dashboard", icon: <LayoutDashboard className="size-4" /> },
  { label: "Cartera", href: "/cartera", icon: <FolderKanban className="size-4" /> },
  { label: "Alertas", href: "/alertas", icon: <Bell className="size-4" /> },
  { label: "Rendiciones", href: "/datos?dominio=rendiciones", icon: <Receipt className="size-4" /> },
  { label: "Tablero", href: "/tablero", icon: <KanbanSquare className="size-4" /> },
  { label: "Procesos", href: "/procesos", icon: <GitBranch className="size-4" /> },
  { label: "Cuellos Botella", href: "/cuellos-de-botella", icon: <SearchX className="size-4" /> },
  { label: "Datos", href: "/datos", icon: <Database className="size-4" /> },
  { label: "Informes", href: "/informes", icon: <FileText className="size-4" /> },
];

interface SidebarProps {
  onNavClick?: () => void;
}

export function Sidebar({ onNavClick }: SidebarProps = {}) {
  const { user } = useAuth();
  const pathname = usePathname();

  if (!user) return null;

  const isDgi = user.population === "dgi";
  let navItems: NavItem[];

  if (isDgi) {
    navItems = dgiNav;
  } else {
    navItems = [...operationalNav];
    if (["JEFE_DIVISION", "JEFE_DEPARTAMENTO"].includes(user.role_code)) {
      navItems = [
        ...navItems,
        { label: "Mi División", href: "/mi-division", icon: <FolderKanban className="size-4" /> },
      ];
    }
    if (["ENCARGADO", "JEFE_UNIDAD"].includes(user.role_code)) {
      navItems = [
        ...navItems,
        { label: "Mis Compromisos", href: "/mis-compromisos", icon: <UserCheck className="size-4" /> },
      ];
    }
    if (user.role_code === "ADMIN_SISTEMA") {
      navItems = [...navItems, ...adminOnlyNav];
    }
  }

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

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
      <div className="flex flex-col gap-0.5 px-2 pt-1 flex-1 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            aria-current={isActive(item.href) ? "page" : undefined}
            className={cn(
              "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              isActive(item.href)
                ? "bg-sidebar-primary text-sidebar-primary-foreground"
                : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            )}
            onClick={onNavClick}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}

