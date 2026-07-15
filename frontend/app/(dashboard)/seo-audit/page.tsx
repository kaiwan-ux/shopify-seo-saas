"use client";

import { Filter, Play, RotateCcw, SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { PageIntro, IssueCard } from "@/components/dashboard/cards";
import { IssueDistribution } from "@/components/dashboard/charts";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { seoApi, shopifyApi } from "@/lib/api/client";
import { collectionToResource, pageToResource, productToResource } from "@/lib/store-resources";
import { useAppStore } from "@/stores/app-store";
import type { Issue, Severity } from "@/lib/types";

const severities: (Severity | "all")[] = ["all", "critical", "high", "medium", "low"];

export default function SeoAuditPage() {
  const store = useAppStore((state) => state.currentStore);
  const auditState = useAppStore((state) => state.audit);
  const setAudit = useAppStore((state) => state.setAudit);
  const resetAudit = useAppStore((state) => state.resetAudit);
  const [filterOpen, setFilterOpen] = useState(false);
  const [configOpen, setConfigOpen] = useState(false);
  const [selectedSeverity, setSelectedSeverity] = useState<Severity | "all">("all");
  const [auditLimit, setAuditLimit] = useState(200);
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);

  const products = useQuery({ queryKey: ["products", auditLimit], queryFn: () => shopifyApi.products(auditLimit), enabled: !!store, staleTime: 2 * 60_000 });
  const collections = useQuery({ queryKey: ["collections", auditLimit], queryFn: () => shopifyApi.collections(auditLimit), enabled: !!store, staleTime: 2 * 60_000 });
  const pages = useQuery({ queryKey: ["pages", auditLimit], queryFn: () => shopifyApi.pages(auditLimit), enabled: !!store, staleTime: 2 * 60_000 });

  const resources = useMemo(() => {
    if (!store) return [];
    return [
      ...(products.data?.items ?? []).map((item) => productToResource(store, item)),
      ...(collections.data?.items ?? []).map((item) => collectionToResource(store, item)),
      ...(pages.data?.items ?? []).map((item) => pageToResource(store, item)),
    ];
  }, [collections.data?.items, pages.data?.items, products.data?.items, store]);

  const runAudit = () => {
    if (!store) return toast.error("Connect a store before running an audit");
    if (!resources.length) return toast.error("Sync store resources before running an audit");
    setAudit({ status: "running", startedAt: new Date().toISOString(), completedAt: undefined, error: undefined, resourcesAnalyzed: resources.length, findings: [] });
    seoApi.audit(store.id, resources)
      .then((result) => {
        const uniqueFindings = dedupeIssues(result.findings ?? []);
        setAudit({ status: "completed", completedAt: new Date().toISOString(), findings: uniqueFindings, resourcesAnalyzed: result.resources_analyzed ?? resources.length, summary: result.summary });
        toast.success(`Audit completed: ${uniqueFindings.length} unique findings`);
      })
      .catch((error: Error) => {
        setAudit({ status: "failed", completedAt: new Date().toISOString(), error: error.message });
        toast.error(error.message || "Audit failed");
      });
  };

  const findings = auditState.findings;
  const groupedFindings = useMemo(() => groupFindings(findings), [findings]);
  const filteredFindings = selectedSeverity === "all" ? groupedFindings : groupedFindings.filter((issue) => issue.severity === selectedSeverity);
  const counts = useIssueCounts(findings);
  const isRunning = auditState.status === "running";

  if (!store) return <Empty title="No store connected" text="Connect your Shopify store before running SEO audits." />;

  return <><PageIntro eyebrow="Intelligence engine" title="SEO audit" description={`Evidence-backed findings for ${store.shop_name || store.shop_domain}.`} actions={<><Button variant="outline" onClick={() => setConfigOpen(true)}><SlidersHorizontal className="h-4 w-4" />Configure</Button><Button variant="outline" onClick={resetAudit} disabled={isRunning}><RotateCcw className="h-4 w-4" />Reset</Button><Button variant="accent" onClick={runAudit} disabled={isRunning || !resources.length}><Play className="h-4 w-4" />{isRunning ? "Audit running" : "Run full audit"}</Button></>} />
    {auditState.status !== "idle" && <div className="metal-panel mb-5 rounded-2xl p-5"><div className="flex items-center justify-between text-sm"><span className="font-medium">{auditState.status === "running" ? "Analyzing synced Shopify resources" : auditState.status === "failed" ? "Audit failed" : "Latest audit complete"}</span><span className="text-muted-foreground">{auditState.resourcesAnalyzed} resources</span></div>{isRunning && <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted"><div className="h-full w-2/3 animate-pulse rounded-full bg-lime-400" /></div>}{auditState.summary && <p className="mt-3 text-sm text-muted-foreground">{auditState.summary}</p>}{auditState.error && <p className="mt-3 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">{auditState.error}</p>}</div>}
    <div className="grid gap-5 xl:grid-cols-[1fr_2fr]"><Card><CardHeader><p className="eyebrow">Open findings</p><CardTitle className="mt-2">{filteredFindings.length} issue groups</CardTitle></CardHeader><CardContent><IssueDistribution critical={counts.critical} high={counts.high} medium={counts.medium} low={counts.low} /><div className="mt-2 grid grid-cols-2 gap-2 text-center text-xs"><div className="rounded-xl bg-muted/40 p-3"><strong className="block text-lg">{findings.length ? Math.round((findings.reduce((sum, item) => sum + item.confidence, 0) / findings.length) * 100) : 0}%</strong><span className="text-muted-foreground">Avg. confidence</span></div><div className="rounded-xl bg-muted/40 p-3"><strong className="block text-lg">{findings.length}</strong><span className="text-muted-foreground">Affected resources</span></div></div></CardContent></Card><div><div className="mb-3 flex items-center justify-between"><h3 className="font-semibold">Priority findings</h3><Button variant="ghost" size="sm" onClick={() => setFilterOpen(true)}><Filter className="h-3.5 w-3.5" />Filter</Button></div><div className="space-y-3">{filteredFindings.length ? filteredFindings.map((issue, index) => <IssueCard key={issue.id ?? `${issue.code}-${index}`} issue={issue} onReview={setSelectedIssue} />) : <div className="rounded-2xl border border-dashed p-12 text-center text-sm text-muted-foreground">{findings.length ? "No findings match the selected filter." : "Run an audit to load findings from your connected store."}</div>}</div></div></div>
    <Dialog open={configOpen} onOpenChange={setConfigOpen}><DialogContent><DialogHeader><DialogTitle>Audit configuration</DialogTitle><DialogDescription>Choose how many synced Shopify resources to include in the next audit.</DialogDescription></DialogHeader><label className="space-y-2 text-sm font-medium"><span>Resource limit per type</span><select value={auditLimit} onChange={(event) => setAuditLimit(Number(event.target.value))} className="focus-ring h-11 w-full rounded-xl border bg-background px-3 text-sm"><option value={50}>Fast scan - 50</option><option value={100}>Balanced - 100</option><option value={200}>Fuller scan - 200</option></select></label><p className="text-xs text-muted-foreground">Current loaded resources: {resources.length}. Use a smaller scan if your store is large and you want faster feedback.</p><DialogFooter><Button variant="outline" onClick={() => setConfigOpen(false)}>Close</Button><Button onClick={() => { setConfigOpen(false); toast.success("Audit settings saved"); }}>Save</Button></DialogFooter></DialogContent></Dialog>
    <Dialog open={filterOpen} onOpenChange={setFilterOpen}><DialogContent><DialogHeader><DialogTitle>Filter findings</DialogTitle><DialogDescription>Show findings by severity.</DialogDescription></DialogHeader><div className="grid grid-cols-2 gap-2">{severities.map((severity) => <Button key={severity} variant={selectedSeverity === severity ? "accent" : "outline"} onClick={() => setSelectedSeverity(severity)} className="capitalize">{severity}</Button>)}</div><DialogFooter><Button onClick={() => setFilterOpen(false)}>Apply</Button></DialogFooter></DialogContent></Dialog>
    <Dialog open={!!selectedIssue} onOpenChange={(open) => !open && setSelectedIssue(null)}><DialogContent><DialogHeader><DialogTitle>{selectedIssue?.title}</DialogTitle><DialogDescription>{selectedIssue?.category} · {selectedIssue?.severity}</DialogDescription></DialogHeader><div className="space-y-4 text-sm"><p className="leading-6 text-muted-foreground">{selectedIssue?.explanation}</p>{selectedIssue?.recommended_action && <div className="rounded-xl border bg-muted/20 p-4"><p className="font-medium">Recommended action</p><p className="mt-1 text-muted-foreground">{selectedIssue.recommended_action}</p></div>}<div className="grid grid-cols-2 gap-2 text-xs"><div className="rounded-xl bg-muted/40 p-3"><strong>{selectedIssue ? Math.round(selectedIssue.confidence * 100) : 0}%</strong><span className="ml-2 text-muted-foreground">confidence</span></div><div className="rounded-xl bg-muted/40 p-3"><strong>{selectedIssue?.approval_required ? "Yes" : "No"}</strong><span className="ml-2 text-muted-foreground">approval</span></div></div></div><DialogFooter><Button onClick={() => setSelectedIssue(null)}>Done</Button></DialogFooter></DialogContent></Dialog>
  </>;
}

function dedupeIssues(findings: Issue[]) {
  const seen = new Set<string>();
  return findings.filter((issue) => {
    const key = [issue.code, issue.resource_type, issue.resource_id, issue.url, issue.title].join("|");
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function groupFindings(findings: Issue[]) {
  const groups = new Map<string, Issue[]>();
  findings.forEach((issue) => {
    const key = [issue.code, issue.title, issue.category, issue.severity].join("|");
    groups.set(key, [...(groups.get(key) ?? []), issue]);
  });

  return Array.from(groups.values()).map((group) => {
    const first = group[0];
    const affectedCount = group.length;
    if (affectedCount === 1) return first;

    const resourceTypes = Array.from(new Set(group.map((issue) => issue.resource_type).filter(Boolean))).join(", ");
    return {
      ...first,
      id: `${first.code}-${first.category}-${first.severity}`,
      resource_id: null,
      url: null,
      confidence: group.reduce((sum, issue) => sum + issue.confidence, 0) / affectedCount,
      explanation: `${first.explanation} Affects ${affectedCount} ${resourceTypes || "resources"}.`,
      recommended_action: `${first.recommended_action ?? "Review affected resources and apply the recommended SEO fix."} This card groups repeated findings so the same issue is shown once.`,
    };
  });
}

function useIssueCounts(findings: Issue[]) {
  return {
    critical: findings.filter((item) => item.severity === "critical").length,
    high: findings.filter((item) => item.severity === "high").length,
    medium: findings.filter((item) => item.severity === "medium").length,
    low: findings.filter((item) => item.severity === "low").length,
  };
}

function Empty({ title, text }: { title: string; text: string }) {
  return <div className="rounded-2xl border border-dashed p-12 text-center"><p className="text-lg font-medium">{title}</p><p className="mt-2 text-sm text-muted-foreground">{text}</p></div>;
}
