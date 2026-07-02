"use client";

import { Upload } from "lucide-react";
import { useState } from "react";

import { apiPost } from "@/lib/api";

export function DocumentUploader({ kbId, onUploaded }: { kbId: number; onUploaded: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  async function upload() {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    setLoading(true);
    try {
      await apiPost(`/api/kb/${kbId}/documents`, form);
      setFile(null);
      onUploaded();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-3 rounded border border-slate-200 bg-white p-4">
      <input
        type="file"
        accept=".pdf,.docx,.md,.markdown,.txt,.csv"
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        className="text-sm"
      />
      <button
        type="button"
        onClick={upload}
        disabled={!file || loading}
        className="inline-flex items-center gap-2 rounded bg-pine px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
      >
        <Upload size={16} />
        {loading ? "Uploading" : "Upload"}
      </button>
    </div>
  );
}
