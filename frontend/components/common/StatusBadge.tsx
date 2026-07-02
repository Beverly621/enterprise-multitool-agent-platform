"use client";

const toneMap: Record<string, string> = {
  SUCCESS: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  READY: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  RUNNING: "bg-sky-50 text-sky-700 ring-sky-200",
  PENDING: "bg-amber-50 text-amber-700 ring-amber-200",
  WAITING_APPROVAL: "bg-amber-50 text-amber-700 ring-amber-200",
  FAILED: "bg-rose-50 text-rose-700 ring-rose-200",
  CANCELLED: "bg-slate-100 text-slate-700 ring-slate-200",
  TIMEOUT: "bg-rose-50 text-rose-700 ring-rose-200"
};

export function StatusBadge({ status }: { status?: string | null }) {
  const label = status ?? "UNKNOWN";
  const tone = toneMap[label.toUpperCase()] ?? "bg-slate-100 text-slate-700 ring-slate-200";
  return (
    <span className={`inline-flex items-center rounded px-2 py-1 text-xs font-medium ring-1 ${tone}`}>
      {label}
    </span>
  );
}
