"use client";

import { ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";
import { Sheet, SheetContent } from "@/components/ui/sheet";

interface AppShellProps {
  children: ReactNode;
}

function getWeekNumber(date: Date): number {
  const oneJan = new Date(date.getFullYear(), 0, 1);
  const numberOfDays = Math.floor((date.getTime() - oneJan.getTime()) / (24 * 60 * 60 * 1000));
  return Math.ceil((numberOfDays + oneJan.getDay() + 1) / 7);
}

export function AppShell({ children }: AppShellProps) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="size-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <p className="text-sm text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const weekNumber = getWeekNumber(new Date());

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar — desktop */}
      <div className="hidden md:block shrink-0">
        <Sidebar />
      </div>

      {/* Sidebar — mobile */}
      <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
        <SheetContent side="left" className="w-56 p-0 bg-sidebar border-sidebar-border">
          <Sidebar onNavClick={() => setMobileNavOpen(false)} />
        </SheetContent>
      </Sheet>

      {/* Main content area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <div className="h-14 shrink-0">
          <Header onMenuToggle={() => setMobileNavOpen(true)} />
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-0">
          {children}
        </main>

        {/* Status bar */}
        <div className="h-8 border-t text-xs px-4 flex items-center justify-between text-muted-foreground bg-background shrink-0">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="inline-block size-2 rounded-full bg-green-500" />
              Conectado
            </span>
            <span className="hidden sm:inline">
              {user.role_label}
            </span>
          </div>
          <span>Semana {weekNumber} · {new Date().getFullYear()}</span>
        </div>
      </div>
    </div>
  );
}
