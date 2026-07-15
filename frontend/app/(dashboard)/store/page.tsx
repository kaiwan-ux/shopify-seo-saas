"use client";

import { Download, Plus, RefreshCw } from "lucide-react";
import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ConnectStoreDialog, ConfirmationDialog } from "@/components/dialogs/action-dialogs";
import { PageIntro, StoreCard } from "@/components/dashboard/cards";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, type Column } from "@/components/ui/data-table";
import { exportCsv } from "@/lib/utils";
import { shopifyApi } from "@/lib/api/client";
import { useAppStore } from "@/stores/app-store";
import type { Collection, Product, StorePage as ShopifyPage } from "@/lib/types";

export default function StorePage() {
  const queryClient = useQueryClient();
  const setCurrentStore = useAppStore((state) => state.setCurrentStore);
  const setStoreHydrated = useAppStore((state) => state.setStoreHydrated);
  
  const storeQuery = useQuery({ queryKey: ["store"], queryFn: shopifyApi.store, retry: false });
  useEffect(() => {
    if (storeQuery.data) {
      setCurrentStore(storeQuery.data);
      setStoreHydrated(true);
    }
    if (storeQuery.error) {
      setCurrentStore(null);
      setStoreHydrated(true);
    }
  }, [setCurrentStore, setStoreHydrated, storeQuery.data, storeQuery.error]);

  const productsQuery = useQuery({ queryKey: ["products", storeQuery.data?.id, 200], queryFn: () => shopifyApi.products(200), enabled: !!storeQuery.data, retry: 1 });
  const collectionsQuery = useQuery({ queryKey: ["collections", storeQuery.data?.id, 200], queryFn: () => shopifyApi.collections(200), enabled: !!storeQuery.data, retry: 1 });
  const pagesQuery = useQuery({ queryKey: ["pages", storeQuery.data?.id, 200], queryFn: () => shopifyApi.pages(200), enabled: !!storeQuery.data, retry: 1 });

  const syncMutation = useMutation({
    mutationFn: () => shopifyApi.sync("full"),
    onSuccess: () => {
      toast.success("Store sync completed");
      queryClient.invalidateQueries({ queryKey: ["store"] });
      queryClient.invalidateQueries({ queryKey: ["products", storeQuery.data?.id] });
      queryClient.invalidateQueries({ queryKey: ["collections", storeQuery.data?.id] });
      queryClient.invalidateQueries({ queryKey: ["pages", storeQuery.data?.id] });
    },
    onError: (error) => toast.error(error.message || "Sync failed"),
  });

  const products = productsQuery.data?.items ?? [];
  const collections = collectionsQuery.data?.items ?? [];
  const pages = pagesQuery.data?.items ?? [];

  const productColumns: Column<Product>[] = [
    { key: "product", label: "Product", render: (row) => <div><p className="font-medium">{row.title}</p><p className="mt-1 text-[10px] text-muted-foreground">/{row.handle}</p></div> },
    { key: "status", label: "Status", render: (row) => <Badge variant={row.status?.toLowerCase() === "active" ? "success" : "secondary"}>{row.status ?? "unknown"}</Badge> },
    { key: "seo", label: "SEO", render: (row) => <span className="text-muted-foreground">{seoStatus(row.seo_title, row.title)}</span> },
    { key: "synced", label: "Synced", render: (row) => <span className="text-muted-foreground">{row.synced_at ? new Date(row.synced_at).toLocaleString() : "-"}</span> },
  ];
  const collectionColumns: Column<Collection>[] = [
    { key: "collection", label: "Collection", render: (row) => <div><p className="font-medium">{row.title}</p><p className="mt-1 text-[10px] text-muted-foreground">/{row.handle}</p></div> },
    { key: "products", label: "Products", render: (row) => row.products_count ?? "-" },
    { key: "seo", label: "SEO", render: (row) => <span className="text-muted-foreground">{seoStatus(row.seo_title, row.title)}</span> },
  ];
  const pageColumns: Column<ShopifyPage>[] = [
    { key: "page", label: "Page", render: (row) => <div><p className="font-medium">{row.title}</p><p className="mt-1 text-[10px] text-muted-foreground">/{row.handle}</p></div> },
    { key: "published", label: "Published", render: (row) => <Badge variant={row.is_published ? "success" : "secondary"}>{row.is_published ? "Published" : "Draft"}</Badge> },
    { key: "seo", label: "SEO", render: (row) => <span className="text-muted-foreground">{seoStatus(row.seo_title, row.title)}</span> },
  ];

  if (storeQuery.isLoading) return <div className="flex min-h-[400px] items-center justify-center text-sm text-muted-foreground">Loading connected store...</div>;
  if (storeQuery.error || !storeQuery.data) return <div className="flex min-h-[400px] flex-col items-center justify-center gap-4"><p className="text-lg font-medium">No store connected</p><p className="text-sm text-muted-foreground">Connect your Shopify store to load live catalog data.</p><ConnectStoreDialog trigger={<Button><Plus className="h-4 w-4" />Connect store</Button>} /></div>;

  const store = storeQuery.data;
  const lastSyncTime = store.last_sync_at ? Math.round((Date.now() - new Date(store.last_sync_at).getTime()) / 60000) : null;

  return (
    <>
      <PageIntro eyebrow="Commerce source" title="Shopify store" description={`${store.shop_name || store.shop_domain} live catalog health and sync state.`} actions={<><ConfirmationDialog trigger={<Button variant="outline" disabled={syncMutation.isPending}><RefreshCw className={`h-4 w-4 ${syncMutation.isPending ? "animate-spin" : ""}`} />{syncMutation.isPending ? "Syncing..." : "Sync now"}</Button>} title="Sync store data?" onConfirm={() => syncMutation.mutate()} /><ConnectStoreDialog trigger={<Button><Plus className="h-4 w-4" />Connect store</Button>} /></>} />
      <div className="mb-7 grid gap-4 lg:grid-cols-[1fr_2fr]"><StoreCard store={store} /><div className="grid grid-cols-2 gap-4"><Metric label="Products" value={productsQuery.data?.total ?? products.length} /><Metric label="Collections" value={collectionsQuery.data?.total ?? collections.length} /><Metric label="Content pages" value={pagesQuery.data?.total ?? pages.length} /><Metric label="Last sync" value={lastSyncTime !== null ? `${lastSyncTime}m` : "Never"} detail={store.sync_status || "idle"} /></div></div>
      <ResourceTable title="Products" rows={products} columns={productColumns} loading={productsQuery.isLoading} onCsv={() => exportCsv("shopify-products", products as unknown as Record<string, unknown>[])} />
      <ResourceTable title="Collections" rows={collections} columns={collectionColumns} loading={collectionsQuery.isLoading} onCsv={() => exportCsv("shopify-collections", collections as unknown as Record<string, unknown>[])} />
      <ResourceTable title="Pages" rows={pages} columns={pageColumns} loading={pagesQuery.isLoading} onCsv={() => exportCsv("shopify-pages", pages as unknown as Record<string, unknown>[])} />
    </>
  );
}

