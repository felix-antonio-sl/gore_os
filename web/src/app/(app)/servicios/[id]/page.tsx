"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ServiceDetailRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/servicios");
  }, [router]);
  return null;
}
