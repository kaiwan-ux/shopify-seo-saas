"use client";

import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import { ConfirmationDialog } from "@/components/dialogs/action-dialogs";

export function DeleteDialog({ trigger, label }: { trigger: React.ReactNode; label: string }) {
  return <ConfirmationDialog trigger={trigger} title={`Delete ${label}?`} destructive />;
}

export function SettingsDialog({ trigger }: { trigger: React.ReactNode }) {
  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Workspace defaults</DialogTitle>
          <DialogDescription>Apply these defaults to new audits and workflows.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <label className="block space-y-2 text-sm font-medium">
            <span>Default audit depth</span>
            <select className="focus-ring h-11 w-full rounded-xl border bg-background px-3 text-sm">
              <option>Complete storefront</option><option>Changed resources</option><option>Priority URLs</option>
            </select>
          </label>
          <label className="flex items-center justify-between rounded-xl border p-4 text-sm">
            <span>Require approval for every write</span><input type="checkbox" defaultChecked className="accent-lime-400" />
          </label>
        </div>
        <DialogFooter><DialogClose asChild><Button variant="outline">Cancel</Button></DialogClose><DialogClose asChild><Button onClick={() => toast.success("Defaults saved")}>Save defaults</Button></DialogClose></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
