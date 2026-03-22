"use client";

import { Search, KeyRound, Menu, Sun, Moon } from "lucide-react";
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
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { GlobalSearch } from "@/components/global-search";
import { NotificationPanel } from "@/components/notification-panel";

interface HeaderProps {
  onMenuToggle?: () => void;
}

export function Header({ onMenuToggle }: HeaderProps = {}) {
  const { user, logout } = useAuth();

  const isDgi = user?.population === "dgi";
  const initials = user
    ? `${user.nombre.charAt(0)}${user.apellido_paterno.charAt(0)}`.toUpperCase()
    : "U";

  const [searchOpen, setSearchOpen] = useState(false);
  const [pwdOpen, setPwdOpen] = useState(false);
  const [pwdForm, setPwdForm] = useState({ current: "", next: "", confirm: "" });
  const [pwdError, setPwdError] = useState("");
  const [pwdLoading, setPwdLoading] = useState(false);
  const [pwdSuccess, setPwdSuccess] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const pwdStrength = pwdForm.next.length === 0 ? null :
    pwdForm.next.length < 8 ? "weak" :
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(pwdForm.next) ? "strong" : "medium";

  const handleChangePassword = async () => {
    setPwdError("");
    if (pwdForm.next.length < 8) {
      setPwdError("La nueva contraseña debe tener al menos 8 caracteres");
      return;
    }
    if (pwdForm.next !== pwdForm.confirm) {
      setPwdError("Las contraseñas no coinciden");
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
        setPwdForm({ current: "", next: "", confirm: "" });
      }, 1500);
    } catch (err: unknown) {
      setPwdError(err instanceof Error ? err.message : "Error al cambiar contraseña");
    } finally {
      setPwdLoading(false);
    }
  };

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

        {/* Notifications */}
        <NotificationPanel />

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
        <Dialog open={pwdOpen} onOpenChange={(open) => { setPwdOpen(open); if (!open) { setPwdError(""); setPwdSuccess(false); setPwdForm({ current: "", next: "", confirm: "" }); } }}>
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
                  {pwdStrength && (
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1 flex-1">
                        <div className={`h-1 flex-1 rounded-full ${pwdStrength === "weak" ? "bg-red-400" : "bg-green-400"}`} />
                        <div className={`h-1 flex-1 rounded-full ${pwdStrength === "strong" ? "bg-green-400" : pwdStrength === "medium" ? "bg-amber-400" : "bg-gray-200"}`} />
                        <div className={`h-1 flex-1 rounded-full ${pwdStrength === "strong" ? "bg-green-400" : "bg-gray-200"}`} />
                      </div>
                      <span className={`text-xs ${pwdStrength === "weak" ? "text-red-600" : pwdStrength === "medium" ? "text-amber-600" : "text-green-600"}`}>
                        {pwdStrength === "weak" ? "Débil" : pwdStrength === "medium" ? "Media" : "Fuerte"}
                      </span>
                    </div>
                  )}
                </div>
                <div className="grid gap-1.5">
                  <label htmlFor="confirm-pwd" className="text-sm font-medium">Confirmar contraseña</label>
                  <Input
                    id="confirm-pwd"
                    type="password"
                    value={pwdForm.confirm}
                    onChange={(e) => setPwdForm((f) => ({ ...f, confirm: e.target.value }))}
                  />
                </div>
                {pwdError && <p className="text-sm text-destructive">{pwdError}</p>}
              </div>
            )}
            <DialogFooter>
              {!pwdSuccess && (
                <Button onClick={handleChangePassword} disabled={pwdLoading || !pwdForm.current || !pwdForm.next || !pwdForm.confirm}>
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
