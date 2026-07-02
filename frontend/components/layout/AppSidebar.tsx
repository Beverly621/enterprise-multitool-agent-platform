"use client";

import {
  Activity,
  ClipboardCheck,
  Database,
  FileText,
  Gauge,
  History,
  MessageSquareText,
  ScrollText,
  Settings,
  ShieldCheck,
  TerminalSquare,
  Users,
  Wrench
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { canAccess } from "@/lib/auth";
import type { User } from "@/lib/types";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge, role: "Guest" },
  { href: "/kb", label: "Knowledge Base", icon: Database, role: "Guest" },
  { href: "/agent", label: "Agent Chat", icon: MessageSquareText, role: "Guest" },
  { href: "/sql-agent", label: "SQL Agent", icon: TerminalSquare, role: "Developer" },
  { href: "/tools", label: "Tools", icon: Wrench, role: "User" },
  { href: "/approvals", label: "Approvals", icon: ClipboardCheck, role: "User" },
  { href: "/runs", label: "Runs", icon: History, role: "User" },
  { href: "/tasks", label: "Tasks", icon: Activity, role: "Developer" },
  { href: "/reports", label: "Reports", icon: FileText, role: "User" },
  { href: "/audit", label: "Audit", icon: ScrollText, role: "Developer" },
  { href: "/admin/users", label: "Admin Users", icon: Users, role: "Admin" },
  { href: "/tools", label: "Tool Admin", icon: Settings, role: "Admin" }
] as const;

export function AppSidebar({ user }: { user: User }) {
  const pathname = usePathname();
  return (
    <aside className="h-screen w-64 shrink-0 border-r border-slate-200 bg-white">
      <div className="flex h-16 items-center gap-3 border-b border-slate-200 px-5">
        <span className="grid h-9 w-9 place-items-center rounded bg-pine text-white">
          <ShieldCheck size={18} />
        </span>
        <div>
          <p className="text-sm font-semibold text-ink">Agent Platform</p>
          <p className="text-xs text-slate-500">{user.roles.join(", ") || "Guest"}</p>
        </div>
      </div>
      <nav className="space-y-1 p-3">
        {items
          .filter((item) => canAccess(user, item.role))
          .map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={`${item.href}-${item.label}`}
                href={item.href}
                className={`flex items-center gap-3 rounded px-3 py-2 text-sm ${
                  active ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon size={17} />
                {item.label}
              </Link>
            );
          })}
      </nav>
    </aside>
  );
}
