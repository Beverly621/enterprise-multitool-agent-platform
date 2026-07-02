"use client";

import { Send } from "lucide-react";
import { useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { apiGet, apiPost } from "@/lib/api";
import type { AgentResponse, KnowledgeBase, TaskProgress } from "@/lib/types";

const prompts = [
  "你好，介绍一下你能做什么？",
  "员工遇到利益冲突时应该怎么处理？请给出制度依据。",
  "哪个地区的异常订单最多？",
  "查询 order_001 的订单状态。",
  "结合最近 30 天订单异常数据和售后知识库生成一份分析报告。",
  "把这份订单异常分析报告生成邮件草稿发给 manager@example.com。"
];

export function AgentChatBox({
  knowledgeBases,
  onResponse,
  onProgress
}: {
  knowledgeBases: KnowledgeBase[];
  onResponse: (response: AgentResponse) => void;
  onProgress: (progress: TaskProgress | null) => void;
}) {
  const [query, setQuery] = useState(prompts[0]);
  const [kbId, setKbId] = useState("");
  const [asyncMode, setAsyncMode] = useState(false);
  const [idempotencyKey, setIdempotencyKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError(null);
    onProgress(null);
    try {
      const response = await apiPost<AgentResponse>("/api/agent/chat", {
        query,
        kb_id: kbId ? Number(kbId) : undefined,
        async_mode: asyncMode,
        idempotency_key: idempotencyKey || undefined
      });
      onResponse(response);
      if (asyncMode && response.run_id) {
        pollProgress(response.run_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Agent request failed");
    } finally {
      setLoading(false);
    }
  }

  function pollProgress(runId: string) {
    const timer = window.setInterval(async () => {
      try {
        const progress = await apiGet<TaskProgress>(`/api/runs/${runId}/progress`);
        onProgress(progress);
        if (["SUCCESS", "FAILED", "CANCELLED", "WAITING_APPROVAL"].includes(progress.status)) {
          window.clearInterval(timer);
        }
      } catch {
        window.clearInterval(timer);
      }
    }, 2000);
  }

  return (
    <div className="space-y-4 rounded border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap gap-2">
        {prompts.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setQuery(item)}
            className="rounded border border-slate-200 px-3 py-2 text-left text-xs text-slate-700 hover:bg-slate-50"
          >
            {item}
          </button>
        ))}
      </div>
      <textarea
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        className="min-h-28 w-full rounded border border-slate-300 px-3 py-2 text-sm outline-none focus:border-pine"
      />
      <div className="grid gap-3 md:grid-cols-3">
        <select
          value={kbId}
          onChange={(event) => setKbId(event.target.value)}
          className="rounded border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">No KB selected</option>
          {knowledgeBases.map((kb) => (
            <option key={kb.id} value={kb.id}>{kb.name}</option>
          ))}
        </select>
        <input
          value={idempotencyKey}
          onChange={(event) => setIdempotencyKey(event.target.value)}
          placeholder="idempotency_key"
          className="rounded border border-slate-300 px-3 py-2 text-sm"
        />
        <label className="flex items-center gap-2 rounded border border-slate-300 px-3 py-2 text-sm">
          <input type="checkbox" checked={asyncMode} onChange={(event) => setAsyncMode(event.target.checked)} />
          Async mode
        </label>
      </div>
      {error && <ErrorState message={error} />}
      <button
        type="button"
        onClick={submit}
        disabled={loading || !query.trim()}
        className="inline-flex items-center gap-2 rounded bg-pine px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
      >
        <Send size={16} />
        {loading ? "Sending" : "Send"}
      </button>
    </div>
  );
}
