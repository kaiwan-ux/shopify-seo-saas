"use client";

import { AlertTriangle, CheckCircle2, ShoppingBag } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { shopifyApi } from "@/lib/api/client";

export function ApprovalDialog({ trigger }: { trigger: React.ReactNode }) {
  return <Dialog><DialogTrigger asChild>{trigger}</DialogTrigger><DialogContent><DialogHeader><DialogTitle>Approve proposed changes?</DialogTitle><DialogDescription>Review live approval requests before Shopify write actions are executed.</DialogDescription></DialogHeader><div className="rounded-xl border bg-muted/25 p-4 text-sm"><p className="font-medium">No pending approval selected</p><p className="mt-1 text-xs text-muted-foreground">Run an agent workflow to generate approval-gated actions.</p></div><DialogFooter><Button variant="outline">Cancel</Button><Button variant="accent" disabled><CheckCircle2 className="h-4 w-4" />Approve</Button></DialogFooter></DialogContent></Dialog>;
}

export function ConfirmationDialog({ trigger, title = "Confirm action", destructive = false, onConfirm }: { trigger: React.ReactNode; title?: string; destructive?: boolean; onConfirm?: () => void }) {
  const [isOpen, setIsOpen] = useState(false);
  const handleConfirm = () => {
    onConfirm?.();
    setIsOpen(false);
    if (!onConfirm) toast.success("Action confirmed");
  };
  return <Dialog open={isOpen} onOpenChange={setIsOpen}><DialogTrigger asChild>{trigger}</DialogTrigger><DialogContent><DialogHeader><DialogTitle>{title}</DialogTitle><DialogDescription>This action is recorded in your workspace activity log.</DialogDescription></DialogHeader><DialogFooter><Button variant="outline" onClick={() => setIsOpen(false)}>Cancel</Button><Button variant={destructive ? "destructive" : "default"} onClick={handleConfirm}>{destructive && <AlertTriangle className="h-4 w-4" />}Confirm</Button></DialogFooter></DialogContent></Dialog>;
}

export function ConnectStoreDialog({ trigger }: { trigger: React.ReactNode }) {
  const [shop, setShop] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const handleConnect = async () => {
    if (!shop) return;
    setIsLoading(true);
    try {
      const data = await shopifyApi.connect(shop.trim());
      window.location.href = data.authorization_url;
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to connect store");
      setIsLoading(false);
    }
  };
  return <Dialog open={isOpen} onOpenChange={setIsOpen}><DialogTrigger asChild>{trigger}</DialogTrigger><DialogContent><DialogHeader><DialogTitle>Connect Shopify store</DialogTitle><DialogDescription>Enter your real `.myshopify.com` domain to begin secure OAuth.</DialogDescription></DialogHeader><label className="space-y-2 text-sm font-medium"><span>Store domain</span><Input value={shop} onChange={(event) => setShop(event.target.value)} placeholder="your-store.myshopify.com" /></label><DialogFooter><Button variant="outline" onClick={() => setIsOpen(false)}>Cancel</Button><Button disabled={!shop || isLoading} onClick={handleConnect}><ShoppingBag className="h-4 w-4" />{isLoading ? "Connecting..." : "Connect"}</Button></DialogFooter></DialogContent></Dialog>;
}
