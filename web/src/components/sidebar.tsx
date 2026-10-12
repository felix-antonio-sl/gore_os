"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CheckSquare, Bell, ShieldAlert, FileText, Handshake, Receipt, Building2, AlertTriangle, Users, ShieldCheck, BookOpen } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { DGI_ROLES } from "@/types";
import { GoreMark } from "@/components/gore-mark";

const RELATED = [
  { label: "Compromisos", href: "/compromisos", icon: CheckSquare },
  { label: "Alertas", href: "/alertas", icon: Bell },
  { label: "IPR", href: "/ipr", icon: Building2 },
  { label: "Problemas", href: "/problemas", icon: AlertTriangle },
  { label: "Riesgos", href: "/riesgos", icon: ShieldAlert },
  { label: "Actos", href: "/actos", icon: FileText },
  { label: "Convenios", href: "/convenios", icon: Handshake },
  { label: "Rendiciones", href: "/rendiciones", icon: Receipt },
  { label: "Solicitudes de servicio", href: "/servicios", icon: BookOpen },
];

export function Sidebar({ onNavClick }: { onNavClick?: () => void } = {}) {
  const { user } = useAuth();
  const pathname = usePathname();
  if (!user) return null;
  const canReadCoordination = [...DGI_ROLES, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"].includes(user.role_code);
  const items = [
    { label: "Bandeja de trabajo", href: "/dashboard", icon: CheckSquare },
    ...RELATED,
    ...(canReadCoordination ? [
      { label: "Decisiones AR", href: "/coordinacion", icon: Users },
      { label: "Escalamientos", href: "/escalamiento", icon: AlertTriangle },
    ] : []),
    ...(user.role_code === "ADMIN_SISTEMA" ? [{ label: "Administración", href: "/admin", icon: ShieldCheck }] : []),
  ];
  return <nav className="w-56 h-full flex flex-col bg-sidebar pt-3 pb-4">
    <div className="px-4 pb-3 mb-1 border-b border-sidebar-border">
      <Link href="/dashboard" className="flex items-center gap-2.5" onClick={onNavClick}>
        <GoreMark className="size-7 shrink-0" /><div><span className="block text-sm font-bold text-sidebar-primary-foreground">GORE_OS</span>
        <span className="text-[10px] text-sidebar-foreground/50">Gobierno Regional de Ñuble</span></div>
      </Link>
    </div>
    <div className="flex flex-col gap-1 px-2 pt-1 flex-1 overflow-y-auto">
      {items.map(({ label, href, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(href + "/");
        return <Link key={href} href={href} onClick={onNavClick} aria-current={active ? "page" : undefined}
          className={cn("flex min-h-11 md:min-h-0 items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
            active ? "bg-sidebar-primary text-sidebar-primary-foreground" : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground")}>
          <Icon className="size-4 shrink-0" />{label}</Link>;
      })}
    </div>
  </nav>;
}
