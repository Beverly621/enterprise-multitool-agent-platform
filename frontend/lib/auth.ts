import type { User } from "@/lib/types";

const TOKEN_KEY = "emtap_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function hasRole(user: User | null, roles: string[]): boolean {
  if (!user) return false;
  return roles.some((role) => user.roles.includes(role));
}

export function canAccess(user: User | null, minRole: "Guest" | "User" | "Developer" | "Admin") {
  const levels: Record<string, number> = { Guest: 0, User: 1, Developer: 2, Admin: 3 };
  const current = Math.max(...(user?.roles ?? ["Guest"]).map((role) => levels[role] ?? 0));
  return current >= levels[minRole];
}
