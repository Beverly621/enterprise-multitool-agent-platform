"use client";

import Link from "next/link";

import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/format";
import type { KnowledgeBase } from "@/lib/types";

export function KnowledgeBaseList({ items }: { items: KnowledgeBase[] }) {
  if (!items.length) return <EmptyState label="No knowledge bases" />;
  return (
    <div className="overflow-hidden rounded border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Visibility</th>
            <th className="px-4 py-3">Updated</th>
          </tr>
        </thead>
        <tbody>
          {items.map((kb) => (
            <tr key={kb.id} className="border-t border-slate-100">
              <td className="px-4 py-3">
                <Link href={`/kb/${kb.id}`} className="font-medium text-pine">{kb.name}</Link>
              </td>
              <td className="px-4 py-3"><StatusBadge status={kb.visibility} /></td>
              <td className="px-4 py-3 text-slate-600">{formatDate(kb.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
