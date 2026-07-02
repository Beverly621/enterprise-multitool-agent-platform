"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { TraceTimeline } from "@/components/agent/TraceTimeline";
import { ErrorState } from "@/components/common/ErrorState";
import { JsonViewer } from "@/components/common/JsonViewer";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet } from "@/lib/api";
import type { ReportRecord, RunRecord, TaskProgress } from "@/lib/types";

export default function RunDetailPage({ params }: { params: { runId: string } }) {
  return <AuthGuard><RunDetail runId={params.runId} /></AuthGuard>;
}

function RunDetail({ runId }: { runId: string }) {
  const [run, setRun] = useState<RunRecord | null>(null);
  const [steps, setSteps] = useState<Array<Record<string, any>>>([]);
  const [traces, setTraces] = useState<Array<Record<string, any>>>([]);
  const [toolCalls, setToolCalls] = useState<Array<Record<string, any>>>([]);
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [report, setReport] = useState<ReportRecord | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiGet<RunRecord>(`/api/runs/${runId}`).then(setRun),
      apiGet<Array<Record<string, any>>>(`/api/runs/${runId}/steps`).then(setSteps),
      apiGet<Array<Record<string, any>>>(`/api/runs/${runId}/traces`).then(setTraces),
      apiGet<Array<Record<string, any>>>(`/api/runs/${runId}/tool-calls`).then(setToolCalls).catch(() => []),
      apiGet<TaskProgress>(`/api/runs/${runId}/progress`).then(setProgress).catch(() => null),
      apiGet<ReportRecord>(`/api/runs/${runId}/report`).then(setReport).catch(() => null)
    ]).catch((err) => setError(err.message));
  }, [runId]);

  if (error) return <ErrorState message={error} />;
  if (!run) return <LoadingState />;

  return (
    <div className="space-y-5">
      <div className="rounded border border-slate-200 bg-white p-5">
        <div className="flex items-center justify-between gap-4">
          <h1 className="font-mono text-sm font-semibold text-ink">{run.run_id}</h1>
          <StatusBadge status={run.status} />
        </div>
        <p className="mt-3 text-sm text-slate-700">{run.query}</p>
        {run.final_answer && <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink">{run.final_answer}</p>}
        {progress && <div className="mt-4"><StatusBadge status={progress.status} /> <span className="ml-2 text-sm text-slate-600">{progress.progress}%</span></div>}
        {report && <Link href={`/reports/${report.report_id}`} className="mt-4 inline-block text-sm font-medium text-pine">Open report</Link>}
      </div>
      <section className="grid gap-5 lg:grid-cols-2">
        <div><h2 className="mb-3 font-semibold text-ink">Steps</h2><TraceTimeline items={steps} /></div>
        <div><h2 className="mb-3 font-semibold text-ink">Traces</h2><TraceTimeline items={traces} /></div>
      </section>
      <section><h2 className="mb-3 font-semibold text-ink">Tool Calls</h2><JsonViewer value={toolCalls} /></section>
    </div>
  );
}
