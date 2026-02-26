"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "@/lib/api";

interface SnapshotPoint {
  value: number | null;
  signal: string | null;
  recorded_at: string;
}

interface SparklineIndicatorProps {
  indicatorId: string;
  days?: number;
}

const SIGNAL_COLORS: Record<string, string> = {
  VERDE: "#22c55e",
  AMARILLO: "#f59e0b",
  ROJO: "#ef4444",
};

export function SparklineIndicator({ indicatorId, days = 90 }: SparklineIndicatorProps) {
  const [data, setData] = useState<SnapshotPoint[]>([]);

  useEffect(() => {
    api
      .get<SnapshotPoint[]>(`/api/dgi/data/indicators/${indicatorId}/history?days=${days}`)
      .then(setData)
      .catch(() => setData([]));
  }, [indicatorId, days]);

  if (data.length < 2) return null;

  const lastSignal = data[data.length - 1]?.signal ?? "VERDE";
  const strokeColor = SIGNAL_COLORS[lastSignal] ?? "#6b7280";

  return (
    <div className="h-8 w-24">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <Line
            type="monotone"
            dataKey="value"
            stroke={strokeColor}
            strokeWidth={1.5}
            dot={false}
          />
          <Tooltip
            contentStyle={{ fontSize: "10px", padding: "2px 6px" }}
            formatter={(v: number) => [`${v}%`, "Valor"]}
            labelFormatter={(_, payload) => {
              const p = payload?.[0]?.payload as SnapshotPoint | undefined;
              if (!p) return "";
              return new Date(p.recorded_at).toLocaleDateString("es-CL");
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
