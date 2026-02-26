"use client";

import { Bell, Search, AlertTriangle, Info } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { AlertaListItem } from "@/types";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { GlobalSearch } from "@/components/global-search";

const SEVERITY_STYLES: Record<string, string> = {
  CRITICO: "text-red-600",
  ALTO: "text-orange-500",
  ATENCION: "text-amber-500",
  INFO: "text-blue-500",
};

function SeverityIcon({ severity }: { severity: string | null }) {
  if (!severity || severity === "INFO") return <Info className="size-3.5 text-blue-500 shrink-0" />;
  return <AlertTriangle className={cn("size-3.5 shrink-0", SEVERITY_STYLES[severity] ?? "text-muted-foreground")} />;
}

export function Header() {
  const { user, logout } = useAuth();

  const isDgi = user?.population === "dgi";
  const initials = user
    ? `${user.nombre.charAt(0)}${user.apellido_paterno.charAt(0)}`.toUpperCase()
    : "U";

  const [alertCount, setAlertCount] = useState(0);
  const [recentAlerts, setRecentAlerts] = useState<AlertaListItem[]>([]);
  const [bellOpen, setBellOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const fetchAlerts = () => {
    api
      .get<{ items: AlertaListItem[]; total: number }>(
        "/alertas?active_only=true&page_size=5"
      )
      .then((data) => {
        setAlertCount(data.total);
        setRecentAlerts(data.items);
      })
      .catch(() => {
        /* silenciar errores de red */
      });
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 60_000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 border-b bg-background flex items-center justify-between px-4">
      {/* Left */}
      <div className="flex items-center gap-3">
        <span className="text-lg font-bold tracking-tight">GORE_OS</span>
        {isDgi && (
          <Badge variant="secondary" className="text-xs">
            DGI
          </Badge>
        )}
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        {/* Search trigger */}
        <Button
          variant="outline"
          size="sm"
          className="h-8 gap-2 text-muted-foreground text-xs px-3"
          onClick={() => setSearchOpen(true)}
        >
          <Search className="size-3.5" />
          <span className="hidden sm:inline">Buscar</span>
          <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded border bg-muted px-1 text-[10px]">
            ⌘K
          </kbd>
        </Button>
        <GlobalSearch open={searchOpen} onOpenChange={setSearchOpen} />

        {/* Bell con popover de alertas */}
        <Popover open={bellOpen} onOpenChange={setBellOpen}>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative h-8 w-8">
              <Bell className="size-4" />
              {alertCount > 0 && (
                <Badge className="absolute -top-0.5 -right-0.5 h-4 min-w-4 px-1 text-[10px]">
                  {alertCount > 99 ? "99+" : alertCount}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-80 p-0">
            <div className="px-3 py-2 border-b">
              <p className="text-sm font-medium">Alertas activas</p>
              {alertCount > 0 && (
                <p className="text-xs text-muted-foreground">{alertCount} pendiente{alertCount !== 1 ? "s" : ""}</p>
              )}
            </div>
            <div className="max-h-64 overflow-y-auto">
              {recentAlerts.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-6">
                  Sin alertas activas
                </p>
              ) : (
                recentAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="flex items-start gap-2 px-3 py-2 border-b last:border-0 hover:bg-muted/50"
                  >
                    <SeverityIcon severity={alert.severity} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate">{alert.message}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">
                        {alert.subject_label ?? alert.subject_type}
                        {" · "}
                        {new Date(alert.triggered_at).toLocaleDateString("es-CL")}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
            <div className="px-3 py-2 border-t">
              <Link
                href="/alertas"
                className="text-xs text-primary hover:underline"
                onClick={() => setBellOpen(false)}
              >
                Ver todas las alertas →
              </Link>
            </div>
          </PopoverContent>
        </Popover>

        {/* User dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full p-0">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="text-xs bg-primary text-primary-foreground">
                  {initials}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>
              <p className="font-medium text-sm">
                {user?.nombre} {user?.apellido_paterno}
              </p>
              <p className="text-xs text-muted-foreground font-normal mt-0.5">
                {user?.role_label}
              </p>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-destructive cursor-pointer"
              onClick={logout}
            >
              Cerrar Sesión
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
