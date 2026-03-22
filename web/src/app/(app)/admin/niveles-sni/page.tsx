"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function NivelesSniRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/admin?tab=configuracion");
  }, [router]);
  return null;
}
