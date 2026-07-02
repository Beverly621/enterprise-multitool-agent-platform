"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { TopNav } from "@/components/layout/TopNav";
import { currentUser } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { User } from "@/lib/types";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    currentUser()
      .then(setUser)
      .catch((err: Error) => setError(err.message));
  }, [router]);

  if (error) return <main className="p-6"><ErrorState message={error} /></main>;
  if (!user) return <main className="p-6"><LoadingState label="Checking session" /></main>;

  return (
    <div className="flex min-h-screen bg-mist">
      <AppSidebar user={user} />
      <div className="min-w-0 flex-1">
        <TopNav user={user} />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
