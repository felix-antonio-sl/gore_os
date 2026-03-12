"use client";

import { useAuth } from "@/lib/auth";
import { PageSkeleton } from "@/components/page-skeleton";
import { OperationalDashboard } from "./components/operational-dashboard";
import { DgiCockpitRouter } from "./components/dgi-cockpit-router";

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) return <PageSkeleton variant="dashboard" />;
  if (!user) return null;

  if (user.population === "dgi") return <DgiCockpitRouter />;
  return <OperationalDashboard />;
}
