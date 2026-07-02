"use client";

import { JsonViewer } from "@/components/common/JsonViewer";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/format";

export function TraceTimeline({ items }: { items: Array<Record<string, any>> }) {
  return (
    <div className="space-y-3">
      {items.map((item, index) => (
        <div key={`${item.id ?? index}`} className="rounded border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-ink">{item.event_name ?? item.step_name}</p>
              <p className="text-xs text-slate-500">{formatDate(item.created_at ?? item.started_at)}</p>
            </div>
            <StatusBadge status={item.status ?? item.event_type} />
          </div>
          {(item.metadata_json || item.output_json || item.input_json) && (
            <div className="mt-3">
              <JsonViewer value={item.metadata_json ?? item.output_json ?? item.input_json} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
