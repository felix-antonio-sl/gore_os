"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Scale } from "lucide-react";

interface PendingVBItem {
  id: string;
  act_number: string | null;
  subject: string;
  item_type: "acto" | "convenio";
  state: string;
  state_label: string;
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  created_at: string | null;
}

interface PendingVBResponse {
  items: PendingVBItem[];
  total: number;
}

export function ModuleJuridico() {
  const router = useRouter();
  const [data, setData] = useState<PendingVBResponse | null>(null);

  useEffect(() => {
    api
      .get<PendingVBResponse>("/api/dashboard/pending-vb")
      .then(setData)
      .catch(() => {});
  }, []);

  if (!data || data.items.length === 0) return null;

  return (
    <div className="rounded-xl border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center gap-2 mb-3">
        <Scale className="size-4 text-violet-600" />
        <h3 className="text-sm font-medium">Pendientes V.B. Juridico</h3>
        <Badge variant="outline" className="text-[10px] ml-auto">
          {data.total}
        </Badge>
      </div>
      <div className="space-y-2">
        {data.items.slice(0, 8).map((item) => (
          <button
            key={item.id}
            onClick={() => {
              if (item.item_type === "acto") {
                router.push(`/actos/${item.id}`);
              } else if (item.ipr_id) {
                router.push(`/ipr/${item.ipr_id}?tab=convenios`);
              } else {
                router.push("/convenios");
              }
            }}
            className="w-full flex items-center gap-2 text-xs text-left py-1.5 hover:bg-muted/50 rounded px-1 -mx-1"
          >
            <Badge variant="outline" className="text-[9px] shrink-0">
              {item.item_type === "acto" ? "Acto" : "Conv"}
            </Badge>
            <span className="truncate flex-1">{item.subject}</span>
            {item.ipr_codigo_bip && (
              <span className="text-blue-600 font-mono text-[10px] shrink-0">
                {item.ipr_codigo_bip}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
