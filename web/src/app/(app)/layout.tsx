import { AppShell } from "@/components/app-shell";
import { BugReportFabLoader } from "@/components/bug-report-fab-loader";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <AppShell>{children}</AppShell>
      <BugReportFabLoader />
    </>
  );
}
