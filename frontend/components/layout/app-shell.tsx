"use client";

import {
  Activity,
  Bell,
  Bot,
  CircleGauge,
  ClipboardCheck,
  FileBarChart,
  Menu,
  Moon,
  Search,
  Settings,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Sun,
  UserRound,
  X,
} from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useRealtime } from "@/hooks/use-realtime";
import { useAppStore } from "@/stores/app-store";

const navigation = [
  { href: "/dashboard", label: "Overview", icon: CircleGauge },
  { href: "/store", label: "Shopify store", icon: ShoppingBag },
  { href: "/seo-audit", label: "SEO audit", icon: ShieldCheck },
  { href: "/agents", label: "Agent center", icon: Bot },
  { href: "/approvals", label: "Approvals", icon: ClipboardCheck },
  { href: "/reports", label: "Reports", icon: FileBarChart },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
];

const secondary = [
  { href: "/notifications", label: "Notifications", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/profile", label: "Profile", icon: UserRound },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [searchOpen, setSearchOpen] = useState(false);
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);
  const toggleSidebar = useAppStore((state) => state.toggleSidebar);
  const user = useAppStore((state) => state.user);
  const store = useAppStore((state) => state.currentStore);
  const storeHydrated = useAppStore((state) => state.storeHydrated);
  const notifications = useAppStore((state) => state.notifications);
  const workflow = useAppStore((state) => state.workflow);
  const audit = useAppStore((state) => state.audit);
  useRealtime();

  const active = useMemo(() => [...navigation, ...secondary].find((item) => pathname.startsWith(item.href)), [pathname]);
  const initials = (user?.full_name || user?.email || "U").split(/[\s@.]+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        setSearchOpen((value) => !value);
      }
      if (event.key === "Escape") setSearchOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {sidebarOpen && <button aria-label="Close navigation" className="fixed inset-0 z-40 bg-black/60 lg:hidden" onClick={toggleSidebar} />}
      <aside className={cn("fixed inset-y-0 left-0 z-50 flex w-[264px] flex-col border-r bg-[#090909] p-4 text-white transition-transform lg:translate-x-0", sidebarOpen ? "translate-x-0" : "-translate-x-full")}>
        <div className="flex h-12 items-center justify-between px-2">
          <Link href="/dashboard" className="flex items-center gap-2.5 text-sm font-semibold tracking-wide">
            <span className="grid h-8 w-8 place-items-center rounded-full border border-white/15 bg-white/10"><Sparkles className="h-4 w-4 text-lime-300" /></span>
            SIGNAL SEO
          </Link>
          <button className="text-white/50 lg:hidden" onClick={toggleSidebar}><X className="h-5 w-5" /></button>
        </div>
        <Link href="/store" className="mt-5 flex items-center justify-between rounded-xl border border-white/10 bg-white/[.045] p-3 text-left hover:bg-white/[.07]">
          <span className="min-w-0">
            <span className="block truncate text-xs font-medium">{store?.shop_name || store?.shop_domain || (storeHydrated ? "No store connected" : "Checking store...")}</span>
            <span className="mt-1 block truncate text-[10px] text-white/40">{store?.shop_domain || (storeHydrated ? "Connect Shopify to load live data" : "Loading connected store")}</span>
          </span>
          <ShoppingBag className="h-4 w-4 text-white/35" />
        </Link>
        <nav className="mt-6 flex-1 space-y-1" aria-label="Main navigation">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link key={item.href} href={item.href} onClick={() => sidebarOpen && toggleSidebar()} className={cn("focus-ring flex h-10 items-center gap-3 rounded-xl px-3 text-sm text-white/50 transition-colors hover:bg-white/[.06] hover:text-white", isActive && "bg-white/[.09] text-white")}>
                <item.icon className={cn("h-4 w-4", isActive && "text-lime-300")} />
                <span className="flex-1">{item.label}</span>
                {item.href === "/notifications" && notifications.length > 0 && <span className="rounded-full bg-lime-300 px-2 py-0.5 text-[10px] font-bold text-black">{notifications.length}</span>}
              </Link>
            );
          })}
        </nav>
        <nav className="space-y-1 border-t border-white/10 pt-4">
          {secondary.map((item) => (
            <Link key={item.href} href={item.href} className={cn("focus-ring flex h-9 items-center gap-3 rounded-xl px-3 text-xs text-white/45 hover:bg-white/[.06] hover:text-white", pathname.startsWith(item.href) && "text-white")}><item.icon className="h-4 w-4" />{item.label}</Link>
          ))}
        </nav>
        <div className="mt-4 flex items-center gap-3 rounded-xl bg-white/[.04] p-3">
          <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-lime-200 to-zinc-500 text-xs font-bold text-black">{initials}</span>
          <span className="min-w-0 flex-1"><span className="block truncate text-xs font-medium">{user?.full_name || user?.email || "Signed-in user"}</span><span className="text-[10px] capitalize text-white/35">{user?.role || "authenticated"}</span></span>
        </div>
      </aside>
      <div className="lg:pl-[264px]">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b bg-background/80 px-4 backdrop-blur-xl sm:px-7">
          <button className="lg:hidden" onClick={toggleSidebar}><Menu className="h-5 w-5" /></button>
          <div className="min-w-0 flex-1">
            <p className="text-[10px] uppercase tracking-[.14em] text-muted-foreground">Workspace / {active?.label ?? "Overview"}</p>
            <h1 className="truncate text-sm font-semibold">{active?.label ?? "Overview"}</h1>
          </div>
          <button onClick={() => setSearchOpen(true)} className="focus-ring hidden h-9 w-60 items-center gap-2 rounded-full border bg-muted/40 px-3 text-xs text-muted-foreground sm:flex">
            <Search className="h-3.5 w-3.5" />Search<span className="ml-auto rounded border px-1.5 py-0.5 text-[9px]">Ctrl K</span>
          </button>
          <Button variant="ghost" size="icon" aria-label="Toggle theme" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}><Sun className="hidden h-4 w-4 dark:block" /><Moon className="h-4 w-4 dark:hidden" /></Button>
          <Button asChild variant="ghost" size="icon" aria-label="Notifications"><Link href="/notifications"><Bell className="h-4 w-4" /></Link></Button>
        </header>
        <main className="mx-auto max-w-[1600px] p-4 sm:p-7"><OperationStrip workflowStatus={workflow.status} auditStatus={audit.status} />{children}</main>
      </div>
      {searchOpen && <SearchPalette onClose={() => setSearchOpen(false)} />}
    </div>
  );
}

