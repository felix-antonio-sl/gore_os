import * as React from "react";
import { cn } from "../lib/utils";
import { formatCurrency } from "../lib/formatters";

export interface CurrencyInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  onValueChange?: (value: number) => void;
  label?: string;
}

export const CurrencyInput = React.forwardRef<
  HTMLInputElement,
  CurrencyInputProps
>(({ className, onValueChange, label, ...props }, ref) => {
  const [displayValue, setDisplayValue] = React.useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Remove non-numeric chars
    const rawValue = e.target.value.replace(/\D/g, "");
    if (!rawValue) {
      setDisplayValue("");
      onValueChange?.(0);
      return;
    }

    const numberValue = parseInt(rawValue, 10);
    setDisplayValue(formatCurrency(numberValue)); // Formats as "$ 1.000"
    onValueChange?.(numberValue);
  };

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium leading-none text-gore-text">
          {label}
        </label>
      )}
      <input
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        value={displayValue}
        onChange={handleChange}
        placeholder="$ 0"
        {...props}
      />
    </div>
  );
});
CurrencyInput.displayName = "CurrencyInput";
