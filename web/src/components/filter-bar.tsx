"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { XIcon } from "lucide-react";

interface FilterOption {
  value: string;
  label: string;
}

interface Filter {
  key: string;
  label: string;
  options: FilterOption[];
}

interface FilterBarProps {
  filters: Filter[];
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
  onClear: () => void;
  searchPlaceholder?: string;
  searchValue?: string;
  onSearchChange?: (v: string) => void;
  /** Debounce delay in ms for search input (default 300) */
  searchDebounceMs?: number;
}

export function FilterBar({
  filters,
  values,
  onChange,
  onClear,
  searchPlaceholder = "Buscar...",
  searchValue,
  onSearchChange,
  searchDebounceMs = 300,
}: FilterBarProps) {
  const activeFilters = Object.entries(values).filter(([, v]) => v && v !== "");
  const hasSearch = searchValue && searchValue.trim() !== "";
  const hasActive = activeFilters.length > 0 || hasSearch;

  // Local state for the search input so typing is never blocked by
  // the async URL/state update that onSearchChange may trigger.
  const [localSearch, setLocalSearch] = useState(searchValue ?? "");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync local state when the external searchValue changes (e.g. "Limpiar" button)
  // Also cancel any pending debounce to avoid stale values firing after the reset.
  useEffect(() => {
    setLocalSearch(searchValue ?? "");
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
      debounceRef.current = null;
    }
  }, [searchValue]);

  const handleLocalSearchChange = useCallback(
    (value: string) => {
      setLocalSearch(value);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onSearchChange?.(value);
      }, searchDebounceMs);
    },
    [onSearchChange, searchDebounceMs]
  );

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        {onSearchChange && (
          <Input
            placeholder={searchPlaceholder}
            value={localSearch}
            onChange={(e) => handleLocalSearchChange(e.target.value)}
            className="h-9 w-full sm:w-56"
          />
        )}
        {filters.map((filter) => (
          <Select
            key={filter.key}
            value={values[filter.key] ?? ""}
            onValueChange={(value) => onChange(filter.key, value === "__all__" ? "" : value)}
          >
            <SelectTrigger className="h-9 w-full sm:w-44">
              <SelectValue placeholder={filter.label} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Todos</SelectItem>
              {filter.options.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ))}
        {hasActive && (
          <Button variant="ghost" size="sm" onClick={onClear} className="h-9 text-muted-foreground">
            <XIcon className="size-4 mr-1" />
            Limpiar
          </Button>
        )}
      </div>
      {hasActive && (
        <div className="flex flex-wrap gap-1">
          {activeFilters.map(([key, value]) => {
            const filter = filters.find((f) => f.key === key);
            const option = filter?.options.find((o) => o.value === value);
            const label = option?.label ?? value;
            return (
              <Badge
                key={key}
                variant="secondary"
                className="cursor-pointer"
                onClick={() => onChange(key, "")}
              >
                {filter?.label}: {label}
                <XIcon className="size-3 ml-1" />
              </Badge>
            );
          })}
          {hasSearch && (
            <Badge
              variant="secondary"
              className="cursor-pointer"
              onClick={() => onSearchChange?.("")}
            >
              Buscar: {searchValue}
              <XIcon className="size-3 ml-1" />
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}
