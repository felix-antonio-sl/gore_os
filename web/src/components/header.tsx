"use client";

import { Bell, Search } from "lucide-react";
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

export function Header() {
  const { user, logout } = useAuth();

  const isDgi = user?.population === "dgi";
  const initials = user
    ? `${user.nombre.charAt(0)}${user.apellido_paterno.charAt(0)}`.toUpperCase()
    : "U";

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
        >
          <Search className="size-3.5" />
          <span className="hidden sm:inline">Buscar</span>
          <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded border bg-muted px-1 text-[10px]">
            ⌘K
          </kbd>
        </Button>

        {/* Bell */}
        <Button variant="ghost" size="icon" className="relative h-8 w-8">
          <Bell className="size-4" />
          <Badge className="absolute -top-0.5 -right-0.5 h-4 min-w-4 px-1 text-[10px]">
            0
          </Badge>
        </Button>

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
