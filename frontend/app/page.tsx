"use client";

import { ArrowRight, HelpCircle, LineChart, SearchCheck, ShieldCheck, Sparkles, Star, Store, Workflow, Zap } from "lucide-react";
import { useRouter } from "next/navigation";
import LiquidMetalHero from "@/components/ui/liquid-metal-hero";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const steps = [
  {
    title: "Connect",
    icon: Store,
    text: "Securely connect your Shopify store so the workspace reads your real products, collections, and pages.",
  },
  {
    title: "Overview",
    icon: LineChart,
    text: "See store health, catalog status, missing metadata, and live activity from one clean dashboard.",
  },
  {
    title: "Audit",
    icon: SearchCheck,
    text: "Run evidence-backed SEO checks for titles, meta descriptions, thin content, headings, and technical signals.",
  },
  {
    title: "Agents",
    icon: Workflow,
    text: "Let specialist agents plan improvements, draft content, inspect technical issues, and prepare safe fixes.",
  },
  {
    title: "Approval",
    icon: ShieldCheck,
    text: "Review every suggested Shopify change before it is written. You stay in control of publishing.",
  },
  {
    title: "Sync",
    icon: Zap,
    text: "Refresh live Shopify data after approved updates so the audit and dashboard show the latest store state.",
  },
  {
    title: "Monitor growth",
    icon: Sparkles,
    text: "Track improvements, watch regressions, and repeat the workflow until SEO health steadily improves.",
  },
];

const outcomes = [
  {
    name: "North Ridge Gear",
    role: "Outdoor Shopify brand",
    quote: "The approval flow gave our team confidence. We fixed metadata gaps quickly without losing control of our catalog.",
  },
  {
    name: "Aster Home Studio",
    role: "Home decor merchant",
    quote: "The audit showed exactly why pages were weak, then the agents prepared clean fixes we could approve in minutes.",
  },
  {
    name: "Peak Snow Supply",
    role: "Sporting goods store",
    quote: "Sync, audit, approve, repeat became our SEO rhythm. The dashboard made progress obvious for non-technical staff.",
  },
  {
    name: "Luma Essentials",
    role: "Lifestyle catalog",
    quote: "We finally had a simple way to improve product copy and search snippets without touching every page manually.",
  },
];

const faqs = [
  {
    question: "Does it change my Shopify store automatically?",
    answer: "No. Agents prepare suggestions first. Shopify writes happen only after you approve them in the Approval Center.",
  },
  {
    question: "What can the agents improve?",
    answer: "They can improve product and collection SEO titles, meta descriptions, useful page copy, product descriptions, and audit-driven content gaps.",
  },
  {
    question: "Why do I need to sync after applying fixes?",
    answer: "Sync pulls the latest Shopify data back into the workspace, so audits and dashboards measure what is actually live in your store.",
  },
  {
    question: "Will SEO health become perfect in one run?",
    answer: "Usually it improves step by step. Metadata can be fixed quickly, while theme structure, page quality, and deeper content often need repeated review.",
  },
];

export default function HomePage() {
  const router = useRouter();
  return (
    <main className="min-h-screen bg-black text-white">
      <LiquidMetalHero
        title="Search growth, under control."
        subtitle="A focused Shopify SEO workspace where audits, AI agents, approvals, sync, and monitoring work together without taking control away from you."
        primaryCtaLabel="Open workspace"
        secondaryCtaLabel="Create account"
        onPrimaryCtaClick={() => router.push("/login")}
        onSecondaryCtaClick={() => router.push("/register")}
      />

      <section className="relative overflow-hidden border-t border-white/10 bg-[radial-gradient(circle_at_top,#1f2f12_0%,#050505_38%,#000_100%)] px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-10 lg:grid-cols-[.9fr_1.1fr] lg:items-end"><div><h2 className="mt-5 max-w-2xl text-4xl font-semibold tracking-[-.04em] sm:text-5xl">
                Know what is wrong, approve what changes, and watch the store improve.
              </h2>
            </div>
            <p className="max-w-2xl text-sm leading-7 text-white/65 sm:text-base">
              Signal SEO connects your Shopify catalog with an intelligence layer that finds SEO issues, prepares safe fixes, and keeps every important action behind human approval. It is made for store owners who want practical SEO progress without guessing, spreadsheets, or risky automation.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-black px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
            <div>
              <p className="eyebrow">How you operate it</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-[-.035em] sm:text-4xl">A simple left-to-right SEO operating flow.</h2>
            </div>
          </div>

          <div className="flex snap-x gap-4 overflow-x-auto pb-4 [scrollbar-width:thin]">
            {steps.map((step, index) => (
              <Card key={step.title} className="metal-panel min-w-[280px] snap-start border-white/10 bg-white/[.045] text-white sm:min-w-[320px]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="grid h-12 w-12 place-items-center rounded-2xl bg-lime-300 text-black">
                      <step.icon className="h-5 w-5" />
                    </span>
                    <span className="text-xs font-semibold text-white/35">0{index + 1}</span>
                  </div>
                  <h3 className="mt-6 text-xl font-semibold">{step.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-white/60">{step.text}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-white/10 bg-white/[.025] px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8 flex items-end justify-between gap-6">
            <div>
              <p className="eyebrow">Merchant stories</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-[-.035em] sm:text-4xl">Trusted by teams that want safer SEO execution.</h2>
            </div>
          </div>

          <div className="flex snap-x gap-4 overflow-x-auto pb-4 [scrollbar-width:thin]">
            {outcomes.map((item) => (
              <Card key={item.name} className="min-w-[300px] snap-start border-white/10 bg-black/40 text-white backdrop-blur-xl sm:min-w-[360px]">
                <CardContent className="p-6">
                  <div className="flex gap-1 text-lime-300">
                    {Array.from({ length: 5 }).map((_, index) => <Star key={index} className="h-4 w-4 fill-current" />)}
                  </div>
                  <p className="mt-5 text-sm leading-7 text-white/70">“{item.quote}”</p>
                  <div className="mt-6 border-t border-white/10 pt-4">
                    <p className="font-medium">{item.name}</p>
                    <p className="mt-1 text-xs text-white/45">{item.role}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-black px-6 py-24 lg:px-8">
        <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[.85fr_1.15fr]">
          <div>
            <p className="eyebrow">FAQs</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-[-.035em] sm:text-4xl">Clear answers before you connect your store.</h2>
            <Button onClick={() => router.push("/register")} className="mt-7 bg-lime-300 text-black hover:bg-lime-200">
              Start with your store<ArrowRight className="h-4 w-4" />
            </Button>
          </div>
          <div className="grid gap-3">
            {faqs.map((faq) => (
              <Card key={faq.question} className="border-white/10 bg-white/[.04] text-white">
                <CardContent className="flex gap-4 p-5">
                  <HelpCircle className="mt-1 h-5 w-5 shrink-0 text-lime-300" />
                  <div>
                    <h3 className="font-medium">{faq.question}</h3>
                    <p className="mt-2 text-sm leading-6 text-white/60">{faq.answer}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-[#050505] px-6 py-10 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-6 text-sm text-white/50 md:flex-row md:items-center">
          <div>
            <p className="text-base font-semibold text-white">Signal SEO</p>
            <p className="mt-1">Shopify SEO intelligence with human-approved execution.</p>
          </div>
          <div className="flex flex-wrap gap-4">
            <button onClick={() => router.push("/login")} className="hover:text-white">Login</button>
            <button onClick={() => router.push("/register")} className="hover:text-white">Register</button>
            <span>© {new Date().getFullYear()} Signal SEO</span>
          </div>
        </div>
      </footer>
    </main>
  );
}


