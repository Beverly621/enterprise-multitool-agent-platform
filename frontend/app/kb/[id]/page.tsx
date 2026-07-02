"use client";

import { useCallback, useEffect, useState } from "react";

import { AgentAnswer } from "@/components/agent/AgentAnswer";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { JsonViewer } from "@/components/common/JsonViewer";
import { DocumentStatusTable } from "@/components/kb/DocumentStatusTable";
import { DocumentUploader } from "@/components/kb/DocumentUploader";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet, apiPost } from "@/lib/api";
import type { AgentResponse, KnowledgeBase } from "@/lib/types";

export default function KnowledgeBaseDetailPage({ params }: { params: { id: string } }) {
  return <AuthGuard><KbDetail id={params.id} /></AuthGuard>;
}

function KbDetail({ id }: { id: string }) {
  const [kb, setKb] = useState<KnowledgeBase | null>(null);
  const [query, setQuery] = useState("员工遇到利益冲突时应该怎么处理？");
  const [searchResult, setSearchResult] = useState<unknown>(null);
  const [answer, setAnswer] = useState<AgentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    void apiGet<KnowledgeBase>(`/api/kb/${id}`)
      .then(setKb)
      .catch((err) => setError(err.message));
  }, [id]);
  useEffect(() => {
    load();
  }, [load]);

  async function search() {
    setSearchResult(await apiPost(`/api/kb/${id}/search`, { query, top_k: 5 }));
  }

  async function rag() {
    setAnswer(await apiPost<AgentResponse>("/api/agent/chat", { query, kb_id: Number(id) }));
  }

  if (error) return <ErrorState message={error} />;
  if (!kb) return <LoadingState />;

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">{kb.name}</h1>
      <DocumentUploader kbId={Number(id)} onUploaded={load} />
      <DocumentStatusTable documents={kb.documents ?? []} />
      <section className="space-y-3 rounded border border-slate-200 bg-white p-4">
        <input value={query} onChange={(event) => setQuery(event.target.value)} className="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
        <div className="flex gap-2">
          <button type="button" onClick={search} className="rounded border border-slate-300 px-4 py-2 text-sm">Search</button>
          <button type="button" onClick={rag} className="rounded bg-pine px-4 py-2 text-sm font-medium text-white">RAG Chat</button>
        </div>
        {searchResult ? <JsonViewer value={searchResult} /> : null}
      </section>
      <AgentAnswer response={answer} />
    </div>
  );
}
