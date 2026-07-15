"use client";

import { Download, FileText, Printer } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { PageIntro } from "@/components/dashboard/cards";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, type Column } from "@/components/ui/data-table";
import { shopifyApi } from "@/lib/api/client";
import { exportCsv } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";

type ReportRow = { id: string; type: string; score: string | number; issues: number; created: string; status: string };

export default function ReportsPage() {
  const store = useAppStore((state) => state.currentStore);
  const products = useQuery({ queryKey: ["products"], queryFn: () => shopifyApi.products(200), enabled: !!store });
  const rows: ReportRow[] = store ? [{ id: store.id.slice(0, 8), type: "Live store baseline", score: "Run audit", issues: products.data?.items.filter((item) => !item.seo_title || !item.seo_description).length ?? 0, created: store.last_sync_at ? new Date(store.last_sync_at).toLocaleString() : "Not synced", status: store.sync_status || "idle" }] : [];
  const columns: Column<ReportRow>[] = [
    { key: "id", label: "Report", render: (row) => <div className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-muted"><FileText className="h-4 w-4" /></span><div><p className="font-medium">{row.id}</p><p className="mt-1 text-[10px] text-muted-foreground">{row.type}</p></div></div> },
    { key: "score", label: "Score", render: (row) => <strong>{row.score}</strong> },
    { key: "issues", label: "Metadata gaps", render: (row) => row.issues },
    { key: "created", label: "Last sync", render: (row) => <span className="text-muted-foreground">{row.created}</span> },
    { key: "status", label: "Status", render: (row) => <Badge variant={row.status === "error" ? "destructive" : "secondary"}>{row.status}</Badge> },
  ];
  return <><PageIntro eyebrow="Decision records" title="Reports" description={store ? `Exportable baseline for ${store.shop_name || store.shop_domain}.` : "Connect a store to generate reports."} actions={<><Button variant="outline" onClick={() => window.print()} disabled={!rows.length}><Printer className="h-4 w-4" />PDF</Button><Button onClick={() => exportCsv("seo-reports", rows)} disabled={!rows.length}><Download className="h-4 w-4" />CSV</Button></>} />{rows.length ? <DataTable rows={rows} columns={columns} /> : <div className="rounded-2xl border border-dashed p-12 text-center text-sm text-muted-foreground">No connected-store report data yet.</div>}</>;
}
