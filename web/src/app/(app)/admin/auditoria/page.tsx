"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AuditoriaRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/admin?tab=auditoria");
  }, [router]);
  return null;
}
