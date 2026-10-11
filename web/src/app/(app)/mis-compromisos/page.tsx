import { redirect } from "next/navigation";

export default function MisCompromisosPage() {
  redirect("/compromisos?mine=true");
}
