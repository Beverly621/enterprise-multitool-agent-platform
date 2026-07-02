"use client";

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="rounded border border-slate-200 bg-white p-6 text-sm text-slate-600">
      {label}
    </div>
  );
}
