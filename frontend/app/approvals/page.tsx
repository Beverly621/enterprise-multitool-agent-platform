"use client";

import { Check, X } from "lucide-react";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet, apiPost } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { ApprovalRecord } from "@/lib/types";

export default function ApprovalsPage() {
  return <AuthGuard><ApprovalsContent /></AuthGuard>;
}

function ApprovalsContent() {
  const [items, setItems] = useState<ApprovalRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const load = () => {
    void apiGet<ApprovalRecord[]>("/api/approvals")
      .then(setItems)
      .catch((err) => setError(err.message));
  };
  useEffect(() => {
    load();
  }, []);

  async function decide(id: string, action: "approve" | "reject") {
    await apiPost(`/api/approvals/${id}/${action}`, { comment: action });
    load();
  }

  if (error) return <ErrorState message={error} />;
  if (!items) return <LoadingState />;

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">Approvals</h1>
      {!items.length ? <EmptyState /> : (
        <div className="overflow-hidden rounded border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr><th className="px-4 py-3">Approval</th><th className="px-4 py-3">Tool</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Created</th><th className="px-4 py-3">Actions</th></tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.approval_id} className="border-t border-slate-100">
                  <td className="px-4 py-3 font-mono text-xs">{item.approval_id}</td>
                  <td className="px-4 py-3">{item.tool_name}</td>
                  <td className="px-4 py-3"><StatusBadge status={item.status} /></td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(item.created_at)}</td>
                  <td className="flex gap-2 px-4 py-3">
                    <button title="Approve" onClick={() => decide(item.approval_id, "approve")} className="rounded border border-emerald-200 p-2 text-emerald-700"><Check size={16} /></button>
                    <button title="Reject" onClick={() => decide(item.approval_id, "reject")} className="rounded border border-rose-200 p-2 text-rose-700"><X size={16} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
