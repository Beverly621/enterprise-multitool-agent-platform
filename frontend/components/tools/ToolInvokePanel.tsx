"use client";

import { Play } from "lucide-react";
import { useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { JsonViewer } from "@/components/common/JsonViewer";
import { apiPost } from "@/lib/api";

export function ToolInvokePanel({ toolName }: { toolName: string }) {
  const [args, setArgs] = useState("{}");
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  async function invoke() {
    setError(null);
    try {
      const parsed = JSON.parse(args || "{}");
      setResult(await apiPost(`/api/tools/${toolName}/invoke`, { args: parsed }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tool invocation failed");
    }
  }

  return (
    <section className="space-y-3 rounded border border-slate-200 bg-white p-5">
      <textarea
        value={args}
        onChange={(event) => setArgs(event.target.value)}
        className="min-h-32 w-full rounded border border-slate-300 p-3 font-mono text-xs"
      />
      {error && <ErrorState message={error} />}
      <button type="button" onClick={invoke} className="inline-flex items-center gap-2 rounded bg-pine px-4 py-2 text-sm font-medium text-white">
        <Play size={16} />
        Invoke
      </button>
      {result ? <JsonViewer value={result} /> : null}
    </section>
  );
}
