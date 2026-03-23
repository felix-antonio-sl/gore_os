"use client";
import dynamic from "next/dynamic";

const BugReportFab = dynamic(
  () => import("@/components/bug-report-fab").then((m) => ({ default: m.BugReportFab })),
  { ssr: false }
);

export function BugReportFabLoader() {
  return <BugReportFab />;
}
