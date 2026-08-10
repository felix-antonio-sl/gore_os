"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PageHeader } from "@/components/page-header";
import { PageGuard } from "@/components/page-guard";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDate } from "@/lib/format";
import { Receipt, CreditCard, Wallet, ChevronDown, ChevronRight, AlertTriangle, RotateCw } from "lucide-react";

interface RendicionItem {
  id: string;
  code: string;
  entered_at: string | null;
  agreement_number: string | null;
  ipr_codigo_bip: string | null;
  ipr_name: string | null;
  total_amount: number | null;
}

interface CdpItem {
  id: string;
  code: string;
  amount: number | null;
  created_at: string;
  ipr_codigo_bip: string | null;
  ipr_name: string | null;
  status: string;
}

interface CuotaItem {
  id: string;
  installment_number: number;
  amount: number | null;
  due_date: string;
  agreement_number: string | null;
  ipr_codigo_bip: string | null;
  payment_status: string;
}

interface PendingApprovals {
  rendiciones: RendicionItem[];
  cdps: CdpItem[];
  cuotas: CuotaItem[];
}

function Section({
  title,
  icon: Icon,
  count,
  children,
  defaultOpen = true,
}: {
  title: string;
  icon: React.ElementType;
  count: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-lg border bg-card">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-3 w-full px-4 py-3 text-left hover:bg-muted/50 transition-colors"
      >
        {open ? <ChevronDown className="size-4 text-muted-foreground" /> : <ChevronRight className="size-4 text-muted-foreground" />}
        <Icon className="size-4 text-muted-foreground" />
        <span className="text-sm font-medium flex-1">{title}</span>
        <Badge variant="secondary" className="text-xs">{count}</Badge>
      </button>
      {open && count > 0 && (
        <div className="border-t px-4 py-2 space-y-1">
          {children}
        </div>
      )}
      {open && count === 0 && (
        <div className="border-t px-4 py-4">
          <p className="text-sm text-muted-foreground text-center">Sin pendientes</p>
        </div>
      )}
    </div>
  );
}

function AprobacionesContent() {
  const router = useRouter();
  const { user } = useAuth();
  const [data, setData] = useState<PendingApprovals | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    api
      .get<PendingApprovals>("/api/dashboard/pending-approvals")
      .then((r) => { setData(r); setLoadError(null); })
      .catch((err) => {
        setData(null);
        setLoadError(err instanceof Error ? err.message : "No se pudieron cargar las aprobaciones");
      })
      .finally(() => setLoading(false));
  }, [refreshKey]);

  const handleRetry = () => {
    setLoading(true);
    setLoadError(null);
    setRefreshKey((k) => k + 1);
  };

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-12 w-full rounded bg-muted animate-pulse" />
        <div className="h-32 rounded-lg bg-muted animate-pulse" />
        <div className="h-32 rounded-lg bg-muted animate-pulse" />
        <div className="h-32 rounded-lg bg-muted animate-pulse" />
      </div>
    );
  }

  const totalPending =
    (data?.rendiciones.length ?? 0) +
    (data?.cdps.length ?? 0) +
    (data?.cuotas.length ?? 0);

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Aprobaciones"
        description={
          loadError
            ? "No se pudieron cargar las aprobaciones"
            : totalPending > 0
              ? `${totalPending} ítems pendientes en tu cola`
              : "Todas las aprobaciones al día"
        }
        accentColor="emerald"
      />

      {loadError ? (
        <EmptyState
          icon={<AlertTriangle className="size-10 stroke-1 text-amber-500" />}
          title="No se pudieron cargar los datos"
          description={loadError}
          action={
            <Button variant="outline" size="sm" onClick={handleRetry}>
              <RotateCw className="size-4 mr-1.5" />
              Reintentar
            </Button>
          }
        />
      ) : totalPending === 0 ? (
        <EmptyState
          title="Sin aprobaciones pendientes"
          description="No hay rendiciones, CDPs ni cuotas que requieran tu aprobación en este momento."
        />
      ) : null}

      {!loadError && (
        <>
      <Section
        title="Rendiciones por Aprobar"
        icon={Receipt}
        count={data?.rendiciones.length ?? 0}
      >
        {data?.rendiciones.map((r) => (
          <div
            key={r.id}
            className="flex items-center gap-3 py-2 px-2 rounded hover:bg-muted/50 cursor-pointer transition-colors"
            onClick={() => {
              if (r.ipr_codigo_bip) {
                router.push(`/datos?dominio=rendiciones`);
              }
            }}
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs">{r.code}</span>
                {r.agreement_number && (
                  <span className="text-xs text-muted-foreground">· Conv. {r.agreement_number}</span>
                )}
              </div>
              {r.ipr_name && (
                <p className="text-xs text-muted-foreground truncate">{r.ipr_codigo_bip} — {r.ipr_name}</p>
              )}
            </div>
            {r.total_amount != null && (
              <span className="text-xs font-medium tabular-nums shrink-0">
                {formatCurrency(r.total_amount)}
              </span>
            )}
            <Badge variant="outline" className="text-[10px] shrink-0">VISADA_RTF</Badge>
          </div>
        ))}
      </Section>

      <Section
        title="CDPs Pendientes"
        icon={Wallet}
        count={data?.cdps.length ?? 0}
        defaultOpen={(data?.cdps.length ?? 0) > 0}
      >
        {data?.cdps.map((c) => (
          <div
            key={c.id}
            className="flex items-center gap-3 py-2 px-2 rounded hover:bg-muted/50 cursor-pointer transition-colors"
            onClick={() => {
              if (c.ipr_codigo_bip) {
                router.push(`/presupuesto`);
              }
            }}
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs">{c.code}</span>
              </div>
              {c.ipr_name && (
                <p className="text-xs text-muted-foreground truncate">{c.ipr_codigo_bip} — {c.ipr_name}</p>
              )}
            </div>
            {c.amount != null && (
              <span className="text-xs font-medium tabular-nums shrink-0">
                {formatCurrency(c.amount)}
              </span>
            )}
          </div>
        ))}
      </Section>

      <Section
        title="Cuotas por Pagar"
        icon={CreditCard}
        count={data?.cuotas.length ?? 0}
        defaultOpen={(data?.cuotas.length ?? 0) > 0}
      >
        {data?.cuotas.map((q) => (
          <div
            key={q.id}
            className="flex items-center gap-3 py-2 px-2 rounded hover:bg-muted/50 cursor-pointer transition-colors"
            onClick={() => router.push(`/convenios`)}
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs">Cuota #{q.installment_number}</span>
                {q.agreement_number && (
                  <span className="text-xs text-muted-foreground">· Conv. {q.agreement_number}</span>
                )}
              </div>
              {q.due_date && (
                <p className="text-xs text-muted-foreground">Vence: {formatDate(q.due_date)}</p>
              )}
            </div>
            {q.amount != null && (
              <span className="text-xs font-medium tabular-nums shrink-0">
                {formatCurrency(q.amount)}
              </span>
            )}
          </div>
        ))}
      </Section>
        </>
      )}
    </div>
  );
}

export default function AprobacionesPage() {
  return (
    <PageGuard allowedRoles={["JEFE_DEPARTAMENTO", "ADMIN_SISTEMA"]}>
      <AprobacionesContent />
    </PageGuard>
  );
}
