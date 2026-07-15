"use client";

import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ErrorPage({ reset }: { error: Error; reset: () => void }) {
  return <div className="grid min-h-[60vh] place-items-center text-center"><div><AlertTriangle className="mx-auto h-8 w-8 text-amber-500" /><h2 className="mt-4 text-xl font-semibold">This view couldn’t load</h2><p className="mt-2 text-sm text-muted-foreground">Your workspace is safe. Try the request again.</p><Button className="mt-5" onClick={reset}>Try again</Button></div></div>;
}
