"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DrawerPanel } from "@/components/drawer-panel";
import { Card, CardContent } from "@/components/ui/card";
import { ComboboxAsync } from "@/components/combobox-async";
import { toast } from "sonner";
import { Plus, ShieldAlert } from "lucide-react";
import { formatDate } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { RISK_STATUS_COLORS, RISK_PROBABILITY_COLORS } from "@/lib/status-colors";
import { DGI_ROLES } from "@/types";
import type { PaginatedResponse, RiskListItem, RiskMatrixCell, RiskSummary } from "@/types";

const STATUS_TABS = ["TODOS", "IDENTIFICADO", "EN_EVALUACION", "EN_MITIGACION", "MITIGADO", "ACEPTADO", "CERRADO"];

const WRITE_ROLES = [...DGI_ROLES, "ADMIN_REGIONAL", "ADMIN_SISTEMA"];

export default function RiesgosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const canWrite = user && WRITE_ROLES.includes(user.role_code);

  const [data, setData] = useState<PaginatedResponse<RiskListItem> | null>(null);
  const [matrix, setMatrix] = useState<RiskMatrixCell[]>([]);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [showMatrix, setShowMatrix] = useState(false);

  const [form, setForm] = useState({
    name: "",
    risk_type_id: "",
    probability_id: "",
    impact_id: "",
    subject_type: "core.ipr",
    subject_id: "",
    mitigation_plan: "",
  });

  // Category options loaded once
  const [riskTypes, setRiskTypes] = useState<{ id: string; code: string; label: string }[]>([]);
  const [probabilities, setProbabilities] = useState<{ id: string; code: string; label: string }[]>([]);
  const [impacts, setImpacts] = useState<{ id: string; code: string; label: string }[]>([]);

  const page = Number(searchParams.get("page") ?? "1");
  const statusFilter = searchParams.get("status") ?? "";

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) params.delete(k);
        else params.set(k, String(v));
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  // Load categories
  useEffect(() => {
    api.get<{ id: string; code: string; label: string }[]>("/api/catalogs/categories?scheme=risk_type").then(setRiskTypes).catch(() => {});
    api.get<{ id: string; code: string; label: string }[]>("/api/catalogs/categories?scheme=risk_probability").then(setProbabilities).catch(() => {});
    api.get<{ id: string; code: string; label: string }[]>("/api/catalogs/categories?scheme=problem_impact").then(setImpacts).catch(() => {});
  }, []);

  const fetchData = () => {
    setLoading(true);
    const statusParam = statusFilter && statusFilter !== "TODOS" ? `&status=${statusFilter}` : "";
    api
      .get<PaginatedResponse<RiskListItem>>(`/api/risk?page=${page}&page_size=20${statusParam}`)
      .then(setData)
      .catch(() => {
        setData(null);
        toast.error("Error al cargar riesgos");
      })
      .finally(() => setLoading(false));
  };

  const fetchMatrix = () => {
    api.get<RiskMatrixCell[]>("/api/risk/matrix").then(setMatrix).catch(() => {});
  };

  useEffect(() => {
    fetchData();
    fetchMatrix();
  }, [page, statusFilter]);

  const handleCreate = async () => {
    if (!form.name.trim() || !form.subject_id) {
      toast.error("Nombre y sujeto son obligatorios");
      return;
    }
    setCreating(true);
    try {
      const result = await api.post<RiskListItem>("/api/risk", {
        name: form.name,
        risk_type_id: form.risk_type_id || undefined,
        probability_id: form.probability_id || undefined,
        impact_id: form.impact_id || undefined,
        subject_type: form.subject_type,
        subject_id: form.subject_id,
        mitigation_plan: form.mitigation_plan || undefined,
      });
      toast.success(`Riesgo ${result.code} creado`);
      setDrawerOpen(false);
      setForm({ name: "", risk_type_id: "", probability_id: "", impact_id: "", subject_type: "core.ipr", subject_id: "", mitigation_plan: "" });
      router.push(`/riesgos/${result.id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear riesgo");
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      key: "code",
      label: "Codigo",
      render: (v: unknown) => <span className="font-mono text-xs">{String(v ?? "-")}</span>,
    },
    {
      key: "name",
      label: "Nombre",
      render: (v: unknown) => <span className="text-sm line-clamp-1 max-w-xs">{String(v ?? "-")}</span>,
    },
    {
      key: "risk_type",
      label: "Tipo",
      render: (_v: unknown, row: unknown) => {
        const r = row as RiskListItem;
        return r.risk_type_label ? (
          <Badge variant="outline" className="text-xs">{r.risk_type_label}</Badge>
        ) : <span className="text-xs text-muted-foreground">-</span>;
      },
    },
    {
      key: "probability",
      label: "Probabilidad",
      render: (_v: unknown, row: unknown) => {
        const r = row as RiskListItem;
        return r.probability ? (
          <Badge variant="outline" className={`text-xs ${RISK_PROBABILITY_COLORS[r.probability] ?? ""}`}>
            {r.probability_label}
          </Badge>
        ) : <span className="text-xs text-muted-foreground">-</span>;
      },
    },
    {
      key: "impact",
      label: "Impacto",
      render: (_v: unknown, row: unknown) => {
        const r = row as RiskListItem;
        return r.impact_label ? (
          <Badge variant="outline" className="text-xs">{r.impact_label}</Badge>
        ) : <span className="text-xs text-muted-foreground">-</span>;
      },
    },
    {
      key: "status",
      label: "Estado",
      render: (_v: unknown, row: unknown) => {
        const r = row as RiskListItem;
        return r.status ? (
          <Badge variant="outline" className={`text-xs ${RISK_STATUS_COLORS[r.status] ?? ""}`}>
            {r.status_label}
          </Badge>
        ) : <span className="text-xs text-muted-foreground">-</span>;
      },
    },
    {
      key: "subject_label",
      label: "Sujeto",
      render: (v: unknown) => (
        <span className="text-xs text-blue-600 line-clamp-1 max-w-[12rem]">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "identified_at",
      label: "Identificado",
      render: (v: unknown) => v ? <span className="text-xs">{formatDate(v as string)}</span> : <span className="text-xs text-muted-foreground">-</span>,
    },
  ];

  // Risk matrix rendering
  const PROB_ORDER = ["MUY_ALTA", "ALTA", "MEDIA", "BAJA", "MUY_BAJA"];
  const IMPACT_ORDER = ["BLOQUEA_PAGO", "RETRASA_OBRA", "RETRASA_CONVENIO", "RIESGO_RENDICION", "INCUMPLIMIENTO_PLAZO", "OTRO"];

  const matrixLookup = new Map<string, number>();
  matrix.forEach((c) => matrixLookup.set(`${c.probability}|${c.impact}`, c.count));

  const cellColor = (count: number) => {
    if (count === 0) return "bg-muted/30";
    if (count === 1) return "bg-green-100 text-green-800";
    if (count <= 2) return "bg-amber-100 text-amber-800";
    return "bg-red-100 text-red-800 font-semibold";
  };

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Registro de Riesgos"
        description="Riesgos identificados en IPRs y procesos institucionales"
        accentColor="rose"
        actions={
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowMatrix(!showMatrix)}
            >
              {showMatrix ? "Ocultar Matriz" : "Matriz de Riesgo"}
            </Button>
            {canWrite && (
              <Button size="sm" onClick={() => setDrawerOpen(true)}>
                <Plus className="size-4 mr-1" />
                Nuevo Riesgo
              </Button>
            )}
          </div>
        }
      />

      {/* Risk Matrix */}
      {showMatrix && (
        <Card className="animate-in fade-in duration-200">
          <CardContent className="pt-6 overflow-x-auto">
            <h3 className="text-sm font-semibold mb-3">Matriz Probabilidad x Impacto</h3>
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr>
                  <th className="p-2 text-left">Prob \ Impacto</th>
                  {IMPACT_ORDER.map((imp) => (
                    <th key={imp} className="p-2 text-center border">{imp.replace(/_/g, " ")}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {PROB_ORDER.map((prob) => (
                  <tr key={prob}>
                    <td className="p-2 font-medium border">{prob.replace(/_/g, " ")}</td>
                    {IMPACT_ORDER.map((imp) => {
                      const count = matrixLookup.get(`${prob}|${imp}`) ?? 0;
                      return (
                        <td key={imp} className={`p-2 text-center border ${cellColor(count)}`}>
                          {count}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Status filter tabs */}
      <div className="flex gap-1 flex-wrap">
        {STATUS_TABS.map((tab) => (
          <Button
            key={tab}
            variant={
              (statusFilter === tab || (!statusFilter && tab === "TODOS"))
                ? "default"
                : "outline"
            }
            size="sm"
            onClick={() => router.push(buildUrl({ status: tab === "TODOS" ? "" : tab, page: 1 }))}
          >
            {tab === "TODOS"
              ? "Todos"
              : tab === "EN_EVALUACION" ? "En Evaluación"
              : tab === "EN_MITIGACION" ? "En Mitigación"
              : tab === "MUY_ALTA" ? "Muy Alta"
              : tab.charAt(0) + tab.slice(1).toLowerCase()}
          </Button>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={(p) => router.push(buildUrl({ page: p }))}
        onRowClick={(row) => router.push(`/riesgos/${(row as RiskListItem).id}`)}
        isLoading={loading}
      />

      {/* Create drawer */}
      <DrawerPanel open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Nuevo Riesgo">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Nombre *</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Nombre descriptivo del riesgo"
              />
            </div>
            <div className="space-y-2">
              <Label>Tipo de Riesgo</Label>
              <Select value={form.risk_type_id} onValueChange={(v) => setForm({ ...form, risk_type_id: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar tipo" />
                </SelectTrigger>
                <SelectContent>
                  {riskTypes.map((t) => (
                    <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Probabilidad</Label>
              <Select value={form.probability_id} onValueChange={(v) => setForm({ ...form, probability_id: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar probabilidad" />
                </SelectTrigger>
                <SelectContent>
                  {probabilities.map((t) => (
                    <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Impacto</Label>
              <Select value={form.impact_id} onValueChange={(v) => setForm({ ...form, impact_id: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar impacto" />
                </SelectTrigger>
                <SelectContent>
                  {impacts.map((t) => (
                    <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Sujeto *</Label>
              <Select value={form.subject_type} onValueChange={(v) => setForm({ ...form, subject_type: v, subject_id: "" })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="core.ipr">IPR</SelectItem>
                  <SelectItem value="core.dgi_process">Proceso</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>{form.subject_type === "core.ipr" ? "IPR" : "Proceso"} *</Label>
              <ComboboxAsync
                value={form.subject_id}
                onChange={(v) => setForm({ ...form, subject_id: v })}
                searchFn={async (term) => {
                  if (form.subject_type === "core.ipr") {
                    const items = await api.get<{ id: string; codigo_bip: string; name: string }[]>(
                      `/api/catalogs/iprs?search=${encodeURIComponent(term)}`
                    );
                    return items.map((i) => ({ value: i.id, label: `${i.codigo_bip} — ${i.name}` }));
                  }
                  const items = await api.get<{ items: { id: string; code: string; name: string }[] }>(
                    `/api/dgi/processes?search=${encodeURIComponent(term)}&page_size=20`
                  );
                  return (items.items ?? []).map((i) => ({ value: i.id, label: `${i.code} — ${i.name}` }));
                }}
                placeholder={form.subject_type === "core.ipr" ? "Buscar IPR..." : "Buscar proceso..."}
              />
            </div>
            <div className="space-y-2">
              <Label>Plan de Mitigacion</Label>
              <Textarea
                value={form.mitigation_plan}
                onChange={(e) => setForm({ ...form, mitigation_plan: e.target.value })}
                placeholder="Descripcion del plan de mitigacion"
                rows={3}
              />
            </div>
            <Button className="w-full" onClick={handleCreate} disabled={creating}>
              {creating ? "Creando..." : "Crear Riesgo"}
            </Button>
          </div>
      </DrawerPanel>
    </div>
  );
}
