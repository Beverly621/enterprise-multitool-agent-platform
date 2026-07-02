"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { apiGet } from "@/lib/api";
import type { User } from "@/lib/types";

export default function AdminUsersPage() {
  return <AuthGuard><UsersContent /></AuthGuard>;
}

function UsersContent() {
  const [users, setUsers] = useState<User[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<User[]>("/api/users").then(setUsers).catch((err) => setError(err.message));
  }, []);
  if (error) return <ErrorState message={error} />;
  if (!users) return <LoadingState />;
  if (!users.length) return <EmptyState />;
  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-ink">Admin Users</h1>
      <div className="overflow-hidden rounded border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr><th className="px-4 py-3">Email</th><th className="px-4 py-3">Roles</th><th className="px-4 py-3">Status</th></tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t border-slate-100">
                <td className="px-4 py-3 font-medium text-ink">{user.email}</td>
                <td className="px-4 py-3">{user.roles.map((role) => <StatusBadge key={role} status={role} />)}</td>
                <td className="px-4 py-3"><StatusBadge status={user.is_active ? "ACTIVE" : "DISABLED"} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
