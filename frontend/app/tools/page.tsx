"use client";

import { useEffect, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { ToolList } from "@/components/tools/ToolList";
import { apiGet } from "@/lib/api";
import type { ToolRecord } from "@/lib/types";

export default function ToolsPage() {
  return <AuthGuard><ToolsContent /></AuthGuard>;
}

function ToolsContent() {
  const [tools, setTools] = useState<ToolRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<ToolRecord[]>("/api/tools").then(setTools).catch((err) => setError(err.message));
  }, []);
  if (error) return <ErrorState message={error} />;
  if (!tools) return <LoadingState />;
  return <div className="space-y-5"><h1 className="text-xl font-semibold text-ink">Tools</h1><ToolList tools={tools} /></div>;
}
