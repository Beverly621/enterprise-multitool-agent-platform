"use client";

import { Plus } from "lucide-react";
import { useEffect, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { KnowledgeBaseList } from "@/components/kb/KnowledgeBaseList";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet, apiPost } from "@/lib/api";
import type { KnowledgeBase } from "@/lib/types";

export default function KnowledgeBasePage() {
  return <AuthGuard><KnowledgeBaseContent /></AuthGuard>;
}

function KnowledgeBaseContent() {
  const [items, setItems] = useState<KnowledgeBase[] | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    void apiGet<KnowledgeBase[]>("/api/kb")
      .then(setItems)
      .catch((err) => setError(err.message));
  };
  useEffect(() => {
    load();
  }, []);

  async function createKb() {
    await apiPost("/api/kb", { name, description, visibility: "private" });
    setName("");
    setDescription("");
    load();
  }

  if (error) return <ErrorState message={error} />;
  if (!items) return <LoadingState />;

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">Knowledge Base</h1>
      <section className="grid gap-3 rounded border border-slate-200 bg-white p-4 md:grid-cols-[1fr_2fr_auto]">
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="name" className="rounded border border-slate-300 px-3 py-2 text-sm" />
        <input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="description" className="rounded border border-slate-300 px-3 py-2 text-sm" />
        <button type="button" onClick={createKb} disabled={!name.trim()} className="inline-flex items-center gap-2 rounded bg-pine px-4 py-2 text-sm font-medium text-white disabled:opacity-60">
          <Plus size={16} />
          Create
        </button>
      </section>
      <KnowledgeBaseList items={items} />
    </div>
  );
}
