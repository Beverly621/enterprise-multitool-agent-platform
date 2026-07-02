"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { JsonViewer } from "@/components/common/JsonViewer";
import { LoadingState } from "@/components/common/LoadingState";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet } from "@/lib/api";
import { formatDate } from "@/lib/format";

export default function AuditPage() {
  return <AuthGuard><AuditContent /></AuthGuard>;
}

function AuditContent() {
  const [items, setItems] = useState<Array<Record<string, any>> | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<Array<Record<string, any>>>("/api/audit").then(setItems).catch((err) => setError(err.message));
  }, []);
  if (error) return <ErrorState message={error} />;
  if (!items) return <LoadingState />;
  if (!items.length) return <EmptyState />;
  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">Audit</h1>
      <div className="space-y-3">
        {items.map((item) => (
          <article key={String(item.id)} className="rounded border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-ink">{String(item.action)}</p>
                <p className="text-xs text-slate-500">{formatDate(String(item.created_at))}</p>
              </div>
              <span className="text-xs text-slate-500">{String(item.resource_type ?? "-")}</span>
            </div>
            <div className="mt-3"><JsonViewer value={item.metadata_json} /></div>
          </article>
        ))}
      </div>
    </div>
  );
}
