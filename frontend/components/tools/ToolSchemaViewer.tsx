"use client";

import { JsonViewer } from "@/components/common/JsonViewer";
import type { ToolRecord } from "@/lib/types";

export function ToolSchemaViewer({ tool }: { tool: ToolRecord }) {
  return (
    <section className="rounded border border-slate-200 bg-white p-5">
      <h2 className="text-base font-semibold text-ink">{tool.name}</h2>
      <p className="mt-1 text-sm text-slate-600">{tool.description}</p>
      <div className="mt-4">
        <JsonViewer value={tool.schema_json} />
      </div>
    </section>
  );
}
