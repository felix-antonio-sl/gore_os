import * as React from "react";
import { cn } from "../lib/utils";
import { formatRut, validateRut } from "../lib/formatters";

export interface RutInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  onRutChange?: (rut: string, isValid: boolean) => void;
  label?: string;
  error?: string;
}

export const RutInput = React.forwardRef<HTMLInputElement, RutInputProps>(
  ({ className, onRutChange, label, error, ...props }, ref) => {
    const [value, setValue] = React.useState("");
    const [isValid, setIsValid] = React.useState(true);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const formatted = formatRut(e.target.value);
      setValue(formatted);
      const valid = validateRut(formatted);
      setIsValid(valid);
      if (onRutChange) {
        onRutChange(formatted, valid);
      }
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
            !isValid && "border-gore-error focus-visible:ring-gore-error",
            className
          )}
          ref={ref}
          value={value}
          onChange={handleChange}
          placeholder="12.345.678-9"
          maxLength={12}
          {...props}
        />
        {error && <span className="text-xs text-gore-error">{error}</span>}
        {!isValid && value.length > 8 && (
          <span className="text-xs text-gore-error">RUT inválido</span>
        )}
      </div>
    );
  }
);
RutInput.displayName = "RutInput";
