"use client";

import { useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { JsonViewer } from "@/components/common/JsonViewer";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiPost } from "@/lib/api";

const samples = [
  "哪个地区的异常订单最多？",
  "删除所有订单数据。",
  "查询 users 表里的 password_hash。",
  "SELECT * FROM demo_orders。",
  "DROP TABLE demo_orders。"
];

export default function SqlAgentPage() {
  return <AuthGuard><SqlAgentContent /></AuthGuard>;
}

function SqlAgentContent() {
  const [question, setQuestion] = useState(samples[0]);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setError(null);
    try {
      setResult(await apiPost("/api/sql-agent/query", { question }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "SQL Agent failed");
    }
  }

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">SQL Agent</h1>
      <div className="flex flex-wrap gap-2">
        {samples.map((item) => <button key={item} onClick={() => setQuestion(item)} className="rounded border border-slate-200 px-3 py-2 text-xs">{item}</button>)}
      </div>
      <section className="space-y-3 rounded border border-slate-200 bg-white p-4">
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} className="min-h-24 w-full rounded border border-slate-300 p-3 text-sm" />
        {error && <ErrorState message={error} />}
        <button type="button" onClick={run} className="rounded bg-pine px-4 py-2 text-sm font-medium text-white">Run Query</button>
      </section>
      {result ? <JsonViewer value={result} /> : null}
    </div>
  );
}
