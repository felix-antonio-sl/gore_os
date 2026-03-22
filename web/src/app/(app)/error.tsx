"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    console.error("[ErrorBoundary]", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center gap-2 py-12 text-muted-foreground">
      <AlertTriangle className="size-10 stroke-1 text-destructive" />
      <p className="text-sm font-medium">Ha ocurrido un error inesperado</p>
      <p className="text-xs">
        Si el problema persiste, contacte al administrador del sistema.
      </p>
      <div className="mt-2 flex gap-2">
        <Button variant="outline" onClick={() => router.push("/dashboard")}>
          Volver al inicio
        </Button>
        <Button variant="outline" onClick={() => reset()}>
          Reintentar
        </Button>
      </div>
    </div>
  );
}
