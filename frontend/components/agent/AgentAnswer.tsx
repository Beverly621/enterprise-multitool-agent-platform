"use client";

import { StatusBadge } from "@/components/common/StatusBadge";
import { JsonViewer } from "@/components/common/JsonViewer";
import { CitationList } from "@/components/agent/CitationList";
import type { AgentResponse } from "@/lib/types";

export function AgentAnswer({ response }: { response: AgentResponse | null }) {
  if (!response) return null;
  return (
    <div className="space-y-4 rounded border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-center gap-3">
        <StatusBadge status={response.status} />
        {response.intent && <span className="text-sm text-slate-600">{response.intent}</span>}
        <span className="font-mono text-xs text-slate-500">{response.run_id}</span>
      </div>
      {response.answer && <div className="whitespace-pre-wrap text-sm leading-6 text-ink">{response.answer}</div>}
      {response.message && <p className="text-sm text-slate-600">{response.message}</p>}
      {response.task_id && <p className="font-mono text-xs text-slate-500">{response.task_id}</p>}
      {response.approval_id && <p className="text-sm text-amber-700">Approval: {response.approval_id}</p>}
      {response.generated_sql && (
        <pre className="overflow-auto rounded bg-slate-950 p-4 text-xs text-slate-100">{response.generated_sql}</pre>
      )}
      {response.sql_result && <JsonViewer value={response.sql_result} />}
      <CitationList citations={response.citations} />
      {response.tool_results?.length ? <JsonViewer value={response.tool_results} /> : null}
    </div>
  );
}
