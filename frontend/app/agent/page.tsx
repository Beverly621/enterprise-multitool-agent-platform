"use client";

import { useEffect, useState } from "react";

import { AgentAnswer } from "@/components/agent/AgentAnswer";
import { AgentChatBox } from "@/components/agent/AgentChatBox";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet } from "@/lib/api";
import type { AgentResponse, KnowledgeBase, TaskProgress } from "@/lib/types";

export default function AgentPage() {
  return <AuthGuard><AgentContent /></AuthGuard>;
}

function AgentContent() {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [progress, setProgress] = useState<TaskProgress | null>(null);

  useEffect(() => {
    apiGet<KnowledgeBase[]>("/api/kb").then(setKbs).catch(() => setKbs([]));
  }, []);

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">Agent Chat</h1>
      <AgentChatBox knowledgeBases={kbs} onResponse={setResponse} onProgress={setProgress} />
      {progress && (
        <section className="rounded border border-slate-200 bg-white p-4">
          <div className="mb-2 flex items-center justify-between">
            <StatusBadge status={progress.status} />
            <span className="text-sm text-slate-600">{progress.progress}%</span>
          </div>
          <div className="h-2 rounded bg-slate-100">
            <div className="h-2 rounded bg-pine" style={{ width: `${progress.progress}%` }} />
          </div>
        </section>
      )}
      <AgentAnswer response={response} />
    </div>
  );
}
