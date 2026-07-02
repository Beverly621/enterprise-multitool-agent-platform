"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet, apiPost } from "@/lib/api";
import { formatDate, shortId } from "@/lib/format";
import type { TaskProgress } from "@/lib/types";

export default function TasksPage() {
  return <AuthGuard><TasksContent /></AuthGuard>;
}

function TasksContent() {
  const [items, setItems] = useState<TaskProgress[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const load = () => {
    void apiGet<TaskProgress[]>("/api/tasks")
      .then(setItems)
      .catch((err) => setError(err.message));
  };
  useEffect(() => {
    load();
  }, []);

  async function cancel(taskId: string) {
    await apiPost(`/api/tasks/${taskId}/cancel`, {});
    load();
  }

  if (error) return <ErrorState message={error} />;
  if (!items) return <LoadingState />;
  if (!items.length) return <EmptyState />;
  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">Tasks</h1>
      <div className="grid gap-3">
        {items.map((task) => (
          <article key={task.task_id} className="rounded border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-mono text-xs text-slate-600">{task.task_id}</p>
                <p className="mt-1 text-sm text-ink">{task.task_type} · {task.current_stage}</p>
              </div>
              <StatusBadge status={task.status} />
            </div>
            <div className="mt-3 h-2 rounded bg-slate-100"><div className="h-2 rounded bg-pine" style={{ width: `${task.progress}%` }} /></div>
            <div className="mt-3 flex items-center justify-between text-sm text-slate-600">
              {task.run_id ? <Link href={`/runs/${task.run_id}`} className="text-pine">{shortId(task.run_id)}</Link> : <span>-</span>}
              <span>{formatDate(task.updated_at)}</span>
              <button onClick={() => cancel(task.task_id)} className="rounded border border-slate-300 px-3 py-1 text-xs">Cancel</button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
