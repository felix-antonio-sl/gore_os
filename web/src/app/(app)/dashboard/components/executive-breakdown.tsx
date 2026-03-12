"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface DivisionBreakdown {
  division_name: string;
  vencidos: number;
  total_compromisos: number;
  problemas_abiertos: number;
  ejecucion_pct: number;
}

interface ExecutiveBreakdownProps {
  divisions: DivisionBreakdown[];
}

export function ExecutiveBreakdown({ divisions }: ExecutiveBreakdownProps) {
  const [divSort, setDivSort] = useState<"vencidos" | "ejecucion" | "name">("vencidos");

  const sorted = divisions.slice().sort((a, b) => {
    if (divSort === "vencidos") return b.vencidos - a.vencidos;
    if (divSort === "ejecucion") return b.ejecucion_pct - a.ejecucion_pct;
    return a.division_name.localeCompare(b.division_name);
  });

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="text-lg">Desglose por División</CardTitle>
        <div className="flex gap-1">
          {([["vencidos", "Vencidos"], ["ejecucion", "Ejecución"], ["name", "Nombre"]] as const).map(([key, label]) => (
            <Button key={key} size="sm" variant={divSort === key ? "default" : "ghost"} className="h-7 text-xs"
              onClick={() => setDivSort(key)}>{label}</Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {sorted.map((div) => (
            <div
              key={div.division_name}
              className="flex items-center justify-between py-2 border-b last:border-0"
            >
              <span className="font-medium text-sm">{div.division_name}</span>
              <div className="flex gap-2 items-center">
                {div.vencidos > 0 && (
                  <Badge variant="destructive" className="text-xs">
                    {div.vencidos} vencidos
                  </Badge>
                )}
                <Badge variant="outline" className="text-xs">
                  {div.total_compromisos} compromisos
                </Badge>
                {div.problemas_abiertos > 0 && (
                  <Badge variant="outline" className="text-xs border-orange-400 text-orange-600">
                    {div.problemas_abiertos} problemas
                  </Badge>
                )}
                <Badge
                  variant="secondary"
                  className={`text-xs ${
                    div.ejecucion_pct >= 70
                      ? "bg-green-100 text-green-800"
                      : div.ejecucion_pct >= 40
                      ? "bg-amber-100 text-amber-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {div.ejecucion_pct}% ejec.
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
