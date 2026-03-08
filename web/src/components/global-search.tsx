"use client";

import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { api } from "@/lib/api";
import type { SearchResult } from "@/types";
import { FileText, AlertCircle, ClipboardList, User } from "lucide-react";

interface SearchResponse {
  results: SearchResult[];
}

const ENTITY_ICONS: Record<string, React.ReactNode> = {
  ipr: <FileText className="size-3.5 shrink-0 text-blue-500" />,
  compromiso: <ClipboardList className="size-3.5 shrink-0 text-green-500" />,
  problema: <AlertCircle className="size-3.5 shrink-0 text-orange-500" />,
  persona: <User className="size-3.5 shrink-0 text-purple-500" />,
};

const ENTITY_LABELS: Record<string, string> = {
  ipr: "IPR",
  compromiso: "Compromisos",
  problema: "Problemas",
  persona: "Personas",
};

const ENTITY_ROUTES: Record<string, (id: string) => string> = {
  ipr: (id) => `/ipr/${id}`,
  compromiso: (id) => `/compromisos?id=${id}`,
  problema: (id) => `/problemas?id=${id}`,
  persona: () => `/datos?dominio=personas`,
};

interface GlobalSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GlobalSearch({ open, onOpenChange }: GlobalSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const router = useRouter();

  // Keyboard shortcut ⌘K / Ctrl+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        onOpenChange(!open);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open, onOpenChange]);

  // Limpiar resultados al cerrar
  useEffect(() => {
    if (!open) {
      setQuery("");
      setResults([]);
    }
  }, [open]);

  // Debounce search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (query.length < 2) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const data = await api.get<SearchResponse>(
          `/api/search?q=${encodeURIComponent(query)}&limit=5`
        );
        setResults(data.results);
      } catch {
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  // Agrupar resultados por entity_type
  const grouped = results.reduce<Record<string, SearchResult[]>>((acc, r) => {
    if (!acc[r.entity_type]) acc[r.entity_type] = [];
    acc[r.entity_type].push(r);
    return acc;
  }, {});

  const handleSelect = (result: SearchResult) => {
    const routeFn = ENTITY_ROUTES[result.entity_type];
    if (routeFn) {
      router.push(routeFn(result.id));
    }
    onOpenChange(false);
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange} shouldFilter={false}>
      <CommandInput
        placeholder="Buscar IPR, compromisos, problemas, personas..."
        value={query}
        onValueChange={setQuery}
      />
      <CommandList>
        {isLoading && (
          <CommandEmpty>Buscando...</CommandEmpty>
        )}
        {!isLoading && query.length >= 2 && results.length === 0 && (
          <CommandEmpty>Sin resultados para &ldquo;{query}&rdquo;</CommandEmpty>
        )}
        {!isLoading && query.length < 2 && (
          <CommandEmpty className="text-xs text-muted-foreground py-6">
            Escribe al menos 2 caracteres para buscar
          </CommandEmpty>
        )}
        {Object.entries(grouped).map(([entityType, items]) => (
          <CommandGroup
            key={entityType}
            heading={ENTITY_LABELS[entityType] ?? entityType}
          >
            {items.map((item) => (
              <CommandItem
                key={`${item.entity_type}-${item.id}`}
                value={`${item.entity_type}-${item.id}-${item.name}`}
                onSelect={() => handleSelect(item)}
                className="flex items-center gap-2"
              >
                {ENTITY_ICONS[item.entity_type]}
                <span className="flex-1 truncate">{item.name}</span>
                {item.code && (
                  <span className="text-[10px] text-muted-foreground">
                    {item.code}
                  </span>
                )}
              </CommandItem>
            ))}
          </CommandGroup>
        ))}
      </CommandList>
    </CommandDialog>
  );
}
