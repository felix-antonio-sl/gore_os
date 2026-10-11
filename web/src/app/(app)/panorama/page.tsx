"use client";

import { useAuth } from "@/lib/auth";
import { PageSkeleton } from "@/components/page-skeleton";
import { OperationalOverview } from "./components/operational-overview";
import { DgiCockpitRouter } from "./components/dgi-cockpit-router";

export default function PanoramaPage() {
  const { user, loading } = useAuth();
  if (loading) return <PageSkeleton variant="dashboard" />;
  if (!user) return null;
  return user.population === "dgi" ? <DgiCockpitRouter /> : <OperationalOverview />;
}
