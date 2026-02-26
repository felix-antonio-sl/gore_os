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

interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

interface Props {
  data: ChartDataPoint[];
}

const LABEL_MAP: Record<string, string> = {
  CRITICO: "Crítico",
  ALTO: "Alto",
  ATENCION: "Atención",
  INFO: "Info",
  SIN_CLASIFICAR: "Sin clasificar",
};

const ORDER = ["CRITICO", "ALTO", "ATENCION", "INFO", "SIN_CLASIFICAR"];

export function AlertsBySeverity({ data }: Props) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-xs text-muted-foreground">
        Sin alertas activas
      </div>
    );
  }

  const sorted = [...data].sort(
    (a, b) => (ORDER.indexOf(a.name) ?? 99) - (ORDER.indexOf(b.name) ?? 99)
  );

  const chartData = sorted.map((d) => ({
    ...d,
    label: LABEL_MAP[d.name] ?? d.name,
  }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 4, right: 24, left: 48, bottom: 4 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e5e7eb" />
        <XAxis
          type="number"
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          allowDecimals={false}
        />
        <YAxis
          type="category"
          dataKey="label"
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          formatter={(value: number) => [value, "Alertas"]}
          contentStyle={{ fontSize: 11, borderRadius: 6 }}
        />
        <Bar dataKey="value" radius={[0, 3, 3, 0]} barSize={16}>
          {chartData.map((entry, index) => (
            <Cell key={index} fill={entry.color ?? "#9ca3af"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
