"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ComiteTDRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/coordinacion?tab=comite-td");
  }, [router]);
  return null;
}
