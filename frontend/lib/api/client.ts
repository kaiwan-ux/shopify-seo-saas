import type { AuditResult, Collection, ListResponse, Product, SEOResource, Store, StorePage, User } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

interface TokenPair {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

class ApiClient {
  private accessToken: string | null = null;
  private refreshPromise: Promise<string | null> | null = null;

  constructor() {
    if (typeof window !== "undefined") this.accessToken = localStorage.getItem("access_token");
  }

  hasAccessToken() {
    if (this.accessToken) return true;
    if (typeof window === "undefined") return false;
    this.accessToken = localStorage.getItem("access_token");
    return Boolean(this.accessToken);
  }

  setAccessToken(token: string | null) {
    this.accessToken = token;
    if (typeof window === "undefined") return;
    if (token) localStorage.setItem("access_token", token);
    else localStorage.removeItem("access_token");
  }

  clearSession() {
    this.setAccessToken(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem("refresh_token");
      document.cookie = "seo_session=; path=/; max-age=0; SameSite=Lax";
    }
  }

  async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers);
    if (!(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
    if (this.hasAccessToken()) headers.set("Authorization", `Bearer ${this.accessToken}`);

    let response = await fetch(`${API_URL}${path}`, { ...init, headers, credentials: "include" });
    if (response.status === 401 && typeof window !== "undefined") {
      const token = await this.refresh();
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
        response = await fetch(`${API_URL}${path}`, { ...init, headers, credentials: "include" });
      }
    }
    if (!response.ok) {
      const data = await response.json().catch(() => ({ detail: "Request failed" }));
      const fieldErrors = Array.isArray(data.errors)
        ? data.errors.map((item: { field?: string; message?: string }) => item.message || item.field).filter(Boolean).join(". ")
        : "";
      throw new Error(fieldErrors || data.detail || data.message || "Request failed");
    }
    if (response.status === 204) return undefined as T;
    return response.json() as Promise<T>;
  }

  private async refresh() {
    if (this.refreshPromise) return this.refreshPromise;
    const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
    if (!refreshToken) return null;
    this.refreshPromise = fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
      .then(async (response) => {
        if (!response.ok) {
          this.clearSession();
          return null;
        }
        const tokens = (await response.json()) as TokenPair;
        this.setAccessToken(tokens.access_token);
        localStorage.setItem("refresh_token", tokens.refresh_token);
        return tokens.access_token;
      })
      .finally(() => {
        this.refreshPromise = null;
      });
    return this.refreshPromise;
  }
}

export const api = new ApiClient();

export const authApi = {
  login: (email: string, password: string) =>
    api.request<TokenPair>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (data: { email: string; password: string; full_name: string }) =>
    api.request<User>("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  me: () => api.request<User>("/users/me"),
};

export const shopifyApi = {
  store: () => api.request<Store>("/shopify/store"),
  connect: (shop_domain: string) =>
    api.request<{ authorization_url: string; state: string; shop_domain: string }>("/shopify/connect", {
      method: "POST",
      body: JSON.stringify({ shop_domain }),
    }),
  sync: (sync_type = "full") =>
    api.request("/shopify/sync", { method: "POST", body: JSON.stringify({ sync_type }) }),
  products: (limit = 100) => api.request<ListResponse<Product>>(`/shopify/products?limit=${limit}`),
  collections: (limit = 100) => api.request<ListResponse<Collection>>(`/shopify/collections?limit=${limit}`),
  pages: (limit = 100) => api.request<ListResponse<StorePage>>(`/shopify/pages?limit=${limit}`),
};

export const seoApi = {
  audit: (store_id: string, resources: SEOResource[]) =>
    api.request<AuditResult>("/seo/audit", { method: "POST", body: JSON.stringify({ store_id, resources }) }),
  technical: (payload: unknown) => api.request("/seo/technical", { method: "POST", body: JSON.stringify(payload) }),
  score: (payload: unknown) => api.request("/seo/score", { method: "POST", body: JSON.stringify(payload) }),
  report: (id: string) => api.request(`/seo/report/${id}`),
};

export const aiApi = {
  agents: () => api.request<{ agents: { name: string; description: string }[] }>("/ai/agents"),
  workflow: (workflowId: string) => api.request(`/ai/workflow/${workflowId}`),
  runWorkflow: (task: string, storeId?: string) =>
    api.request("/ai/workflow/start", { method: "POST", body: JSON.stringify({ task, store_id: storeId }) }),
  runAgent: (agent_name: string, task: string, storeId?: string) =>
    api.request("/ai/agents/run", { method: "POST", body: JSON.stringify({ agent_name, task, store_id: storeId }) }),
  applyApprovals: (fixes: Record<string, unknown>[], storeId?: string) =>
    api.request("/ai/approvals/apply", { method: "POST", body: JSON.stringify({ fixes, store_id: storeId }) }),
};


