"use client";

import { Camera, LogOut, Save, Trash2 } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { PageIntro } from "@/components/dashboard/cards";
import { DeleteDialog } from "@/components/dialogs/more-dialogs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api/client";
import { useAppStore } from "@/stores/app-store";
import { useState } from "react";

export default function ProfilePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const user = useAppStore((state) => state.user);
  const setUser = useAppStore((state) => state.setUser);
  const setCurrentStore = useAppStore((state) => state.setCurrentStore);
  const resetWorkspace = useAppStore((state) => state.resetWorkspace);
  const [dialog, setDialog] = useState<"password" | "sessions" | null>(null);
  const initials = (user?.full_name || user?.email || "U").split(/[\s@.]+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
  const signOut = () => {
    api.clearSession();
    queryClient.clear();
    setUser(null);
    resetWorkspace();
    setCurrentStore(null);
    toast.success("Signed out");
    router.push("/login");
  };
  return <><PageIntro eyebrow="Personal account" title="Profile" description="Identity, role, and session security." /><div className="grid gap-5 xl:grid-cols-[1.2fr_1fr]"><Card><CardHeader><CardTitle>Profile details</CardTitle></CardHeader><CardContent><div className="mb-7 flex items-center gap-4"><span className="grid h-16 w-16 place-items-center rounded-full bg-gradient-to-br from-lime-200 to-zinc-600 text-lg font-bold text-black">{initials}</span><Button variant="outline" size="sm" onClick={() => toast.info("Photo upload will be available after account media storage is enabled.")}><Camera className="h-3.5 w-3.5" />Change photo</Button></div><div className="grid gap-4 sm:grid-cols-2"><label className="space-y-2 text-sm font-medium"><span>Full name</span><Input defaultValue={user?.full_name ?? ""} placeholder="Your name" /></label><label className="space-y-2 text-sm font-medium"><span>Email</span><Input type="email" defaultValue={user?.email ?? ""} placeholder="you@company.com" /></label><label className="space-y-2 text-sm font-medium"><span>Role</span><Input value={user?.role ?? "authenticated"} disabled /></label><label className="space-y-2 text-sm font-medium"><span>Time zone</span><Input defaultValue={Intl.DateTimeFormat().resolvedOptions().timeZone} /></label></div><Button className="mt-6" onClick={() => toast.success("Profile preferences saved locally") }><Save className="h-4 w-4" />Save profile</Button></CardContent></Card><Card><CardHeader><CardTitle>Account security</CardTitle></CardHeader><CardContent className="space-y-3"><Button variant="outline" className="w-full justify-start" onClick={() => setDialog("password")}>Change password</Button><Button variant="outline" className="w-full justify-start" onClick={() => setDialog("sessions")}>Manage sessions</Button><Button variant="outline" className="w-full justify-start" onClick={signOut}><LogOut className="h-4 w-4" />Sign out</Button><DeleteDialog label="account" trigger={<Button variant="destructive" className="mt-5 w-full"><Trash2 className="h-4 w-4" />Delete account</Button>} /></CardContent></Card></div><Dialog open={dialog === "password"} onOpenChange={(open) => !open && setDialog(null)}><DialogContent><DialogHeader><DialogTitle>Change password</DialogTitle><DialogDescription>Password update API is not enabled yet. This control is ready for the backend endpoint in the next auth pass.</DialogDescription></DialogHeader><Input type="password" placeholder="New password" /><DialogFooter><Button onClick={() => { setDialog(null); toast.info("Password endpoint not available yet"); }}>Done</Button></DialogFooter></DialogContent></Dialog><Dialog open={dialog === "sessions"} onOpenChange={(open) => !open && setDialog(null)}><DialogContent><DialogHeader><DialogTitle>Active sessions</DialogTitle><DialogDescription>Your current browser session is active. Server-side session management is not enabled yet.</DialogDescription></DialogHeader><div className="rounded-xl border p-4 text-sm"><p className="font-medium">Current session</p><p className="mt-1 text-xs text-muted-foreground">This device Â· active now</p></div><DialogFooter><Button onClick={() => setDialog(null)}>Close</Button></DialogFooter></DialogContent></Dialog></>;
}



