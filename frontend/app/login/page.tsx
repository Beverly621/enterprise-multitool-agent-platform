"use client";

import { LogIn } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { login } from "@/lib/api";
import { setToken } from "@/lib/auth";

const demoAccounts = [
  "admin@example.com / admin123",
  "developer@example.com / dev123",
  "user@example.com / user123",
  "guest@example.com / guest123"
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setToken(await login(email, password));
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-mist p-6">
      <form onSubmit={submit} className="w-full max-w-md space-y-5 rounded border border-slate-200 bg-white p-6">
        <div>
          <h1 className="text-xl font-semibold text-ink">Enterprise Agent Console</h1>
          <p className="mt-1 text-sm text-slate-600">Sign in</p>
        </div>
        <input
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          type="email"
        />
        <input
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          type="password"
        />
        {error && <ErrorState message={error} />}
        <button
          type="submit"
          disabled={loading}
          className="inline-flex w-full items-center justify-center gap-2 rounded bg-pine px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          <LogIn size={16} />
          {loading ? "Signing in" : "Login"}
        </button>
        <div className="rounded bg-slate-50 p-3 text-xs leading-6 text-slate-600">
          {demoAccounts.map((account) => <div key={account}>{account}</div>)}
        </div>
      </form>
    </main>
  );
}
