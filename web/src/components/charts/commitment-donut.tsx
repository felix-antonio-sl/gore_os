"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
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
  PENDIENTE: "Pendiente",
  EN_PROGRESO: "En progreso",
  COMPLETADO: "Completado",
  VERIFICADO: "Verificado",
  CANCELADO: "Cancelado",
  VENCIDO: "Vencido",
};

export function CommitmentDonut({ data }: Props) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-xs text-muted-foreground">
        Sin datos de compromisos
      </div>
    );
  }

  const chartData = data.map((d) => ({
    ...d,
    label: LABEL_MAP[d.name] ?? d.name,
  }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="label"
          cx="50%"
          cy="50%"
          innerRadius={45}
          outerRadius={72}
          paddingAngle={2}
        >
          {chartData.map((entry, index) => (
            <Cell
              key={index}
              fill={entry.color ?? "#9ca3af"}
            />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number, name: string) => [value, name]}
          contentStyle={{ fontSize: 11, borderRadius: 6 }}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ fontSize: 10 }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
