import { Activity, Database, LockKeyhole, Workflow } from "lucide-react";

const modules = [
  { name: "RAG Knowledge Base", status: "Phase 2", icon: Database },
  { name: "SQL Agent Guardrails", status: "Phase 3", icon: LockKeyhole },
  { name: "Tool Calling", status: "Phase 4", icon: Workflow },
  { name: "Tracing", status: "Phase 1 schema ready", icon: Activity }
];

async function getVersion() {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8100";
  try {
    const response = await fetch(`${baseUrl}/api/version`, { cache: "no-store" });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export default async function Home() {
  const version = await getVersion();

  return (
    <main className="min-h-screen">
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <h1 className="text-xl font-semibold tracking-normal text-ink">
              Enterprise Multi-Tool Agent Platform
            </h1>
            <p className="mt-1 text-sm text-slate-600">Backend foundation, RBAC and provider switching are online.</p>
          </div>
          <a
            href="http://localhost:8100/docs"
            className="rounded-md bg-pine px-4 py-2 text-sm font-medium text-white"
          >
            Swagger
          </a>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-5 px-6 py-8 md:grid-cols-[1fr_320px]">
        <div className="grid gap-4 sm:grid-cols-2">
          {modules.map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.name} className="rounded-lg border border-slate-200 bg-white p-5">
                <div className="flex items-center gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-md bg-slate-100 text-pine">
                    <Icon size={20} />
                  </span>
                  <div>
                    <h2 className="text-base font-semibold text-ink">{item.name}</h2>
                    <p className="text-sm text-slate-600">{item.status}</p>
                  </div>
                </div>
              </article>
            );
          })}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-base font-semibold text-ink">Runtime</h2>
          <dl className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-600">Backend</dt>
              <dd className="font-medium text-ink">{version ? "reachable" : "offline"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-600">LLM</dt>
              <dd className="font-medium text-ink">{version?.data?.llm_provider ?? "unknown"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-600">Embedding</dt>
              <dd className="font-medium text-ink">{version?.data?.embedding_provider ?? "unknown"}</dd>
            </div>
          </dl>
        </aside>
      </section>
    </main>
  );
}
