"use client";

import { useEffect, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { ToolInvokePanel } from "@/components/tools/ToolInvokePanel";
import { ToolSchemaViewer } from "@/components/tools/ToolSchemaViewer";
import { apiGet } from "@/lib/api";
import type { ToolRecord } from "@/lib/types";

export default function ToolDetailPage({ params }: { params: { toolName: string } }) {
  return <AuthGuard><ToolDetail toolName={decodeURIComponent(params.toolName)} /></AuthGuard>;
}

function ToolDetail({ toolName }: { toolName: string }) {
  const [tool, setTool] = useState<ToolRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<ToolRecord>(`/api/tools/${toolName}`).then(setTool).catch((err) => setError(err.message));
  }, [toolName]);
  if (error) return <ErrorState message={error} />;
  if (!tool) return <LoadingState />;
  return <div className="space-y-5"><ToolSchemaViewer tool={tool} /><ToolInvokePanel toolName={tool.name} /></div>;
}
