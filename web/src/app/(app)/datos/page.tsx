import { redirect } from "next/navigation";

export default async function LegacyDataPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  if (params.dominio !== "rendiciones") redirect("/dashboard");
  const query = new URLSearchParams();
  for (const key of ["id", "state", "search", "page"]) if (typeof params[key] === "string") query.set(key, params[key]);
  redirect(`/rendiciones${query.size ? `?${query}` : ""}`);
}
