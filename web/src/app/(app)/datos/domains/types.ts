import type React from "react";

export interface Column {
  key: string;
  label: string;
  render?: (value: unknown, row: unknown) => React.ReactNode;
}

export interface Filter {
  key: string;
  label: string;
  options: { value: string; label: string }[];
}

export interface FetchResult {
  items: unknown[];
  total: number;
  totalPages: number;
}

export interface DomainConfig {
  id: string;
  label: string;
  fetchData: (params: URLSearchParams) => Promise<FetchResult>;
  columns: Column[];
  filters: Filter[];
  searchPlaceholder: string;
  DetailPanel: React.ComponentType<{ item: unknown; onClose: () => void; onRefresh?: () => void }>;
  // Whether the API returns paginated (server) or plain array (client)
  paginationMode: "server" | "client";
  // Optional action component rendered above the filter bar (e.g. "Nueva Rendición")
  CreateAction?: React.ComponentType<{ onRefresh: () => void }>;
}
