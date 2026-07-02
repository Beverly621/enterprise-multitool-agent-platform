"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { JsonViewer } from "@/components/common/JsonViewer";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { MarkdownReportViewer } from "@/components/reports/MarkdownReportViewer";
import { apiGet, apiPost } from "@/lib/api";
import type { ReportRecord } from "@/lib/types";

export default function ReportDetailPage({ params }: { params: { reportId: string } }) {
  return <AuthGuard><ReportDetail reportId={params.reportId} /></AuthGuard>;
}

function ReportDetail({ reportId }: { reportId: string }) {
  const [report, setReport] = useState<ReportRecord | null>(null);
  const [exportResult, setExportResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<ReportRecord>(`/api/reports/${reportId}`).then(setReport).catch((err) => setError(err.message));
  }, [reportId]);
  async function exportReport() {
    setExportResult(await apiPost(`/api/reports/${reportId}/export`, {}));
  }
  if (error) return <ErrorState message={error} />;
  if (!report) return <LoadingState />;
  return (
    <div className="space-y-5">
      <section className="rounded border border-slate-200 bg-white p-5">
        <div className="flex items-center justify-between gap-4">
          <h1 className="text-xl font-semibold text-ink">{report.title}</h1>
          <StatusBadge status={report.status} />
        </div>
        <p className="mt-2 text-sm text-slate-600">{report.summary}</p>
        {report.run_id && <Link href={`/runs/${report.run_id}`} className="mt-3 inline-block text-sm text-pine">{report.run_id}</Link>}
      </section>
      <MarkdownReportViewer content={report.content_markdown} />
      <section className="rounded border border-slate-200 bg-white p-5">
        <button onClick={exportReport} className="rounded bg-pine px-4 py-2 text-sm font-medium text-white">Export</button>
        {exportResult ? <div className="mt-4"><JsonViewer value={exportResult} /></div> : null}
      </section>
      <JsonViewer value={report.source_metadata_json} />
    </div>
  );
}
