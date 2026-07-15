"use client";

import { Activity, AlertTriangle, ClipboardCheck, Radio, ShieldCheck, Workflow } from "lucide-react";
import { PageIntro } from "@/components/dashboard/cards";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { relativeTime } from "@/lib/seo-metrics";
import { useAppStore } from "@/stores/app-store";

export default function MonitoringPage() {
  const store = useAppStore((state) => state.currentStore);
  const events = useAppStore((state) => state.notifications);
  const workflow = useAppStore((state) => state.workflow);
  const audit = useAppStore((state) => state.audit);
  const activeAlerts = events.filter((event) => event.type === "alert").length;
  const agentOutputs = (workflow.result as { agent_outputs?: Record<string, { reasoning?: string; result?: Record<string, unknown>; confidence?: number }> } | undefined)?.agent_outputs ?? {};
  const monitoring = agentOutputs.monitoring;
  const monitoringResult = monitoring?.result ?? {};

  return <><PageIntro eyebrow="Continuous signals" title="Monitoring" description={store ? `Live regressions and workflow state for ${store.shop_name || store.shop_domain}.` : "Connect a store to monitor live signals."} />
    <div className="grid gap-4 sm:grid-cols-3"><Metric icon={Radio} label="Monitoring status" value={store?.is_connected ? "Online" : "Not connected"} /><Metric icon={Activity} label="Sync state" value={store?.sync_status || "idle"} /><Metric icon={AlertTriangle} label="Active alerts" value={String(activeAlerts)} tone="warning" /></div>
    <div className="mt-5 grid gap-5 xl:grid-cols-[1.1fr_1fr]"><Card><CardHeader><p className="eyebrow">Real monitoring state</p><CardTitle className="mt-2">Latest workflow and audit</CardTitle></CardHeader><CardContent className="grid gap-3 md:grid-cols-2"><StatusBlock icon={Workflow} title="Workflow" value={workflow.status.replace("_", " ")} detail={workflow.completedAt ? `Completed ${relativeTime(workflow.completedAt)}` : workflow.startedAt ? "Running now" : "No workflow started in this browser session"} /><StatusBlock icon={ShieldCheck} title="SEO audit" value={audit.status} detail={audit.completedAt ? `${audit.findings.length} findings · ${relativeTime(audit.completedAt)}` : `${audit.resourcesAnalyzed || 0} resources analyzed`} /><StatusBlock icon={ClipboardCheck} title="Monitoring agent" value={String(monitoringResult.status ?? "not run").replace("_", " ")} detail={monitoring?.reasoning || "Run the Monitoring agent or full workflow to create a current baseline."} /><StatusBlock icon={Activity} title="Regression comparison" value={monitoringResult.previous_score === undefined || monitoringResult.previous_score === null ? "baseline needed" : `${monitoringResult.previous_score} → ${monitoringResult.current_score}`} detail={String(monitoringResult.next_check_recommendation ?? "A second completed workflow gives monitoring something to compare.")} /></CardContent></Card><Card><CardHeader className="flex-row items-center justify-between"><div><p className="eyebrow">Event stream</p><CardTitle className="mt-2">Live activity</CardTitle></div><Badge variant={events.length ? "success" : "secondary"}>{events.length ? "Live" : "Waiting"}</Badge></CardHeader><CardContent className="space-y-2">{events.length ? events.map((event, index) => <div key={`${event.id}-${index}`} className="rounded-xl border bg-muted/20 p-3"><div className="flex items-center justify-between"><p className="text-xs font-medium">{event.title}</p><span className="text-[9px] text-muted-foreground">{event.createdAt}</span></div><p className="mt-1 text-[11px] text-muted-foreground">{event.message}</p>{event.progress && <div className="mt-2 h-1 rounded-full bg-muted"><div className="h-full rounded-full bg-lime-400" style={{ width: `${event.progress}%` }} /></div>}</div>) : <p className="rounded-xl border border-dashed p-8 text-center text-sm text-muted-foreground">No realtime events received yet. Workflow and agent summaries above still use real saved browser state.</p>}</CardContent></Card></div></>;
}

function Metric({ icon: Icon, label, value, tone = "success" }: { icon: typeof Activity; label: string; value: string; tone?: "success" | "warning" }) {
  return <div className="metal-panel rounded-2xl p-5"><Icon className={tone === "warning" ? "h-4 w-4 text-amber-500" : "h-4 w-4 text-lime-500"} /><p className="mt-5 text-2xl font-semibold capitalize">{value}</p><p className="mt-1 text-xs text-muted-foreground">{label}</p></div>;
}

function StatusBlock({ icon: Icon, title, value, detail }: { icon: typeof Activity; title: string; value: string; detail: string }) {
  return <div className="rounded-xl border bg-muted/20 p-4"><div className="flex items-center gap-2"><Icon className="h-4 w-4 text-lime-500" /><p className="text-xs font-medium">{title}</p></div><p className="mt-4 text-lg font-semibold capitalize">{value}</p><p className="mt-2 text-xs leading-5 text-muted-foreground">{detail}</p></div>;
}
