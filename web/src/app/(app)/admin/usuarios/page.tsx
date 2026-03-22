"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function UsuariosRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/admin?tab=usuarios");
  }, [router]);
  return null;
}
