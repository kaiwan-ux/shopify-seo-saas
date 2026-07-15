"use client";

import { ArrowDownRight, ArrowUpRight, Bot, Check, Clock3, ExternalLink, MoreHorizontal, ShieldAlert, ShoppingBag } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { AgentStatus, Approval, Issue, Store } from "@/lib/types";

export function PageIntro({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description: string; actions?: React.ReactNode }) {
  return <div className="mb-7 flex flex-col justify-between gap-5 md:flex-row md:items-end"><div><p className="eyebrow">{eyebrow}</p><h2 className="mt-2 text-3xl font-semibold tracking-[-.035em] sm:text-4xl">{title}</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p></div>{actions && <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>}</div>;
}

export function SeoScoreCard({ score = 0, delta = 0, lastAudit = "Not run yet", status = "Needs review" }: { score?: number; delta?: number; lastAudit?: string; status?: string }) {
  const circumference = 2 * Math.PI * 49;
  return <Card className="metal-panel overflow-hidden"><CardHeader className="flex-row items-center justify-between"><div><p className="eyebrow">SEO health</p><p className="mt-2 text-sm text-muted-foreground">Store-wide score</p></div><Badge variant="success"><ArrowUpRight className="mr-1 h-3 w-3" />{delta} pts</Badge></CardHeader><CardContent className="flex items-end justify-between"><div className="relative h-36 w-36"><svg viewBox="0 0 120 120" className="-rotate-90"><circle cx="60" cy="60" r="49" fill="none" stroke="currentColor" strokeWidth="8" className="text-muted" /><circle cx="60" cy="60" r="49" fill="none" stroke="#bef264" strokeLinecap="round" strokeWidth="8" strokeDasharray={circumference} strokeDashoffset={circumference * (1 - score / 100)} /></svg><div className="absolute inset-0 grid place-items-center text-center"><div><strong className="text-4xl tracking-tight">{score}</strong><span className="block text-[10px] uppercase tracking-widest text-muted-foreground">of 100</span></div></div></div><div className="pb-3 text-right"><p className="text-xs text-muted-foreground">Last audit</p><p className="mt-1 text-sm font-medium">{lastAudit}</p><p className="mt-4 text-xs text-lime-500">{status}</p></div></CardContent></Card>;
}

export function AnalyticsCard({ label, value, delta, positive = true }: { label: string; value: string; delta: string; positive?: boolean }) {
  return <Card className="metal-panel"><CardContent className="p-5"><p className="eyebrow">{label}</p><div className="mt-5 flex items-end justify-between"><strong className="text-3xl font-semibold tracking-tight">{value}</strong><span className={cn("flex items-center gap-1 text-xs", positive ? "text-lime-500" : "text-red-500")}>{positive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}{delta}</span></div></CardContent></Card>;
}

export function AgentCard({ name, role, status, lastRun, actionLabel = "Open", onAction, actionDisabled = false }: { name: string; role: string; status: AgentStatus; lastRun: string; actionLabel?: string; onAction?: () => void; actionDisabled?: boolean }) {
  const variants = { running: "success", complete: "success", attention: "warning", idle: "secondary" } as const;
  return <Card className="transition-transform hover:-translate-y-0.5"><CardContent className="p-5"><div className="flex items-start justify-between"><span className="grid h-10 w-10 place-items-center rounded-xl bg-muted"><Bot className="h-4 w-4" /></span><Badge variant={variants[status]}>{status === "running" && <span className="mr-1.5 h-1.5 w-1.5 animate-pulse rounded-full bg-current" />}{status}</Badge></div><h3 className="mt-5 font-semibold">{name}</h3><p className="mt-1 text-xs text-muted-foreground">{role}</p><div className="mt-5 flex items-center justify-between border-t pt-4 text-[11px] text-muted-foreground"><span>{lastRun}</span><Button size="sm" variant="ghost" onClick={onAction} disabled={actionDisabled}>{actionLabel}</Button></div></CardContent></Card>;
}

export function IssueCard({ issue, onReview }: { issue: Issue; onReview?: (issue: Issue) => void }) {
  const variants = { critical: "destructive", high: "warning", medium: "secondary", low: "success" } as const;
  return <Card><CardContent className="p-5"><div className="flex gap-4"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-muted"><ShieldAlert className="h-4 w-4" /></span><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><h3 className="font-medium">{issue.title}</h3><Badge variant={variants[issue.severity]}>{issue.severity}</Badge></div><p className="mt-2 text-sm leading-6 text-muted-foreground">{issue.explanation}</p><div className="mt-4 flex items-center justify-between text-xs"><span className="text-muted-foreground">{Math.round(issue.confidence * 100)}% confidence</span><Button variant="ghost" size="sm" onClick={() => onReview?.(issue)}>Review <ArrowUpRight className="h-3 w-3" /></Button></div></div></div></CardContent></Card>;
}

export function ApprovalCard({ approval, onApprove, onReject }: { approval: Approval; onApprove: () => void; onReject: () => void }) {
  return <Card className="overflow-hidden"><div className="h-1 bg-gradient-to-r from-amber-400 to-transparent" /><CardContent className="p-5"><div className="flex items-start justify-between gap-3"><div><Badge variant="warning">{approval.risk}</Badge><h3 className="mt-3 font-medium">{approval.action}</h3><p className="mt-1 text-xs text-muted-foreground">{approval.resource} Â· {approval.agent}</p></div><Clock3 className="h-4 w-4 text-muted-foreground" /></div><div className="mt-5 grid grid-cols-2 gap-2"><Button size="sm" variant="outline" onClick={onReject}>Decline</Button><Button size="sm" variant="accent" onClick={onApprove}><Check className="h-3.5 w-3.5" />Approve</Button></div></CardContent></Card>;
}

export function StoreCard({ store }: { store: Store }) {
  return <Card className="metal-panel"><CardContent className="p-6"><div className="flex items-start justify-between"><span className="grid h-11 w-11 place-items-center rounded-xl bg-lime-300 text-black"><ShoppingBag className="h-5 w-5" /></span><Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button></div><h3 className="mt-5 text-lg font-semibold">{store.shop_name}</h3><p className="mt-1 text-xs text-muted-foreground">{store.shop_domain}</p><div className="mt-6 flex items-center justify-between border-t pt-4"><Badge variant={store.is_connected ? "success" : "destructive"}>{store.is_connected ? "Connected" : "Disconnected"}</Badge><Button size="sm" variant="ghost" asChild><a href={`https://${store.shop_domain}`} target="_blank" rel="noreferrer">View <ExternalLink className="h-3.5 w-3.5" /></a></Button></div></CardContent></Card>;
}

