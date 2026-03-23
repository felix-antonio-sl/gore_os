import { AppShell } from "@/components/app-shell";
import { BugReportFab } from "@/components/bug-report-fab";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <AppShell>{children}</AppShell>
      <BugReportFab />
    </>
  );
}
