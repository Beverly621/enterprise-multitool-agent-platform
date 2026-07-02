"use client";

export function EmptyState({ label = "No data" }: { label?: string }) {
  return (
    <div className="rounded border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
      {label}
    </div>
  );
}
