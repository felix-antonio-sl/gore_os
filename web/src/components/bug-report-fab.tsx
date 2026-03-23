"use client";

import { useState, useEffect } from "react";
import { Bug } from "lucide-react";
import { DrawerPanel } from "@/components/drawer-panel";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

const SEVERITY_OPTIONS = [
  { value: "CRITICO", label: "Crítico", color: "bg-red-500", activeRing: "ring-red-500" },
  { value: "ALTO", label: "Alto", color: "bg-amber-500", activeRing: "ring-amber-500" },
  { value: "MEDIO", label: "Medio", color: "bg-blue-500", activeRing: "ring-blue-500" },
  { value: "BAJO", label: "Bajo", color: "bg-green-500", activeRing: "ring-green-500" },
] as const;

export function BugReportFab() {
  const [devMode, setDevMode] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setDevMode(localStorage.getItem("goreos_dev_mode") === "true");
  }, []);

  if (!devMode) return null;

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-4 right-4 z-50 flex items-center justify-center size-12 rounded-full bg-amber-500 text-white shadow-lg hover:bg-amber-600 transition-colors cursor-pointer"
        title="Reportar Bug"
      >
        <Bug className="size-5" />
      </button>
      <BugReportDrawer open={open} onClose={() => setOpen(false)} />
    </>
  );
}

function BugReportDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { user } = useAuth();
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [severity, setSeverity] = useState("MEDIO");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);

  // Handle image paste from clipboard
  useEffect(() => {
    if (!open) return;
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;
      for (const item of items) {
        if (item.type.startsWith("image/")) {
          const file = item.getAsFile();
          if (file) {
            const reader = new FileReader();
            reader.onload = () => setScreenshot(reader.result as string);
            reader.readAsDataURL(file);
          }
          break;
        }
      }
    };
    window.addEventListener("paste", handlePaste);
    return () => window.removeEventListener("paste", handlePaste);
  }, [open]);

  // Handle file input
  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setScreenshot(reader.result as string);
    reader.readAsDataURL(file);
  }

  const context = {
    user_email: user?.email ?? "",
    role_code: user?.role_code ?? "",
    population: user?.population ?? null,
    division_id: user?.division_id ? String(user.division_id) : null,
    url: typeof window !== "undefined" ? window.location.pathname + window.location.search : "",
    viewport: typeof window !== "undefined" ? `${window.innerWidth}x${window.innerHeight}` : null,
    checklist_item: typeof window !== "undefined" ? localStorage.getItem("goreos_active_checklist_item") : null,
    screenshot,
  };

  async function handleSubmit() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api.post("/api/dev/bugs", {
        title: title.trim(),
        severity,
        description: description.trim() || null,
        ...context,
      });
      setTitle("");
      setDescription("");
      setSeverity("MEDIO");
      setScreenshot(null);
      onClose();
      const { toast } = await import("sonner");
      toast.success("Bug guardado");
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  return (
    <DrawerPanel open={open} onClose={onClose} title="Reportar Bug">
      <div className="space-y-4">
        {/* Auto-context summary */}
        <div className="rounded-md bg-muted p-3 text-xs text-muted-foreground space-y-1">
          <p>
            <span className="font-medium">Usuario:</span> {context.user_email} ({context.role_code})
          </p>
          <p>
            <span className="font-medium">URL:</span> {context.url}
          </p>
          {context.checklist_item && (
            <p>
              <span className="font-medium">Checklist:</span> {context.checklist_item}
            </p>
          )}
        </div>

        {/* Title */}
        <div>
          <label htmlFor="bug-title" className="text-sm font-medium">
            Título <span className="text-red-500">*</span>
          </label>
          <input
            id="bug-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Qué salió mal..."
            className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        {/* Severity */}
        <div>
          <label className="text-sm font-medium">Severidad</label>
          <div className="mt-1 flex gap-1">
            {SEVERITY_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setSeverity(opt.value)}
                className={`flex-1 rounded-md px-2 py-1.5 text-xs font-medium transition-all cursor-pointer ${
                  severity === opt.value
                    ? `${opt.color} text-white ring-2 ${opt.activeRing} ring-offset-1`
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="bug-description" className="text-sm font-medium">
            Descripción
          </label>
          <textarea
            id="bug-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Detalles adicionales..."
            rows={3}
            className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
          />
        </div>

        {/* Screenshot upload */}
        <div>
          <label className="text-sm font-medium">Captura</label>
          <div className="mt-1">
            {screenshot ? (
              <div className="relative">
                <img
                  src={screenshot}
                  alt="Captura de pantalla"
                  className="w-full rounded-md border"
                />
                <button
                  type="button"
                  onClick={() => setScreenshot(null)}
                  className="absolute top-1 right-1 bg-black/60 text-white rounded-full size-5 flex items-center justify-center text-xs hover:bg-black/80"
                >
                  ✕
                </button>
              </div>
            ) : (
              <label className="flex flex-col items-center gap-1.5 rounded-md border border-dashed p-4 text-xs text-muted-foreground cursor-pointer hover:bg-muted/30 transition-colors">
                <span>📋 Pegar imagen (Ctrl+V / ⌘V)</span>
                <span className="text-[10px]">o click para seleccionar archivo</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </label>
            )}
          </div>
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={saving || !title.trim()}
          className="w-full rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {saving ? "Guardando..." : "Guardar Bug"}
        </button>
      </div>
    </DrawerPanel>
  );
}
