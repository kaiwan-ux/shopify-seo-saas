"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export interface Column<T> {
  key: string;
  label: string;
  render: (row: T) => React.ReactNode;
  className?: string;
}

export function DataTable<T>({ rows, columns, pageSize = 8, empty = "No records" }: { rows: T[]; columns: Column<T>[]; pageSize?: number; empty?: string }) {
  const [page, setPage] = useState(0);
  const pages = Math.max(1, Math.ceil(rows.length / pageSize));
  const visible = rows.slice(page * pageSize, (page + 1) * pageSize);
  return (
    <div className="overflow-hidden rounded-2xl border bg-card">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[680px] text-left text-sm">
          <thead className="border-b bg-muted/30 text-[10px] uppercase tracking-[.14em] text-muted-foreground">
            <tr>{columns.map((column) => <th key={column.key} className={`px-5 py-3.5 font-semibold ${column.className ?? ""}`}>{column.label}</th>)}</tr>
          </thead>
          <tbody className="divide-y">
            {visible.map((row, index) => <tr key={index} className="transition-colors hover:bg-muted/20">{columns.map((column) => <td key={column.key} className={`px-5 py-4 ${column.className ?? ""}`}>{column.render(row)}</td>)}</tr>)}
          </tbody>
        </table>
        {!visible.length && <div className="p-12 text-center text-sm text-muted-foreground">{empty}</div>}
      </div>
      {pages > 1 && <div className="flex items-center justify-between border-t px-5 py-3 text-xs text-muted-foreground"><span>Page {page + 1} of {pages}</span><div className="flex gap-1"><Button size="icon" variant="ghost" disabled={page === 0} onClick={() => setPage((value) => value - 1)}><ChevronLeft className="h-4 w-4" /></Button><Button size="icon" variant="ghost" disabled={page === pages - 1} onClick={() => setPage((value) => value + 1)}><ChevronRight className="h-4 w-4" /></Button></div></div>}
    </div>
  );
}
