"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SaludDatosRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/admin?tab=monitoreo");
  }, [router]);
  return null;
}
