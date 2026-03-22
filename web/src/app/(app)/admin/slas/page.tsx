"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SlasRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/admin?tab=monitoreo");
  }, [router]);
  return null;
}
