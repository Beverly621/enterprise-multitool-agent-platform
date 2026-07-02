"use client";

import { JsonViewer } from "@/components/common/JsonViewer";

export function CitationList({ citations }: { citations?: Array<Record<string, unknown>> }) {
  if (!citations?.length) return null;
  return (
    <section className="space-y-2">
      <h3 className="text-sm font-semibold text-ink">Citations</h3>
      <div className="grid gap-2">
        {citations.map((citation, index) => (
          <JsonViewer key={index} value={citation} />
        ))}
      </div>
    </section>
  );
}
