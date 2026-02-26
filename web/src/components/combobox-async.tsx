"use client";

import * as React from "react";
import { ChevronsUpDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
} from "@/components/ui/command";

export interface ComboboxOption {
  value: string;
  label: string;
}

interface ComboboxAsyncProps {
  value: string;
  onChange: (value: string) => void;
  searchFn: (query: string) => Promise<ComboboxOption[]>;
  placeholder?: string;
  displayLabel?: string;
  className?: string;
}

export function ComboboxAsync({
  value,
  onChange,
  searchFn,
  placeholder = "Seleccione...",
  displayLabel,
  className,
}: ComboboxAsyncProps) {
  const [open, setOpen] = React.useState(false);
  const [query, setQuery] = React.useState("");
  const [options, setOptions] = React.useState<ComboboxOption[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [selectedLabel, setSelectedLabel] = React.useState(displayLabel ?? "");

  // Keep selectedLabel in sync if displayLabel prop changes externally
  React.useEffect(() => {
    if (displayLabel !== undefined) setSelectedLabel(displayLabel);
  }, [displayLabel]);

  // Debounced search
  React.useEffect(() => {
    if (!open) return;

    if (!query || query.length < 2) {
      setOptions([]);
      return;
    }

    setLoading(true);
    const timer = setTimeout(() => {
      searchFn(query)
        .then(setOptions)
        .catch(() => setOptions([]))
        .finally(() => setLoading(false));
    }, 300);

    return () => clearTimeout(timer);
  }, [query, open, searchFn]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "w-full justify-between font-normal",
            !value && "text-muted-foreground",
            className,
          )}
        >
          <span className="truncate">
            {value ? selectedLabel || placeholder : placeholder}
          </span>
          <ChevronsUpDown className="ml-2 size-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Escribe para buscar..."
            value={query}
            onValueChange={setQuery}
          />
          <CommandList>
            {loading && (
              <div className="py-4 text-center text-sm text-muted-foreground">
                Buscando...
              </div>
            )}
            {!loading && query.length >= 2 && options.length === 0 && (
              <CommandEmpty>Sin resultados.</CommandEmpty>
            )}
            {!loading && query.length < 2 && (
              <div className="py-4 text-center text-sm text-muted-foreground">
                Escribe al menos 2 caracteres...
              </div>
            )}
            {options.length > 0 && (
              <CommandGroup>
                {options.map((opt) => (
                  <CommandItem
                    key={opt.value}
                    value={opt.value}
                    onSelect={() => {
                      onChange(opt.value);
                      setSelectedLabel(opt.label);
                      setOpen(false);
                      setQuery("");
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 size-4",
                        value === opt.value ? "opacity-100" : "opacity-0",
                      )}
                    />
                    <span className="truncate">{opt.label}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
