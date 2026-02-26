"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from "recharts";

interface BudgetChartPoint {
  division: string;
  ejecucion_pct: number;
  pagado: number;
  vigente: number;
}

interface Props {
  data: BudgetChartPoint[];
}

function getBarColor(pct: number): string {
  if (pct >= 70) return "#10b981"; // verde
  if (pct >= 40) return "#f59e0b"; // ámbar
  return "#ef4444";                // rojo
}

export function ExecutionBarChart({ data }: Props) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-xs text-muted-foreground">
        Sin datos presupuestarios
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
        <XAxis
          dataKey="division"
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => `${v}%`}
        />
        <Tooltip
          formatter={(value: number) => [`${value}%`, "Ejecución"]}
          contentStyle={{ fontSize: 11, borderRadius: 6 }}
        />
        <Bar dataKey="ejecucion_pct" radius={[3, 3, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={getBarColor(entry.ejecucion_pct)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
