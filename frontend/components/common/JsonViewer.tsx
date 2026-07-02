"use client";

export function JsonViewer({ value }: { value: unknown }) {
  return (
    <pre className="max-h-96 overflow-auto rounded border border-slate-200 bg-slate-950 p-4 text-xs leading-5 text-slate-100">
      {JSON.stringify(value ?? {}, null, 2)}
    </pre>
  );
}
