"use client";

import { Suspense } from "react";
import { PageHeader } from "@/components/page-header";
import { PageGuard } from "@/components/page-guard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTabParam } from "@/hooks/use-tab-param";
import { Users, Building2, Settings, Activity, Shield } from "lucide-react";
import { TabUsuarios } from "./components/tab-usuarios";
import { TabDivisiones } from "./components/tab-divisiones";
import { TabConfig } from "./components/tab-config";
import { TabMonitoreo } from "./components/tab-monitoreo";
import { TabAuditoria } from "./components/tab-auditoria";

export default function AdminPage() {
  return (
    <PageGuard allowedRoles={["ADMIN_SISTEMA"]}>
      <Suspense fallback={<div className="p-6"><div className="h-96 rounded-lg bg-muted animate-pulse" /></div>}>
        <AdminContent />
      </Suspense>
    </PageGuard>
  );
}

function AdminContent() {
  const [tab, setTab] = useTabParam("tab", "usuarios");

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Administración"
        description="Panel de administración del sistema"
        accentColor="violet"
      />

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="usuarios" className="flex items-center gap-1.5 text-xs">
            <Users className="size-3.5" />
            Usuarios
          </TabsTrigger>
          <TabsTrigger value="divisiones" className="flex items-center gap-1.5 text-xs">
            <Building2 className="size-3.5" />
            Divisiones
          </TabsTrigger>
          <TabsTrigger value="configuracion" className="flex items-center gap-1.5 text-xs">
            <Settings className="size-3.5" />
            Configuración
          </TabsTrigger>
          <TabsTrigger value="monitoreo" className="flex items-center gap-1.5 text-xs">
            <Activity className="size-3.5" />
            Monitoreo
          </TabsTrigger>
          <TabsTrigger value="auditoria" className="flex items-center gap-1.5 text-xs">
            <Shield className="size-3.5" />
            Auditoría
          </TabsTrigger>
        </TabsList>

        <TabsContent value="usuarios" className="mt-4">
          <TabUsuarios />
        </TabsContent>

        <TabsContent value="divisiones" className="mt-4">
          <TabDivisiones />
        </TabsContent>

        <TabsContent value="configuracion" className="mt-4">
          <TabConfig />
        </TabsContent>

        <TabsContent value="monitoreo" className="mt-4">
          <TabMonitoreo />
        </TabsContent>

        <TabsContent value="auditoria" className="mt-4">
          <TabAuditoria />
        </TabsContent>
      </Tabs>
    </div>
  );
}
