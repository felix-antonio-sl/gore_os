"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { domainRegistry } from "./domains";
import { exportCSV } from "@/lib/csv-export";

// ---------------------------------------------------------------------------
// Domain sidebar config
// ---------------------------------------------------------------------------

const DOMAINS = [
  { id: "ipr", label: "IPR" },
  { id: "indicadores", label: "Indicadores" },
  { id: "presupuesto", label: "Presupuesto" },
  { id: "convenios", label: "Convenios" },
  { id: "organizaciones", label: "Organizaciones" },
  { id: "personas", label: "Personas" },
  { id: "territorio", label: "Territorio" },
  { id: "eventos", label: "Eventos" },
  { id: "rendiciones", label: "Rendiciones" },
] as const;

type DomainId = (typeof DOMAINS)[number]["id"];

// ---------------------------------------------------------------------------
// Main page — generic orchestrator
// ---------------------------------------------------------------------------

export default function DatosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const { user } = useAuth();

  const domainParam = (searchParams.get("dominio") as DomainId) ?? "ipr";
  const activeDomain: DomainId = DOMAINS.find((d) => d.id === domainParam)?.id ?? "ipr";

  // H12: Auto pre-filter rendiciones for RTF role
  useEffect(() => {
    if (user?.role_code === "RTF" && activeDomain === "rendiciones" && !searchParams.has("state")) {
      const params = new URLSearchParams(searchParams.toString());
      params.set("state", "EN_REVISION_RTF");
      router.replace(`${pathname}?${params.toString()}`);
    }
  }, [user, activeDomain, searchParams, pathname, router]);

  const page = Number(searchParams.get("page") ?? "1");

  // Generic data state
  const [items, setItems] = useState<unknown[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<unknown | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const config = domainRegistry[activeDomain];

  // Build filter values from URL params (generic — whatever keys the domain defines)
  const filterValues: Record<string, string> = {};
  if (config) {
    for (const filter of config.filters) {
      filterValues[filter.key] = searchParams.get(filter.key) ?? "";
    }
  }

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) {
          params.delete(k);
        } else {
          params.set(k, String(v));
        }
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  const handleDomainChange = (domain: DomainId) => {
    setSelectedItem(null);
    setItems([]);
    router.push(`${pathname}?dominio=${domain}`);
  };

  const handleFilterChange = (key: string, value: string) => {
    router.push(buildUrl({ [key]: value, page: 1 }));
  };

  const handleSearchChange = (value: string) => {
    router.push(buildUrl({ search: value, page: 1 }));
  };

  const handleClear = () => {
    router.push(`${pathname}?dominio=${activeDomain}`);
  };

  const handlePageChange = (newPage: number) => {
    router.push(buildUrl({ page: newPage }));
  };

  // Fetch data using domain config
  useEffect(() => {
    if (!config) return;
    setIsLoading(true);
    setLoadError(null);
    setSelectedItem(null);

    config
      .fetchData(searchParams)
      .then(({ items: newItems, total: newTotal, totalPages: newTotalPages }) => {
        setItems(newItems);
        setTotal(newTotal);
        setTotalPages(newTotalPages);
        setLoadError(null);
      })
      .catch((err: Error) => {
        setItems([]);
        setTotal(0);
        setTotalPages(1);
        setLoadError(err?.message || "No se pudieron cargar los datos de este dominio.");
      })
      .finally(() => setIsLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeDomain, searchParams.toString(), refreshKey]);

  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia("(max-width: 767px)");
    setIsMobile(mql.matches);
    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  const hasDetailPanel = selectedItem !== null;

  // Active filters: any domain filter set, or a non-empty search term.
  const hasActiveFilters =
    (searchParams.get("search") ?? "") !== "" ||
    (config?.filters ?? []).some((f) => (searchParams.get(f.key) ?? "") !== "");

  const triggerRefresh = () => setRefreshKey((k) => k + 1);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-5 py-3 border-b flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-lg font-bold leading-tight">Explorador de Datos</h1>
          <p className="text-[11px] text-muted-foreground mt-0.5">
            Acceso analítico a los dominios de datos de GORE Ñuble
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="h-8 text-xs gap-1.5"
          onClick={() => {
            if (config && items.length > 0) {
              const date = new Date().toISOString().slice(0, 10);
              exportCSV(config.columns, items, `goreos_${activeDomain}_${date}`);
            }
          }}
        >
          <Download className="size-3.5" />
          Exportar CSV
        </Button>
      </div>

      {/* Mobile domain selector */}
      <div className="px-5 py-2 border-b md:hidden">
        <Select value={activeDomain} onValueChange={(v) => handleDomainChange(v as DomainId)}>
          <SelectTrigger className="h-9">
            <SelectValue placeholder="Dominio" />
          </SelectTrigger>
          <SelectContent>
            {DOMAINS.map((domain) => (
              <SelectItem key={domain.id} value={domain.id}>
                {domain.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Body: responsive layout */}
      <div
        className={cn(
          "flex-1 overflow-hidden grid grid-cols-1",
          hasDetailPanel && !isMobile
            ? "md:grid-cols-[200px_1fr_340px]"
            : "md:grid-cols-[200px_1fr]"
        )}
      >
        {/* Left: Domain sidebar (desktop only) */}
        <aside className="border-r bg-muted/20 overflow-y-auto hidden md:block">
          <div className="py-2">
            <p className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Dominios
            </p>
            {DOMAINS.map((domain) => (
              <button
                key={domain.id}
                onClick={() => handleDomainChange(domain.id)}
                className={cn(
                  "w-full text-left px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
                  activeDomain === domain.id
                    ? "bg-accent text-accent-foreground font-medium"
                    : "text-muted-foreground"
                )}
              >
                {domain.label}
              </button>
            ))}
          </div>
        </aside>

        {/* Center: Generic data table */}
        <div className="overflow-auto flex flex-col">
          {config ? (
            <div className="flex flex-col h-full">
              {config.filters.length > 0 && (
                <div className="px-4 pt-3 pb-2 border-b shrink-0">
                  <FilterBar
                    filters={config.filters}
                    values={filterValues}
                    onChange={handleFilterChange}
                    onClear={handleClear}
                    searchPlaceholder={config.searchPlaceholder}
                    searchValue={searchParams.get("search") ?? ""}
                    onSearchChange={handleSearchChange}
                  />
                </div>
              )}
              {/* Search-only bar for domains with no filter dropdowns */}
              {config.filters.length === 0 && (
                <div className="px-4 pt-3 pb-2 border-b shrink-0">
                  {config.CreateAction && (
                    <div className="flex justify-end mb-2">
                      <config.CreateAction onRefresh={() => setRefreshKey((k) => k + 1)} />
                    </div>
                  )}
                  <FilterBar
                    filters={[]}
                    values={{}}
                    onChange={handleFilterChange}
                    onClear={handleClear}
                    searchPlaceholder={config.searchPlaceholder}
                    searchValue={searchParams.get("search") ?? ""}
                    onSearchChange={handleSearchChange}
                  />
                </div>
              )}
              <div className="px-4 py-3 flex-1 overflow-auto">
                <DataTable
                  columns={config.columns}
                  data={items}
                  page={page}
                  totalPages={totalPages}
                  total={total}
                  onPageChange={handlePageChange}
                  onRowClick={(row) => setSelectedItem(row)}
                  isLoading={isLoading}
                  error={loadError}
                  onRetry={triggerRefresh}
                  hasActiveFilters={hasActiveFilters}
                  onClearFilters={handleClear}
                  emptyTitle="Sin datos para este dominio"
                  emptyDescription="No hay registros disponibles en este dominio por ahora."
                />
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <p className="text-sm">Dominio no encontrado.</p>
            </div>
          )}
        </div>

        {/* Right: Detail panel — inline on desktop */}
        {hasDetailPanel && config && !isMobile && (
          <div className="border-l bg-background overflow-hidden flex flex-col">
            <config.DetailPanel
              item={selectedItem}
              onClose={() => setSelectedItem(null)}
              onRefresh={() => { setSelectedItem(null); setRefreshKey(k => k + 1); }}
            />
          </div>
        )}
      </div>

      {/* Mobile: Detail panel as DrawerPanel */}
      {isMobile && config && (
        <DrawerPanel
          open={hasDetailPanel}
          onClose={() => setSelectedItem(null)}
          title="Detalle"
        >
          {hasDetailPanel && (
            <config.DetailPanel
              item={selectedItem}
              onClose={() => setSelectedItem(null)}
              onRefresh={() => { setSelectedItem(null); setRefreshKey(k => k + 1); }}
            />
          )}
        </DrawerPanel>
      )}
    </div>
  );
}
