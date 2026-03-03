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
  Vote,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

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
  { label: "Convenios", href: "/convenios", icon: <Handshake className="size-4" /> },
  { label: "Reuniones", href: "/reuniones", icon: <CalendarClock className="size-4" /> },
  { label: "Actos", href: "/actos", icon: <FileText className="size-4" /> },
  { label: "Sesiones CORE", href: "/core-sessions", icon: <Vote className="size-4" /> },
];

const adminOnlyNav: NavItem[] = [
  { label: "Usuarios", href: "/admin/usuarios", icon: <Users className="size-4" /> },
  { label: "Divisiones", href: "/admin/divisiones", icon: <Building2 className="size-4" /> },
];

const dgiNav: NavItem[] = [
  { label: "Home", href: "/dashboard", icon: <LayoutDashboard className="size-4" /> },
  { label: "Alertas", href: "/alertas", icon: <Bell className="size-4" /> },
  { label: "Tablero", href: "/tablero", icon: <KanbanSquare className="size-4" /> },
  { label: "Datos", href: "/datos", icon: <Database className="size-4" /> },
  { label: "Informes", href: "/informes", icon: <FileText className="size-4" /> },
];

export function Sidebar() {
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

  const firstItem = navItems[0];
  const restItems = navItems.slice(1);

  return (
    <nav className="w-56 h-full flex flex-col bg-background border-r pt-4 pb-4">
      <div className="px-3 mb-1">
        {firstItem && (
          <Link
            href={firstItem.href}
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
              pathname === firstItem.href || pathname.startsWith(firstItem.href + "/")
                ? "bg-accent text-accent-foreground"
                : "text-muted-foreground"
            )}
          >
            {firstItem.icon}
            {firstItem.label}
          </Link>
        )}
      </div>
      <Separator className="mb-1" />
      <div className="flex flex-col gap-0.5 px-3 flex-1">
        {restItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
              pathname === item.href || pathname.startsWith(item.href + "/")
                ? "bg-accent text-accent-foreground"
                : "text-muted-foreground"
            )}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
