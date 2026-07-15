"use client";

import { Save, Settings2 } from "lucide-react";
import { toast } from "sonner";
import { PageIntro } from "@/components/dashboard/cards";
import { SettingsDialog } from "@/components/dialogs/more-dialogs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAppStore } from "@/stores/app-store";

export default function SettingsPage() {
  const store = useAppStore((state) => state.currentStore);
  return <><PageIntro eyebrow="Workspace controls" title="Settings" description="Agent behavior, notifications, and storefront preferences." actions={<SettingsDialog trigger={<Button variant="outline"><Settings2 className="h-4 w-4" />Defaults</Button>} />} /><div className="grid gap-5 xl:grid-cols-[1.2fr_1fr]"><Card><CardHeader><p className="eyebrow">Store preferences</p><CardTitle className="mt-2">SEO defaults</CardTitle></CardHeader><CardContent className="space-y-5"><label className="block space-y-2 text-sm font-medium"><span>Brand name</span><Input value={store?.shop_name || store?.shop_domain || "No connected store"} readOnly /></label><label className="block space-y-2 text-sm font-medium"><span>Primary market</span><select className="focus-ring h-11 w-full rounded-xl border bg-background px-3 text-sm"><option>Use Shopify store market</option><option>United States - English</option><option>United Kingdom - English</option><option>Canada - English</option></select></label><label className="block space-y-2 text-sm font-medium"><span>Content tone</span><Input placeholder="Set preferred brand tone" /></label><Button onClick={() => toast.success("Preferences saved locally") }><Save className="h-4 w-4" />Save changes</Button></CardContent></Card><Card><CardHeader><p className="eyebrow">Guardrails</p><CardTitle className="mt-2">Agent permissions</CardTitle></CardHeader><CardContent className="space-y-3">{[["Require approval for writes", true],["Allow scheduled audits", true],["Allow redirect suggestions", true],["Allow automatic publishing", false]].map(([label, checked]) => <label key={String(label)} className="flex items-center justify-between rounded-xl border p-4 text-sm"><span>{label}</span><input type="checkbox" defaultChecked={Boolean(checked)} className="h-4 w-4 accent-lime-400" /></label>)}</CardContent></Card><Card><CardHeader><p className="eyebrow">Notifications</p><CardTitle className="mt-2">Alert routing</CardTitle></CardHeader><CardContent className="space-y-3">{["Critical SEO issues", "Approval requests", "Workflow completion", "Weekly summary"].map((label) => <label key={label} className="flex items-center justify-between rounded-xl p-2 text-sm"><span>{label}</span><input type="checkbox" defaultChecked className="accent-lime-400" /></label>)}</CardContent></Card></div></>;
}
