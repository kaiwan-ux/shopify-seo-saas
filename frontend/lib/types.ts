export type Severity = "critical" | "high" | "medium" | "low";
export type AgentStatus = "running" | "idle" | "complete" | "attention";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "owner" | "admin" | "analyst" | "viewer";
}

export interface Store {
  id: string;
  owner_id?: string;
  shop_domain: string;
  shop_name: string | null;
  is_connected: boolean;
  last_sync_at: string | null;
  last_sync_error?: string | null;
  sync_status: string;
  shopify_shop_id?: string | null;
  installed_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Product {
  id: string;
  store_id?: string;
  shopify_id?: string;
  title: string;
  handle: string;
  description?: string | null;
  status?: string | null;
  vendor?: string | null;
  product_type?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
  synced_at?: string | null;
  is_deleted?: boolean;
}

export interface Collection {
  id: string;
  store_id?: string;
  shopify_id?: string;
  title: string;
  handle: string;
  description?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
  products_count?: number | null;
  synced_at?: string | null;
}

export interface StorePage {
  id: string;
  store_id?: string;
  shopify_id?: string;
  title: string;
  handle: string;
  body_html?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
  is_published?: boolean;
  synced_at?: string | null;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
}

export interface Issue {
  id?: string;
  code: string;
  title: string;
  explanation: string;
  severity: Severity;
  category: string;
  url?: string | null;
  confidence: number;
  approval_required: boolean;
  recommended_action?: string;
  resource_type?: string;
  resource_id?: string | null;
}

export interface Approval {
  id: string;
  action: string;
  resource: string;
  agent: string;
  risk: "moderate" | "dangerous";
  createdAt: string;
}

export interface RealtimeEvent {
  id: string;
  type: "audit" | "agent" | "workflow" | "alert" | "notification" | "tool";
  title: string;
  message: string;
  progress?: number;
  createdAt: string;
}

export interface SEOResource {
  id: string;
  resource_type: "product" | "collection" | "page" | "url" | "store";
  url: string;
  title: string;
  body?: string;
  seo_title?: string | null;
  meta_description?: string | null;
  headings?: string[];
  published?: boolean;
  indexable?: boolean;
  metadata?: Record<string, unknown>;
}

export interface AuditResult {
  findings: Issue[];
  resources_analyzed: number;
  summary: string;
  confidence: number;
  report_id?: string;
}
