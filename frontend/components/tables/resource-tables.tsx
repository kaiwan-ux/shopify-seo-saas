"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable, type Column } from "@/components/ui/data-table";
import type { Issue, RealtimeEvent } from "@/lib/types";

type Resource = { id: string; title: string; status: string; score: number; updated: string };

const resourceColumns: Column<Resource>[] = [
  { key: "title", label: "Resource", render: (row) => <div><p className="font-medium">{row.title}</p><p className="mt-1 text-[10px] text-muted-foreground">{row.id}</p></div> },
  { key: "status", label: "Status", render: (row) => <Badge variant={row.status === "Active" ? "success" : "secondary"}>{row.status}</Badge> },
  { key: "score", label: "SEO score", render: (row) => <strong>{row.score}</strong> },
  { key: "updated", label: "Updated", render: (row) => <span className="text-muted-foreground">{row.updated}</span> },
];

export function ProductsTable({ rows }: { rows: Resource[] }) {
  return <DataTable rows={rows} columns={resourceColumns} empty="No products" />;
}

export function CollectionsTable({ rows }: { rows: Resource[] }) {
  return <DataTable rows={rows} columns={resourceColumns} empty="No collections" />;
}

export function PagesTable({ rows }: { rows: Resource[] }) {
  return <DataTable rows={rows} columns={resourceColumns} empty="No pages" />;
}

export function IssuesTable({ rows }: { rows: Issue[] }) {
  const columns: Column<Issue>[] = [
    { key: "issue", label: "Issue", render: (row) => <div><p className="font-medium">{row.title}</p><p className="mt-1 text-[10px] text-muted-foreground">{row.code}</p></div> },
    { key: "severity", label: "Severity", render: (row) => <Badge variant={row.severity === "critical" ? "destructive" : row.severity === "high" ? "warning" : "secondary"}>{row.severity}</Badge> },
    { key: "category", label: "Category", render: (row) => row.category },
    { key: "confidence", label: "Confidence", render: (row) => `${Math.round(row.confidence * 100)}%` },
  ];
  return <DataTable rows={rows} columns={columns} empty="No issues" />;
}

export function MonitoringLogsTable({ rows }: { rows: RealtimeEvent[] }) {
  const columns: Column<RealtimeEvent>[] = [
    { key: "event", label: "Event", render: (row) => <div><p className="font-medium">{row.title}</p><p className="mt-1 text-[10px] text-muted-foreground">{row.message}</p></div> },
    { key: "type", label: "Type", render: (row) => <Badge variant="secondary">{row.type}</Badge> },
    { key: "time", label: "Time", render: (row) => row.createdAt },
    { key: "progress", label: "Progress", render: (row) => row.progress ? `${row.progress}%` : "—" },
  ];
  return <DataTable rows={rows} columns={columns} empty="No monitoring events" />;
}

export { DataTable as ReportsTable };
