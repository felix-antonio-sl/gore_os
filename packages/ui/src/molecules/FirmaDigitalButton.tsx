import * as React from "react";
import { cn } from "../lib/utils";
import { Icons } from "../atoms/GoreIcon";

export interface FirmaDigitalButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  onSign?: () => Promise<void>;
  signerName: string;
}

export function FirmaDigitalButton({
  className,
  onSign,
  signerName,
  ...props
}: FirmaDigitalButtonProps) {
  const [status, setStatus] = React.useState<
    "idle" | "signing" | "success" | "error"
  >("idle");

  const handleSign = async () => {
    if (!onSign) return;
    setStatus("signing");
    try {
      await onSign();
      setStatus("success");
    } catch (error) {
      setStatus("error");
    }
  };

  return (
    <button
      onClick={handleSign}
      disabled={status === "signing" || status === "success"}
      className={cn(
        "relative flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
        status === "idle" && "bg-gore-brand text-white hover:bg-gore-brand/90",
        status === "signing" && "bg-gore-brand/70 text-white",
        status === "success" && "bg-gore-success text-white",
        status === "error" && "bg-gore-error text-white",
        className
      )}
      {...props}
    >
      {status === "idle" && (
        <>
          <Icons.FileText size={16} className="text-white" />
          Firmar como {signerName}
        </>
      )}
      {status === "signing" && <span>Firmando con ClaveÚnica...</span>}
      {status === "success" && (
        <>
          <Icons.CheckCircle size={16} className="text-white" />
          Firmado Digitalmente
        </>
      )}
      {status === "error" && "Error al firmar"}
    </button>
  );
}
