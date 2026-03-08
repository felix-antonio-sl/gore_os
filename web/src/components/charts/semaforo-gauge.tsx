"use client";

import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
} from "recharts";

interface Props {
  signal: "VERDE" | "AMARILLO" | "ROJO" | string;
  label: string;
  dimension: string;
}

const SIGNAL_CONFIG = {
  VERDE:    { color: "#10b981", value: 90, bg: "#d1fae5" },
  AMARILLO: { color: "#f59e0b", value: 55, bg: "#fef3c7" },
  ROJO:     { color: "#ef4444", value: 20, bg: "#fee2e2" },
};

const SIGNAL_LABEL: Record<string, string> = {
  VERDE: "Óptimo",
  AMARILLO: "Atención",
  ROJO: "Crítico",
};

export function SemaforoGauge({ signal, label }: Props) {
  const config = SIGNAL_CONFIG[signal as keyof typeof SIGNAL_CONFIG] ?? {
    color: "#9ca3af",
    value: 50,
    bg: "#f3f4f6",
  };

  const chartData = [{ name: label, value: config.value, fill: config.color }];

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-20 h-20">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="60%"
            outerRadius="100%"
            barSize={8}
            data={chartData}
            startAngle={180}
            endAngle={0}
          >
            {/* Track background */}
            <RadialBar
              dataKey="value"
              cornerRadius={4}
              background={{ fill: config.bg }}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center mt-3">
          <span className="text-[10px] font-bold" style={{ color: config.color }}>
            {SIGNAL_LABEL[signal] ?? signal}
          </span>
        </div>
      </div>
      <p className="text-[10px] text-center text-muted-foreground leading-tight max-w-16">
        {label}
      </p>
    </div>
  );
}
