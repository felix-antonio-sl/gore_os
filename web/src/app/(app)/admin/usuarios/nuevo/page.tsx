"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function NuevoUsuarioRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/admin/usuarios");
  }, [router]);
  return null;
}
