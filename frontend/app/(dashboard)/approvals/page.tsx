"use client";

import { CheckCheck, ShieldCheck, X } from "lucide-react";
import { toast } from "sonner";
import { PageIntro } from "@/components/dashboard/cards";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { aiApi } from "@/lib/api/client";
import { useAppStore } from "@/stores/app-store";

type Fix = Record<string, unknown> & {
  field?: string;
  resource_id?: string;
  resource_type?: string;
  current_value?: string | null;
  suggested_value?: string;
  confidence?: number;
};

type WorkflowResult = { pending_approvals?: Fix[]; agent_outputs?: Record<string, unknown>; applied_fixes?: ApplyResult };
type ApplyResult = { result?: { executed?: { fix?: Fix }[]; failed?: { fix?: Fix; error?: string }[]; summary?: string }; reasoning?: string };

export default function ApprovalsPage() {
  const store = useAppStore((state) => state.currentStore);
  const workflow = useAppStore((state) => state.workflow);
  const setWorkflow = useAppStore((state) => state.setWorkflow);
  const appendWorkflowLog = useAppStore((state) => state.appendWorkflowLog);
  const result = workflow.result as WorkflowResult | undefined;
  const approvals = dedupeFixes(result?.pending_approvals ?? []);

  const clearApprovals = () => {
    setWorkflow({ status: "completed", result: { ...(result ?? {}), pending_approvals: [] } });
    toast.info("Pending fixes rejected locally");
  };

  const applyAll = async () => {
    if (!store) return toast.error("Connect a store first");
    if (!approvals.length) return toast.info("Approval queue is clear");
    setWorkflow({ status: "running" });
    appendWorkflowLog(`${new Date().toLocaleTimeString()}  Applying ${approvals.length} approved fixes`);
    try {
      const applied = await aiApi.applyApprovals(approvals, store.id) as ApplyResult;
      const executed = applied.result?.executed ?? [];
      const failed = applied.result?.failed ?? [];
      const failedFixes = failed.map((item) => item.fix).filter(Boolean) as Fix[];
      setWorkflow({ status: "completed", result: { ...(result ?? {}), pending_approvals: failedFixes, applied_fixes: applied }, completedAt: new Date().toISOString() });
      appendWorkflowLog(`${new Date().toLocaleTimeString()}  Approved fixes applied: ${executed.length} succeeded, ${failed.length} failed`);
      if (failed.length) toast.warning(`${executed.length} fixes applied, ${failed.length} could not be applied`);
      else toast.success("Approved fixes applied. Run Store sync to refresh local data.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to apply fixes";
      setWorkflow({ status: "failed", error: message, completedAt: new Date().toISOString() });
      toast.error(message);
    }
  };

  return <><PageIntro eyebrow="Human control layer" title="Approval center" description={store ? `Approval gates for ${store.shop_name || store.shop_domain}.` : "Connect a store to review write approvals."} actions={<><Button variant="outline" onClick={clearApprovals} disabled={!approvals.length}><X className="h-4 w-4" />Reject all</Button><Button variant="accent" onClick={applyAll} disabled={!approvals.length || workflow.status === "running"}><CheckCheck className="h-4 w-4" />Apply approved</Button></>} /><div className="metal-panel mb-6 flex items-center gap-4 rounded-2xl p-5"><span className="grid h-10 w-10 place-items-center rounded-xl bg-lime-300 text-black"><ShieldCheck className="h-5 w-5" /></span><div><p className="text-sm font-medium">Approval policy active</p><p className="mt-1 text-xs text-muted-foreground">Agents suggest changes first. Shopify writes happen only after you approve here.</p></div></div>{approvals.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{approvals.map((fix, index) => <Card key={`${fix.resource_id}-${fix.field}-${index}`}><CardContent className="p-5"><p className="text-xs uppercase tracking-[.14em] text-muted-foreground">{fix.resource_type ?? "resource"} Â· {fix.field ?? "change"}</p><h3 className="mt-3 font-medium">{fix.field === "description_html" ? "Suggested content update" : fix.field === "seo" ? "Suggested SEO title and meta description" : "Suggested SEO update"}</h3><div className="mt-4 space-y-3 text-xs"><div className="rounded-xl bg-muted/30 p-3"><p className="font-medium">Current</p><p className="mt-1 text-muted-foreground">{formatFixValue(fix.current_value)}</p></div><div className="rounded-xl border border-lime-400/30 bg-lime-400/10 p-3"><p className="font-medium">Suggested</p><p className="mt-1 text-muted-foreground">{formatFixValue(fix.suggested_value)}</p></div></div><p className="mt-4 text-[11px] text-muted-foreground">Confidence: {Math.round((fix.confidence ?? 0) * 100)}%</p></CardContent></Card>)}</div> : <div className="rounded-2xl border border-dashed p-16 text-center"><CheckCheck className="mx-auto h-7 w-7 text-lime-500" /><p className="mt-4 font-medium">Queue clear</p><p className="mt-1 text-sm text-muted-foreground">Run a workflow that generates content fixes; approval-required changes will appear here.</p></div>}</>;
}

function dedupeFixes(fixes: Fix[]) {
  const seen = new Set<string>();
  return fixes.filter((fix) => {
    const key = [fix.resource_type, fix.resource_id, fix.field, fix.suggested_value].join("|");
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function formatFixValue(value: unknown) {
  if (!value) return "Empty";
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    const data = value as Record<string, unknown>;
    return Object.entries(data)
      .filter(([, item]) => item !== undefined && item !== null && item !== "")
      .map(([key, item]) => `${key.replace("seo_", "SEO ")}: ${String(item)}`)
      .join("\n") || "Empty";
  }
  return String(value);
}
