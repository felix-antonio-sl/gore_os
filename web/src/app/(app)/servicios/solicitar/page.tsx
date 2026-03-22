"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SolicitarServicioRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/servicios");
  }, [router]);
  return null;
}
