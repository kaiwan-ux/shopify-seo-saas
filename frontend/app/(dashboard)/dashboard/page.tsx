"use client";

import { ArrowRight, Play } from "lucide-react";
import Link from "next/link";
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AuditTimeline, IssueDistribution } from "@/components/dashboard/charts";
import { AnalyticsCard, PageIntro, SeoScoreCard } from "@/components/dashboard/cards";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { shopifyApi } from "@/lib/api/client";
import { collectionToResource, pageToResource, productToResource } from "@/lib/store-resources";
import { countIssues, issueLabel, liveFindingsFromResources, relativeTime, scoreFromFindings } from "@/lib/seo-metrics";
import { useAppStore } from "@/stores/app-store";

export default function DashboardPage() {
  const store = useAppStore((state) => state.currentStore);
  const storeHydrated = useAppStore((state) => state.storeHydrated);
  const notifications = useAppStore((state) => state.notifications);
  const audit = useAppStore((state) => state.audit);
  const workflow = useAppStore((state) => state.workflow);
  const products = useQuery({ queryKey: ["products", store?.id, 200], queryFn: () => shopifyApi.products(200), enabled: !!store, staleTime: 30_000 });
  const collections = useQuery({ queryKey: ["collections", store?.id, 200], queryFn: () => shopifyApi.collections(200), enabled: !!store, staleTime: 30_000 });
  const pages = useQuery({ queryKey: ["pages", store?.id, 200], queryFn: () => shopifyApi.pages(200), enabled: !!store, staleTime: 30_000 });

  const resources = useMemo(() => {
    if (!store) return [];
    return [
      ...(products.data?.items ?? []).map((item) => productToResource(store, item)),
      ...(collections.data?.items ?? []).map((item) => collectionToResource(store, item)),
      ...(pages.data?.items ?? []).map((item) => pageToResource(store, item)),
    ];
  }, [collections.data?.items, pages.data?.items, products.data?.items, store]);

  if (!store && !storeHydrated) return <div className="rounded-2xl border border-dashed p-12 text-center text-sm text-muted-foreground">Checking connected Shopify store...</div>;
  if (!store) return <NoStore />;

  const liveFindings = liveFindingsFromResources(resources);
  const findings = audit.status === "completed" && audit.findings.length ? audit.findings : liveFindings;
  const counts = countIssues(findings);
  const score = scoreFromFindings(findings);
  const missingSeo = liveFindings.filter((item) => item.code.startsWith("metadata.")).length;
  const liveEvents = notifications.slice(0, 4);
  const trendData = buildTrend(score, audit.completedAt ?? store.last_sync_at ?? undefined);
  const agentOutputs = Object.entries((workflow.result as { agent_outputs?: Record<string, { reasoning?: string; confidence?: number }> } | undefined)?.agent_outputs ?? {});

  return (
    <>
      <PageIntro eyebrow={new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })} title="Store pulse" description={`${store.shop_name || store.shop_domain} live SEO and catalog overview.`} actions={<><Button variant="outline" asChild><Link href="/reports">Reports</Link></Button><Button variant="accent" asChild><Link href="/seo-audit"><Play className="h-4 w-4" />Run audit</Link></Button></>} />
      <div className="grid gap-4 xl:grid-cols-[1.15fr_2fr]"><SeoScoreCard score={score} delta={0} lastAudit={relativeTime(audit.completedAt)} status={findings.length ? "Needs review" : "Healthy"} /><div className="grid grid-cols-2 gap-4 lg:grid-cols-4"><AnalyticsCard label="Products" value={String(products.data?.total ?? products.data?.items.length ?? 0)} delta="live" /><AnalyticsCard label="Collections" value={String(collections.data?.total ?? collections.data?.items.length ?? 0)} delta="live" /><AnalyticsCard label="Pages" value={String(pages.data?.total ?? pages.data?.items.length ?? 0)} delta="live" /><AnalyticsCard label="Open SEO" value={String(findings.length)} delta={findings.length ? "needs review" : "clear"} positive={findings.length === 0} /></div></div>
      <div className="mt-4 grid gap-4 xl:grid-cols-[2fr_1fr]"><Card><CardHeader className="flex-row items-center justify-between"><div><p className="eyebrow">Momentum</p><CardTitle className="mt-2">SEO score trend</CardTitle></div><Badge variant="secondary">Live store data</Badge></CardHeader><CardContent><AuditTimeline data={trendData} /></CardContent></Card><Card><CardHeader><p className="eyebrow">Current audit</p><CardTitle className="mt-2">Issue mix</CardTitle></CardHeader><CardContent><IssueDistribution critical={counts.critical} high={counts.high} medium={counts.medium} low={counts.low} /></CardContent></Card></div>
      <div className="mt-4 grid gap-4 xl:grid-cols-[1.2fr_1fr]"><Card><CardHeader className="flex-row items-center justify-between"><div><p className="eyebrow">Live operations</p><CardTitle className="mt-2">Workspace status</CardTitle></div><Button asChild variant="ghost" size="sm"><Link href="/monitoring">View monitoring<ArrowRight className="h-3.5 w-3.5" /></Link></Button></CardHeader><CardContent className="grid gap-3 sm:grid-cols-3"><StatusTile label="Workflow" value={workflow.status} detail={workflow.completedAt ? relativeTime(workflow.completedAt) : workflow.startedAt ? "running now" : "not started"} /><StatusTile label="Audit" value={audit.status} detail={audit.completedAt ? relativeTime(audit.completedAt) : `${audit.resourcesAnalyzed || resources.length} resources loaded`} /><StatusTile label="Events" value={String(liveEvents.length)} detail={liveEvents.length ? "recent signals" : "no realtime events"} /></CardContent></Card><Card><CardHeader><p className="eyebrow">Agents</p><CardTitle className="mt-2">Latest contribution</CardTitle></CardHeader><CardContent className="space-y-2">{agentOutputs.length ? agentOutputs.slice(0, 5).map(([name, output]) => <div key={name} className="rounded-xl border bg-muted/20 p-3"><div className="flex items-center justify-between"><p className="text-xs font-semibold capitalize">{name}</p><span className="text-[10px] text-muted-foreground">{Math.round((output.confidence ?? 0) * 100)}%</span></div><p className="mt-1 line-clamp-2 text-xs leading-5 text-muted-foreground">{output.reasoning || "Completed"}</p></div>) : <p className="rounded-xl border border-dashed p-8 text-center text-sm text-muted-foreground">Run a workflow or single agent to see real agent outputs here.</p>}</CardContent></Card></div>
      <Card className="mt-4"><CardHeader className="flex-row items-center justify-between"><div><p className="eyebrow">Priority queue</p><CardTitle className="mt-2">What to fix next</CardTitle></div><Button asChild variant="outline" size="sm"><Link href="/seo-audit">Run audit</Link></Button></CardHeader><CardContent>{findings.length ? <p className="text-sm text-muted-foreground">{issueLabel(findings.length)} {missingSeo ? `${missingSeo} are metadata-related and should be handled through Approval Center.` : "Run the audit page to review grouped evidence."}</p> : <p className="text-sm text-muted-foreground">No obvious SEO gaps detected in synced products, collections, or pages.</p>}</CardContent></Card>
    </>
  );
}

function buildTrend(score: number, completedAt?: string) {
  const now = completedAt ? new Date(completedAt) : new Date();
  return Array.from({ length: 6 }, (_, index) => {
    const date = new Date(now);
    date.setDate(now.getDate() - (5 - index));
    return { day: date.toLocaleDateString(undefined, { month: "short", day: "numeric" }), score };
  });
}


function NoStore() {
  return <div className="rounded-2xl border border-dashed p-12 text-center"><p className="text-lg font-medium">Connect a Shopify store to begin</p><p className="mt-2 text-sm text-muted-foreground">The dashboard only shows live data from your connected store.</p><Button asChild className="mt-5"><Link href="/store">Open store connection</Link></Button></div>;
}

function StatusTile({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <div className="rounded-xl border bg-muted/20 p-4"><p className="text-[10px] uppercase tracking-[.14em] text-muted-foreground">{label}</p><p className="mt-3 text-lg font-semibold capitalize">{value.replace("_", " ")}</p><p className="mt-1 text-xs text-muted-foreground">{detail}</p></div>;
}

