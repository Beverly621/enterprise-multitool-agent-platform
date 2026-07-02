"use client";

import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/format";
import type { DocumentRecord } from "@/lib/types";

export function DocumentStatusTable({ documents }: { documents: DocumentRecord[] }) {
  if (!documents.length) return <EmptyState label="No documents" />;
  return (
    <div className="overflow-hidden rounded border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">File</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Chunks</th>
            <th className="px-4 py-3">Updated</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((document) => (
            <tr key={document.id} className="border-t border-slate-100">
              <td className="px-4 py-3 font-medium text-ink">{document.filename}</td>
              <td className="px-4 py-3 text-slate-600">{document.file_type}</td>
              <td className="px-4 py-3"><StatusBadge status={document.status} /></td>
              <td className="px-4 py-3 text-slate-600">{document.chunk_count}</td>
              <td className="px-4 py-3 text-slate-600">{formatDate(document.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
