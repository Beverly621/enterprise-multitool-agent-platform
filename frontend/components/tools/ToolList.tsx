"use client";

import Link from "next/link";

import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import type { ToolRecord } from "@/lib/types";

export function ToolList({ tools }: { tools: ToolRecord[] }) {
  if (!tools.length) return <EmptyState label="No tools" />;
  return (
    <div className="grid gap-3">
      {tools.map((tool) => (
        <Link key={tool.name} href={`/tools/${tool.name}`} className="rounded border border-slate-200 bg-white p-4 hover:border-pine">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="font-medium text-ink">{tool.name}</p>
              <p className="mt-1 text-sm text-slate-600">{tool.description}</p>
            </div>
            <div className="flex gap-2">
              <StatusBadge status={tool.enabled === false ? "DISABLED" : "ENABLED"} />
              <StatusBadge status={tool.permission_level} />
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
