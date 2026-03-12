"use client";

import { useAuth } from "@/lib/auth";
import { PageSkeleton } from "@/components/page-skeleton";
import { CommandCenter } from "./components/command-center";

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) return <PageSkeleton variant="dashboard" />;
  if (!user) return null;

  return <CommandCenter />;
}
