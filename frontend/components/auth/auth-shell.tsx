"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

export function AuthShell({
  title,
  description,
  children,
  footer,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <main className="relative grid min-h-screen overflow-hidden bg-black text-white lg:grid-cols-[1.05fr_.95fr]">
      <div className="relative hidden border-r border-white/10 lg:block">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_40%_40%,rgba(190,242,100,.18),transparent_24%),radial-gradient(circle_at_70%_65%,rgba(255,255,255,.12),transparent_28%)]" />
        <div className="absolute inset-0 bg-grid bg-[size:52px_52px]" />
        <div className="relative flex h-full flex-col justify-between p-12">
          <Link href="/" className="flex items-center gap-3 text-sm font-semibold">
            <span className="grid h-9 w-9 place-items-center rounded-full border border-white/15 bg-white/10">
              <Sparkles className="h-4 w-4 text-lime-300" />
            </span>
            SIGNAL SEO
          </Link>
          <div className="max-w-xl">
            <p className="eyebrow !text-white/45">Intelligence with guardrails</p>
            <h2 className="mt-5 text-5xl font-medium leading-[1.05] tracking-[-.045em]">
              Your store&apos;s search operation, finally visible.
            </h2>
          </div>
          <p className="text-xs text-white/35">Audit · Decide · Improve</p>
        </div>
      </div>
      <div className="flex items-center justify-center bg-background px-6 py-16 text-foreground">
        <div className="w-full max-w-md">
          <Link href="/" className="mb-12 flex items-center gap-2 text-sm font-semibold lg:hidden">
            <Sparkles className="h-4 w-4" /> SIGNAL SEO
          </Link>
          <p className="eyebrow">Secure workspace</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-[-.035em]">{title}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{description}</p>
          <div className="mt-8">{children}</div>
          <div className="mt-7 text-center text-sm text-muted-foreground">{footer}</div>
        </div>
      </div>
    </main>
  );
}
