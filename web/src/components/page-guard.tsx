"use client";

import { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { EmptyState } from "@/components/empty-state";
import { PageSkeleton } from "@/components/page-skeleton";
import { Button } from "@/components/ui/button";
import { ShieldX } from "lucide-react";
import type { RoleCode } from "@/types";

interface PageGuardProps {
  allowedRoles?: RoleCode[];
  allowedPopulations?: ("operativa" | "dgi")[];
  skeleton?: ReactNode;
  children: ReactNode;
}

export function PageGuard({
  allowedRoles,
  allowedPopulations,
  skeleton,
  children,
}: PageGuardProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  if (loading) {
    return <>{skeleton ?? <PageSkeleton variant="list" />}</>;
  }

  if (!user) return null;

  const roleAllowed = !allowedRoles || allowedRoles.includes(user.role_code);
  const popAllowed = !allowedPopulations || allowedPopulations.includes(user.population);

  if (!roleAllowed || !popAllowed) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<ShieldX className="size-10 stroke-1" />}
          title="Sin permisos"
          description="No tiene acceso a esta sección."
          action={
            <Button variant="outline" onClick={() => router.push("/dashboard")}>
              Volver al inicio
            </Button>
          }
        />
      </div>
    );
  }

  return <>{children}</>;
}
