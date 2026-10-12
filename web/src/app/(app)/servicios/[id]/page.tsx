import { redirect } from "next/navigation";

export default async function ServicePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  redirect(`/servicios?service_id=${encodeURIComponent(id)}`);
}
