import { redirect } from "next/navigation";

/**
 * /mi-division has been absorbed into the dashboard's ModuleMyTeam.
 * Redirect any bookmarked URLs to the dashboard.
 */
export default function MiDivisionPage() {
  redirect("/dashboard");
}
