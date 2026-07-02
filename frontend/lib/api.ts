import { clearToken, getToken } from "@/lib/auth";
import type { ApiEnvelope, User } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8100";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
  });
}

export async function apiDelete<T>(path: string): Promise<T> {
  return request<T>(path, { method: "DELETE" });
}

export async function login(email: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
    skipAuth: true
  });
  return data.access_token;
}

export async function currentUser(): Promise<User> {
  return apiGet<User>("/api/auth/me");
}

async function request<T>(
  path: string,
  init: RequestInit & { skipAuth?: boolean } = {}
): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token && !init.skipAuth) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });
  if (response.status === 401 && typeof window !== "undefined") {
    clearToken();
    window.location.href = "/login";
  }
  const payload = await safeJson(response);
  if (!response.ok) {
    const message = payload?.detail ?? payload?.message ?? `API request failed: ${response.status}`;
    throw new ApiError(String(message), response.status);
  }
  if (payload && "data" in payload) {
    return (payload as ApiEnvelope<T>).data;
  }
  return payload as T;
}

async function safeJson(response: Response): Promise<any> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}
