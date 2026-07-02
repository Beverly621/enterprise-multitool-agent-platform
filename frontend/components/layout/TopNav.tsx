"use client";

import { LogOut, Shield } from "lucide-react";
import { useRouter } from "next/navigation";

import { clearToken } from "@/lib/auth";
import type { User } from "@/lib/types";

export function TopNav({ user }: { user: User }) {
  const router = useRouter();
  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-5">
      <div>
        <p className="text-sm font-semibold text-ink">
          {process.env.NEXT_PUBLIC_APP_NAME ?? "Enterprise Multi-Tool Agent Platform"}
        </p>
        <p className="text-xs text-slate-500">Agent Runtime Console</p>
      </div>
      <div className="flex items-center gap-3">
        <span className="inline-flex items-center gap-2 rounded border border-slate-200 px-3 py-2 text-sm text-slate-700">
          <Shield size={16} />
          {user.email}
        </span>
        <button
          type="button"
          className="rounded border border-slate-200 p-2 text-slate-600 hover:bg-slate-50"
          title="Logout"
          onClick={() => {
            clearToken();
            router.push("/login");
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
