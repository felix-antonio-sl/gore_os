"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DivisionesRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/coordinacion?tab=divisiones");
  }, [router]);
  return null;
}
