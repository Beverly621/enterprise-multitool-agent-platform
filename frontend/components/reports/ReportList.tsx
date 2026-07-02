"use client";

import Link from "next/link";

import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate, shortId } from "@/lib/format";
import type { ReportRecord } from "@/lib/types";

export function ReportList({ reports }: { reports: ReportRecord[] }) {
  if (!reports.length) return <EmptyState label="No reports" />;
  return (
    <div className="overflow-hidden rounded border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">Title</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Run</th>
            <th className="px-4 py-3">Created</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report) => (
            <tr key={report.report_id} className="border-t border-slate-100">
              <td className="px-4 py-3">
                <Link href={`/reports/${report.report_id}`} className="font-medium text-pine">{report.title}</Link>
              </td>
              <td className="px-4 py-3 text-slate-600">{report.report_type}</td>
              <td className="px-4 py-3"><StatusBadge status={report.status} /></td>
              <td className="px-4 py-3 font-mono text-xs text-slate-600">{shortId(report.run_id)}</td>
              <td className="px-4 py-3 text-slate-600">{formatDate(report.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
