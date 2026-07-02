"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet } from "@/lib/api";
import { formatDate, shortId } from "@/lib/format";
import type { RunRecord } from "@/lib/types";

export default function RunsPage() {
  return <AuthGuard><RunsContent /></AuthGuard>;
}

function RunsContent() {
  const [items, setItems] = useState<RunRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<RunRecord[]>("/api/runs").then(setItems).catch((err) => setError(err.message));
  }, []);
  if (error) return <ErrorState message={error} />;
  if (!items) return <LoadingState />;
  if (!items.length) return <EmptyState />;
  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">Runs</h1>
      <div className="overflow-hidden rounded border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr><th className="px-4 py-3">Run</th><th className="px-4 py-3">Intent</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Step</th><th className="px-4 py-3">Created</th></tr>
          </thead>
          <tbody>
            {items.map((run) => (
              <tr key={run.run_id} className="border-t border-slate-100">
                <td className="px-4 py-3"><Link href={`/runs/${run.run_id}`} className="font-mono text-xs text-pine">{shortId(run.run_id)}</Link></td>
                <td className="px-4 py-3">{run.intent}</td>
                <td className="px-4 py-3"><StatusBadge status={run.status} /></td>
                <td className="px-4 py-3 text-slate-600">{run.current_step}</td>
                <td className="px-4 py-3 text-slate-600">{formatDate(run.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
