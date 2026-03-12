"use client";

import { useCallback } from "react";
import { useSearchParams, usePathname, useRouter } from "next/navigation";

/**
 * Syncs a Radix Tabs value with a URL search param.
 * Enables bookmarkable/shareable tab state (e.g. /ipr/abc?tab=convenios).
 */
export function useTabParam(
  paramName = "tab",
  defaultValue = ""
): [string, (value: string) => void] {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const currentValue = searchParams.get(paramName) ?? defaultValue;

  const setValue = useCallback(
    (value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value === defaultValue) {
        params.delete(paramName);
      } else {
        params.set(paramName, value);
      }
      const qs = params.toString();
      router.replace(pathname + (qs ? "?" + qs : ""), { scroll: false });
    },
    [searchParams, pathname, router, paramName, defaultValue]
  );

  return [currentValue, setValue];
}
