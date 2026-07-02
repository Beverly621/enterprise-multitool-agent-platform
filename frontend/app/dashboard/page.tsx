"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet } from "@/lib/api";
import { formatDate, shortId } from "@/lib/format";
import type { DashboardSummary } from "@/lib/types";

const cards: Array<[keyof DashboardSummary, string]> = [
  ["knowledge_bases", "Knowledge Bases"],
  ["documents", "Documents"],
  ["agent_runs", "Agent Runs"],
  ["tasks", "Tasks"],
  ["reports", "Reports"],
  ["tool_calls", "Tool Calls"],
  ["pending_approvals", "Pending Approvals"],
  ["failed_tasks", "Failed Tasks"]
];

export default function DashboardPage() {
  return <AuthGuard><DashboardContent /></AuthGuard>;
}

function DashboardContent() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<DashboardSummary>("/api/dashboard/summary").then(setSummary).catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!summary) return <LoadingState />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-ink">Dashboard</h1>
      <section className="grid gap-4 md:grid-cols-4">
        {cards.map(([key, label]) => (
          <article key={key} className="rounded border border-slate-200 bg-white p-4">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-ink">{String(summary[key] ?? 0)}</p>
          </article>
        ))}
      </section>
      <section className="grid gap-4 lg:grid-cols-2">
        <Recent title="Recent Runs" items={summary.recent_runs} idKey="run_id" />
        <Recent title="Recent Reports" items={summary.recent_reports} idKey="report_id" />
      </section>
    </div>
  );
}

function Recent({ title, items, idKey }: { title: string; items: any[]; idKey: string }) {
  return (
    <section className="rounded border border-slate-200 bg-white p-4">
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      {!items?.length ? <div className="mt-3"><EmptyState /></div> : (
        <div className="mt-3 space-y-2">
          {items.map((item, index) => (
            <div key={index} className="flex items-center justify-between gap-4 rounded border border-slate-100 p-3 text-sm">
              <span className="font-mono text-xs text-slate-600">{shortId(item[idKey])}</span>
              <StatusBadge status={item.status} />
              <span className="text-xs text-slate-500">{formatDate(item.created_at)}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
