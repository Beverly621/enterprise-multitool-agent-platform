"use client";

import { useEffect, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { ReportList } from "@/components/reports/ReportList";
import { apiGet } from "@/lib/api";
import type { ReportRecord } from "@/lib/types";

export default function ReportsPage() {
  return <AuthGuard><ReportsContent /></AuthGuard>;
}

function ReportsContent() {
  const [reports, setReports] = useState<ReportRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<ReportRecord[]>("/api/reports").then(setReports).catch((err) => setError(err.message));
  }, []);
  if (error) return <ErrorState message={error} />;
  if (!reports) return <LoadingState />;
  return <div className="space-y-5"><h1 className="text-xl font-semibold text-ink">Reports</h1><ReportList reports={reports} /></div>;
}
