"use client";

export function MarkdownReportViewer({ content }: { content: string }) {
  return (
    <article className="prose prose-slate max-w-none rounded border border-slate-200 bg-white p-6">
      <pre className="whitespace-pre-wrap font-sans text-sm leading-7 text-ink">{content}</pre>
    </article>
  );
}