function seoStatus(seoTitle: string | null | undefined, title: string | null | undefined) {
  if (seoTitle?.trim()) return "Title set";
  if (title?.trim()) return "Title fallback";
  return "Missing title";
}

function Metric({ label, value, detail }: { label: string; value: string | number; detail?: string }) {
  return <div className="metal-panel rounded-2xl p-5"><p className="eyebrow">{label}</p><p className="mt-5 text-3xl font-semibold">{value}</p>{detail && <p className="mt-1 text-xs text-lime-500">{detail}</p>}</div>;
}

function ResourceTable<T>({ title, rows, columns, loading, onCsv }: { title: string; rows: T[]; columns: Column<T>[]; loading: boolean; onCsv: () => void }) {
  return <section className="mb-8"><div className="mb-3 flex items-center justify-between"><div><p className="eyebrow">Live Shopify data</p><h3 className="mt-1 font-semibold">{title}</h3></div><Button variant="outline" size="sm" onClick={onCsv} disabled={!rows.length}><Download className="h-3.5 w-3.5" />CSV</Button></div>{loading ? <div className="rounded-2xl border p-10 text-center text-sm text-muted-foreground">Loading {title.toLowerCase()}...</div> : rows.length ? <DataTable rows={rows} columns={columns} /> : <div className="rounded-2xl border border-dashed p-10 text-center text-sm text-muted-foreground">No synced {title.toLowerCase()} found. Run sync after connecting the store.</div>}</section>;
}

