"use client";

import { Bell, CheckCheck, CircleAlert, Workflow } from "lucide-react";
import { PageIntro } from "@/components/dashboard/cards";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/stores/app-store";

export default function NotificationsPage() {
  const items = useAppStore((state) => state.notifications);
  const markAllRead = useAppStore((state) => state.markAllRead);
  return <><PageIntro eyebrow="Inbox" title="Notifications" description="Important workflow and monitoring events from your live workspace." actions={<Button variant="outline" onClick={markAllRead} disabled={!items.length}><CheckCheck className="h-4 w-4" />Mark all read</Button>} /><div className="overflow-hidden rounded-2xl border bg-card">{items.length ? items.map((event, index) => <div key={`${event.id}-${index}`} className="flex gap-4 border-b p-5 last:border-0 hover:bg-muted/20"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-muted">{event.type === "alert" ? <CircleAlert className="h-4 w-4 text-amber-500" /> : event.type === "workflow" ? <Workflow className="h-4 w-4 text-lime-500" /> : <Bell className="h-4 w-4" />}</span><div className="min-w-0 flex-1"><div className="flex items-center justify-between gap-3"><p className="font-medium">{event.title}</p><span className="text-[10px] text-muted-foreground">{event.createdAt}</span></div><p className="mt-1 text-sm text-muted-foreground">{event.message}</p>{event.progress && event.progress < 100 && <div className="mt-3 h-1 max-w-md rounded-full bg-muted"><div className="h-full rounded-full bg-lime-400" style={{ width: `${event.progress}%` }} /></div>}</div></div>) : <p className="p-12 text-center text-sm text-muted-foreground">No realtime notifications yet.</p>}</div></>;
}
