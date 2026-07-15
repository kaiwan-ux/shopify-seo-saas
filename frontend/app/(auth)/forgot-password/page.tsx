"use client";

import { useState } from "react";
import Link from "next/link";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);
  return (
    <AuthShell
      title={sent ? "Check your inbox" : "Reset password"}
      description={sent ? "A secure reset link is on its way." : "We’ll send a secure reset link."}
      footer={<Link className="text-foreground underline underline-offset-4" href="/login">Back to sign in</Link>}
    >
      {sent ? (
        <div className="metal-panel rounded-2xl p-6 text-sm text-muted-foreground">If an account matches that email, the link will arrive shortly.</div>
      ) : (
        <form className="space-y-5" onSubmit={(event) => { event.preventDefault(); setSent(true); }}>
          <label className="block space-y-2 text-sm font-medium">
            <span>Work email</span><Input type="email" required placeholder="you@company.com" />
          </label>
          <Button className="w-full" size="lg">Send reset link</Button>
        </form>
      )}
    </AuthShell>
  );
}
