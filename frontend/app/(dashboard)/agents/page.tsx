"use client";

import { Play, RotateCcw, Send, Terminal } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { AgentCard, PageIntro } from "@/components/dashboard/cards";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { aiApi } from "@/lib/api/client";
import { useAppStore } from "@/stores/app-store";
import type { AgentStatus } from "@/lib/types";
import { useState } from "react";

const descriptions: Record<string, string> = {
  audit: "On-page and content findings",
  technical: "Crawl and indexation analysis",
  content: "Metadata and content drafts",
  autofix: "Approved Shopify changes",
  reporting: "Executive reporting",
  monitoring: "Regression detection",
  performance: "Performance opportunities",
  planner: "Workflow orchestration",
};

type AgentOutput = { reasoning?: string; confidence?: number; result?: Record<string, unknown> };
type WorkflowResult = { agent_outputs?: Record<string, AgentOutput>; pending_approvals?: unknown[]; logs?: string[] };

export default function AgentsPage() {
  const store = useAppStore((state) => state.currentStore);
  const workflow = useAppStore((state) => state.workflow);
  const setWorkflow = useAppStore((state) => state.setWorkflow);
  const appendWorkflowLog = useAppStore((state) => state.appendWorkflowLog);
  const resetWorkflow = useAppStore((state) => state.resetWorkflow);
  const [prompt, setPrompt] = useState("");
  const agents = useQuery({ queryKey: ["agents"], queryFn: aiApi.agents, staleTime: 5 * 60_000 });
  const isRunning = workflow.status === "running";

  const run = (task = prompt) => {
    if (!store) return toast.error("Connect a store before running agents");
    const objective = task.trim();
    if (!objective) return;

    const startedAt = new Date().toISOString();
    setWorkflow({ status: "running", task: objective, startedAt, completedAt: undefined, error: undefined, result: undefined, logs: [] });
    appendWorkflowLog(`${new Date().toLocaleTimeString()}  Started workflow for ${store.shop_domain}`);
    appendWorkflowLog(`${new Date().toLocaleTimeString()}  Objective: ${objective}`);
    setPrompt("");

    aiApi.runWorkflow(objective, store.id)
      .then((result) => {
        const data = result as { workflow_id?: string; status?: string; duration_ms?: number };
        const status = data.status === "waiting_approval" ? "waiting_approval" : "completed";
        const workflowResult = result as WorkflowResult & { workflow_id?: string; status?: string; duration_ms?: number; pending_approvals?: unknown[]; logs?: string[] };
        setWorkflow({ id: data.workflow_id, status, completedAt: new Date().toISOString(), result });
        appendWorkflowLog(`${new Date().toLocaleTimeString()}  Workflow ${status}${data.duration_ms ? ` in ${data.duration_ms}ms` : ""}`);
        (workflowResult.logs ?? []).slice(-8).forEach((line) => appendWorkflowLog(String(line)));
        if (workflowResult.pending_approvals?.length) appendWorkflowLog(`${workflowResult.pending_approvals.length} changes are waiting in Approval Center`);
        toast.success(workflowResult.pending_approvals?.length ? "Workflow produced changes for approval" : "Workflow completed");
      })
      .catch((error: Error) => {
        setWorkflow({ status: "failed", completedAt: new Date().toISOString(), error: error.message });
        appendWorkflowLog(`${new Date().toLocaleTimeString()}  Failed: ${error.message}`);
        toast.error(error.message || "Workflow failed");
      });
  };

  const runSingleAgent = (agentName: string) => {
    if (!store) return toast.error("Connect a store before running agents");
    const objective = prompt.trim() || `Run the ${agentName} agent against the connected store and return safe findings`;
    setWorkflow({ status: "running", task: `${agentName} agent: ${objective}`, startedAt: new Date().toISOString(), completedAt: undefined, error: undefined, result: undefined, logs: [] });
    appendWorkflowLog(`${new Date().toLocaleTimeString()}  Started ${agentName} agent for ${store.shop_domain}`);
    aiApi.runAgent(agentName, objective, store.id)
      .then((result) => {
        setWorkflow({ status: "completed", completedAt: new Date().toISOString(), result: { agent_outputs: { [agentName]: result } } });
        appendWorkflowLog(`${new Date().toLocaleTimeString()}  ${agentName} agent completed`);
        appendWorkflowLog(JSON.stringify(result).slice(0, 700));
        toast.success(`${agentName} agent completed`);
      })
      .catch((error: Error) => {
        setWorkflow({ status: "failed", completedAt: new Date().toISOString(), error: error.message });
        appendWorkflowLog(`${new Date().toLocaleTimeString()}  ${agentName} failed: ${error.message}`);
        toast.error(error.message || `${agentName} agent failed`);
      });
  };

  const available = agents.data?.agents ?? [];
  const statusForCard = (name: string): AgentStatus => {
    if (isRunning) return "running";
    if (workflow.status === "failed") return name === "autofix" ? "attention" : "idle";
    if (workflow.status === "completed" || workflow.status === "waiting_approval") return "complete";
    return "idle";
  };

  return <><PageIntro eyebrow="Multi-agent operations" title="Agent center" description={store ? `Direct agents against ${store.shop_name || store.shop_domain}.` : "Connect a store before running live agents."} actions={<><Button variant="outline" onClick={resetWorkflow} disabled={isRunning}><RotateCcw className="h-4 w-4" />Reset status</Button><Button onClick={() => run("Run a standard SEO audit workflow and prioritize safe quick wins without publishing changes")} disabled={!store || isRunning}><Play className="h-4 w-4" />{isRunning ? "Workflow running" : "Run workflow"}</Button></>} />
    {workflow.status !== "idle" && <div className="metal-panel mb-5 rounded-2xl p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm font-medium">{workflow.task}</p><p className="mt-1 text-xs text-muted-foreground">Status: {workflow.status}{workflow.id ? ` · ${workflow.id}` : ""}</p></div>{isRunning && <span className="h-2 w-2 animate-pulse rounded-full bg-lime-400" />}</div>{isRunning && <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-muted"><div className="h-full w-2/3 animate-pulse rounded-full bg-lime-400" /></div>}{workflow.error && <p className="mt-3 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">{workflow.error}</p>}</div>}
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{available.length ? available.map((agent) => <AgentCard key={agent.name} name={`${agent.name[0].toUpperCase()}${agent.name.slice(1)} agent`} role={agent.description || descriptions[agent.name] || "SEO specialist"} status={statusForCard(agent.name)} lastRun={isRunning ? "Running now" : workflow.completedAt ? new Date(workflow.completedAt).toLocaleTimeString() : "Ready"} actionLabel="Run" onAction={() => runSingleAgent(agent.name)} actionDisabled={isRunning || !store} />) : <div className="rounded-2xl border border-dashed p-8 text-sm text-muted-foreground">Loading available agents from backend...</div>}</div>
    <WorkflowSummary result={workflow.result as WorkflowResult | undefined} />
    <div className="mt-5 grid gap-5 xl:grid-cols-[1.1fr_1fr]"><Card><CardHeader><p className="eyebrow">Ask the planner</p><CardTitle className="mt-2">New objective</CardTitle></CardHeader><CardContent><div className="flex gap-2"><Input value={prompt} onChange={(event) => setPrompt(event.target.value)} onKeyDown={(event) => event.key === "Enter" && run()} placeholder="Audit my synced products and prioritize quick wins" /><Button size="icon" onClick={() => run()} disabled={isRunning}><Send className="h-4 w-4" /></Button></div><div className="mt-4 flex flex-wrap gap-2">{["Audit metadata", "Find broken links", "Draft collection copy"].map((value) => <button key={value} onClick={() => setPrompt(value)} className="rounded-full border px-3 py-1.5 text-[11px] text-muted-foreground hover:text-foreground">{value}</button>)}</div></CardContent></Card><Card className="bg-[#090909] text-white"><CardHeader className="flex-row items-center gap-2"><Terminal className="h-4 w-4 text-lime-300" /><CardTitle className="text-sm">Live execution</CardTitle>{isRunning && <span className="ml-auto h-2 w-2 animate-pulse rounded-full bg-lime-300" />}</CardHeader><CardContent className="max-h-72 space-y-2 overflow-auto font-mono text-[11px] text-white/50">{workflow.logs.length ? workflow.logs.map((log, index) => <p key={index}>{log}</p>) : <p>No live workflow logs yet. Start a workflow to test agents on the connected store.</p>}</CardContent></Card></div></>;

}

function WorkflowSummary({ result }: { result?: WorkflowResult }) {
  const outputs = Object.entries(result?.agent_outputs ?? {});
  const pending = result?.pending_approvals?.length ?? 0;
  if (!outputs.length && !pending) return null;
  return (
    <div className="mt-5 rounded-2xl border bg-card p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Workflow output</p>
          <h3 className="mt-1 font-semibold">What the agents produced</h3>
        </div>
        {pending > 0 && <span className="rounded-full bg-amber-500/15 px-3 py-1 text-xs text-amber-500">{pending} waiting approval</span>}
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {outputs.map(([name, output]) => (
          <div key={name} className="rounded-xl border bg-muted/20 p-4">
            <p className="text-xs font-semibold capitalize">{name}</p>
            <p className="mt-2 line-clamp-3 text-xs leading-5 text-muted-foreground">{output.reasoning || "Completed"}</p>
            <p className="mt-3 text-[11px] text-muted-foreground">Confidence: {Math.round((output.confidence ?? 0) * 100)}%</p>
          </div>
        ))}
      </div>
      {pending > 0 && <p className="mt-4 text-sm text-muted-foreground">Open Approval Center to review and apply the suggested Shopify changes.</p>}
    </div>
  );
}
