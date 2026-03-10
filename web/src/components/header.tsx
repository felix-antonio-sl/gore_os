"use client";

import { Bell, Search, AlertTriangle, Info, KeyRound, Menu, Sun, Moon } from "lucide-react";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
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

interface HeaderProps {
  onMenuToggle?: () => void;
}

export function Header({ onMenuToggle }: HeaderProps = {}) {
  const { user, logout } = useAuth();

  const isDgi = user?.population === "dgi";
  const initials = user
    ? `${user.nombre.charAt(0)}${user.apellido_paterno.charAt(0)}`.toUpperCase()
    : "U";

  const [alertCount, setAlertCount] = useState(0);
  const [recentAlerts, setRecentAlerts] = useState<AlertaListItem[]>([]);
  const [bellOpen, setBellOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [pwdOpen, setPwdOpen] = useState(false);
  const [pwdForm, setPwdForm] = useState({ current: "", next: "" });
  const [pwdError, setPwdError] = useState("");
  const [pwdLoading, setPwdLoading] = useState(false);
  const [pwdSuccess, setPwdSuccess] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const handleChangePassword = async () => {
    setPwdError("");
    if (pwdForm.next.length < 8) {
      setPwdError("La nueva contraseña debe tener al menos 8 caracteres");
      return;
    }
    setPwdLoading(true);
    try {
      await api.post("/auth/change-password", {
        current_password: pwdForm.current,
        new_password: pwdForm.next,
      });
      setPwdSuccess(true);
      setTimeout(() => {
        setPwdOpen(false);
        setPwdSuccess(false);
        setPwdForm({ current: "", next: "" });
      }, 1500);
    } catch (err: unknown) {
      setPwdError(err instanceof Error ? err.message : "Error al cambiar contraseña");
    } finally {
      setPwdLoading(false);
    }
  };

  const ALERT_REFRESH_MS = 60_000;

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
    const interval = setInterval(fetchAlerts, ALERT_REFRESH_MS);
    return () => clearInterval(interval);
  }, []);

  // Theme hydration
  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setTheme(isDark ? "dark" : "light");
  }, []);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.classList.toggle("dark", next === "dark");
    localStorage.setItem("goreos_theme", next);
  };

  return (
    <header className="h-14 border-b bg-background flex items-center justify-between px-4">
      {/* Left */}
      <div className="flex items-center gap-3">
        {onMenuToggle && (
          <Button variant="ghost" size="icon" className="md:hidden h-8 w-8" onClick={onMenuToggle} aria-label="Abrir menú">
            <Menu className="size-5" />
          </Button>
        )}
        <span className="text-lg font-bold tracking-tight text-primary font-serif">GORE_OS</span>
        {isDgi && (
          <Badge className="text-xs bg-teal-100 text-teal-800 border-teal-200 dark:bg-teal-900 dark:text-teal-200 dark:border-teal-800">
            DGI
          </Badge>
        )}
      </div>

      {/* Right */}
      <div className="flex items-center gap-1.5">
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

        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={toggleTheme}
          aria-label={theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
        >
          {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
        </Button>

        {/* Bell con popover de alertas */}
        <Popover open={bellOpen} onOpenChange={setBellOpen}>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative h-8 w-8" aria-label="Ver alertas">
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
              className="cursor-pointer"
              onClick={() => setPwdOpen(true)}
            >
              <KeyRound className="size-4 mr-2" />
              Cambiar Contraseña
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive cursor-pointer"
              onClick={logout}
            >
              Cerrar Sesión
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Password change dialog */}
        <Dialog open={pwdOpen} onOpenChange={(open) => { setPwdOpen(open); if (!open) { setPwdError(""); setPwdSuccess(false); setPwdForm({ current: "", next: "" }); } }}>
          <DialogContent className="sm:max-w-[380px]">
            <DialogHeader>
              <DialogTitle>Cambiar Contraseña</DialogTitle>
              <DialogDescription>
                Ingrese su contraseña actual y la nueva contraseña.
              </DialogDescription>
            </DialogHeader>
            {pwdSuccess ? (
              <p className="text-sm text-green-600 py-4 text-center">Contraseña actualizada correctamente</p>
            ) : (
              <div className="grid gap-3 py-2">
                <div className="grid gap-1.5">
                  <label htmlFor="current-pwd" className="text-sm font-medium">Contraseña actual</label>
                  <Input
                    id="current-pwd"
                    type="password"
                    value={pwdForm.current}
                    onChange={(e) => setPwdForm((f) => ({ ...f, current: e.target.value }))}
                  />
                </div>
                <div className="grid gap-1.5">
                  <label htmlFor="new-pwd" className="text-sm font-medium">Nueva contraseña</label>
                  <Input
                    id="new-pwd"
                    type="password"
                    value={pwdForm.next}
                    onChange={(e) => setPwdForm((f) => ({ ...f, next: e.target.value }))}
                    placeholder="Mínimo 8 caracteres"
                  />
                </div>
                {pwdError && <p className="text-sm text-destructive">{pwdError}</p>}
              </div>
            )}
            <DialogFooter>
              {!pwdSuccess && (
                <Button onClick={handleChangePassword} disabled={pwdLoading || !pwdForm.current || !pwdForm.next}>
                  {pwdLoading ? "Guardando..." : "Guardar"}
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </header>
  );
}
