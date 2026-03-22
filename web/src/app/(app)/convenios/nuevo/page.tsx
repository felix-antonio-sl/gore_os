"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function NuevoConvenioRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/convenios");
  }, [router]);
  return null;
}
