"use client";

import { useAuth } from "@/lib/auth";
import { PageSkeleton } from "@/components/page-skeleton";
import { CommandCenter } from "./components/command-center";
import { DgiCockpitRouter } from "./components/dgi-cockpit-router";

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) return <PageSkeleton variant="dashboard" />;
  if (!user) return null;

  // DGI population gets the role-specific cockpit (Jefe DGI, Control de Gestión,
  // Procesos, TD); the operational population gets the unified Centro de Comando.
  if (user.population === "dgi") return <DgiCockpitRouter />;

  return <CommandCenter />;
}