function SearchPalette({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const items = [...navigation, ...secondary].filter((item) => item.label.toLowerCase().includes(query.toLowerCase()));
  return (
    <div className="fixed inset-0 z-[100] flex justify-center bg-black/60 p-4 pt-[12vh] backdrop-blur-sm" onMouseDown={onClose}>
      <div className="h-fit w-full max-w-xl overflow-hidden rounded-2xl border bg-card shadow-2xl" onMouseDown={(event) => event.stopPropagation()}>
        <div className="flex items-center gap-3 border-b p-4"><Search className="h-4 w-4 text-muted-foreground" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search pages and actions" className="w-full bg-transparent text-sm outline-none" /></div>
        <div className="max-h-80 p-2">
          {items.map((item) => <Link key={item.href} href={item.href} onClick={onClose} className="flex items-center gap-3 rounded-xl p-3 text-sm hover:bg-muted"><item.icon className="h-4 w-4 text-muted-foreground" />{item.label}</Link>)}
          {!items.length && <p className="p-5 text-center text-sm text-muted-foreground">No results</p>}
        </div>
      </div>
    </div>
  );
}


function OperationStrip({ workflowStatus, auditStatus }: { workflowStatus: string; auditStatus: string }) {
  const active = [
    workflowStatus === "running" ? { href: "/agents", label: "Workflow running" } : null,
    auditStatus === "running" ? { href: "/seo-audit", label: "SEO audit running" } : null,
  ].filter(Boolean) as { href: string; label: string }[];
  if (!active.length) return null;
  return (
    <div className="mb-5 flex flex-wrap gap-2 rounded-2xl border bg-card/70 p-3 text-xs shadow-sm backdrop-blur">
      {active.map((item) => (
        <Link key={item.href} href={item.href} className="flex items-center gap-2 rounded-full bg-muted px-3 py-1.5 hover:text-foreground">
          <span className="h-2 w-2 animate-pulse rounded-full bg-lime-400" />{item.label}
        </Link>
      ))}
    </div>
  );
}


