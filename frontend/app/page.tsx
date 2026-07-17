"use client";

import { ArrowRight, BarChart3, CheckCircle2, HelpCircle, LineChart, SearchCheck, ShieldCheck, Sparkles, Star, Store, TrendingUp, Workflow, Zap } from "lucide-react";
import Image from "next/image";
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

const benefits = [
  {
    icon: CheckCircle2,
    title: "Always in control",
    description: "Every change requires your approval. No surprises, no automatic edits without your consent.",
  },
  {
    icon: TrendingUp,
    title: "Measurable results",
    description: "Track your SEO score improvements with real-time analytics and actionable insights.",
  },
  {
    icon: Zap,
    title: "Save hours weekly",
    description: "Automate the tedious SEO tasks while you focus on growing your business.",
  },
];

const stats = [
  { value: "10x", label: "Faster SEO audits" },
  { value: "100%", label: "Human approval" },
  { value: "24/7", label: "AI monitoring" },
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

      {/* NEW: Stats Bar - Mobile Optimized */}
      <section className="border-y border-lime-400/20 bg-gradient-to-r from-lime-950/30 via-emerald-950/20 to-lime-950/30 px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-3 gap-4 sm:gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-2xl font-bold text-lime-400 sm:text-4xl lg:text-5xl">
                  {stat.value}
                </div>
                <div className="mt-1 text-xs text-white/60 sm:mt-2 sm:text-sm">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Dashboard Preview Section - Mobile Optimized */}
      <section className="relative overflow-hidden border-t border-white/10 bg-gradient-to-b from-black via-[#0a0a0a] to-black px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          {/* Section Header - Mobile Optimized */}
          <div className="mb-8 text-center sm:mb-12">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-lime-400 sm:mb-3 sm:text-sm">
              Your Command Center
            </p>
            <h2 className="mx-auto max-w-3xl text-2xl font-bold tracking-tight sm:text-3xl lg:text-5xl">
              Complete visibility into your{" "}
              <span className="bg-gradient-to-r from-lime-400 via-emerald-400 to-lime-300 bg-clip-text text-transparent">
                store's SEO health
              </span>
            </h2>
            <p className="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-white/60 sm:mt-4 sm:text-base lg:text-lg">
              Real-time insights, AI-powered recommendations, and full control over every optimization—all in one elegant workspace.
            </p>
          </div>

          {/* Dashboard Image - Mobile Optimized */}
          <div className="relative">
            {/* Glow Effect */}
            <div className="absolute -inset-4 rounded-2xl bg-gradient-to-r from-lime-400/10 via-emerald-400/10 to-lime-400/10 opacity-50 blur-2xl sm:-inset-6 sm:rounded-3xl sm:blur-3xl" />
            
            {/* Image Container - Mobile Optimized */}
            <div className="relative overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br from-neutral-900/80 to-neutral-950/80 p-1.5 shadow-2xl backdrop-blur-sm sm:rounded-2xl sm:p-2">
              <div className="relative aspect-[16/10] overflow-hidden rounded-lg bg-neutral-950 sm:aspect-[16/9] sm:rounded-xl lg:aspect-[16/10]">
                <Image
                  src="/dashboard-preview.png"
                  alt="Signal SEO Dashboard - Complete workspace for Shopify SEO management"
                  fill
                  className="object-cover object-top transition-transform duration-700 hover:scale-105"
                  priority
                  quality={95}
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 90vw, 1200px"
                />
                {/* Subtle Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
              </div>
            </div>

            {/* Decorative Elements */}
            <div className="absolute -left-2 top-1/4 h-16 w-16 rounded-full bg-lime-400/20 blur-2xl sm:-left-4 sm:h-24 sm:w-24 sm:blur-3xl" />
            <div className="absolute -right-2 bottom-1/4 h-20 w-20 rounded-full bg-emerald-400/20 blur-2xl sm:-right-4 sm:h-32 sm:w-32 sm:blur-3xl" />
          </div>
        </div>
      </section>

      {/* NEW: Benefits Section - Mobile Optimized */}
      <section className="border-t border-white/10 bg-gradient-to-b from-black to-neutral-950 px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8 text-center sm:mb-12">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-lime-400 sm:mb-3 sm:text-sm">
              Why Signal SEO
            </p>
            <h2 className="text-2xl font-bold tracking-tight sm:text-3xl lg:text-4xl">
              Built for Shopify merchants who value{" "}
              <span className="text-lime-400">control</span>
            </h2>
          </div>

          <div className="grid gap-4 sm:gap-6 md:grid-cols-3">
            {benefits.map((benefit) => (
              <Card
                key={benefit.title}
                className="border-white/10 bg-gradient-to-br from-white/5 to-white/[.02] text-white backdrop-blur-sm transition-all hover:border-lime-400/30 hover:shadow-lg hover:shadow-lime-400/10"
              >
                <CardContent className="p-5 sm:p-6">
                  <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-lime-400/10 sm:h-12 sm:w-12">
                    <benefit.icon className="h-5 w-5 text-lime-400 sm:h-6 sm:w-6" />
                  </div>
                  <h3 className="mb-2 text-lg font-semibold sm:text-xl">{benefit.title}</h3>
                  <p className="text-sm leading-relaxed text-white/60 sm:text-base">{benefit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden border-t border-white/10 bg-[radial-gradient(ellipse_at_top,rgba(132,204,22,0.1),transparent_50%)] px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-8 lg:grid-cols-[.9fr_1.1fr] lg:items-end lg:gap-10">
            <div>
              <h2 className="mt-2 max-w-2xl text-2xl font-semibold tracking-tight sm:mt-5 sm:text-3xl lg:text-5xl lg:leading-tight">
                Know what is wrong, approve what changes, and watch the store improve.
              </h2>
            </div>
            <p className="max-w-2xl text-sm leading-6 text-white/65 sm:text-base sm:leading-7">
              Signal SEO connects your Shopify catalog with an intelligence layer that finds SEO issues, prepares safe fixes, and keeps every important action behind human approval. It is made for store owners who want practical SEO progress without guessing, spreadsheets, or risky automation.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-black px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <div className="mb-6 flex flex-col justify-between gap-3 sm:mb-8 md:flex-row md:items-end md:gap-4">
            <div>
              <p className="eyebrow">How you operate it</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight sm:mt-3 sm:text-3xl lg:text-4xl">
                A simple left-to-right SEO operating flow.
              </h2>
            </div>
          </div>

          <div className="flex snap-x gap-3 overflow-x-auto pb-4 sm:gap-4 [scrollbar-width:thin]">
            {steps.map((step, index) => (
              <Card key={step.title} className="metal-panel min-w-[260px] snap-start border-white/10 bg-white/[.045] text-white transition-all hover:border-lime-400/30 hover:bg-white/[.06] sm:min-w-[300px] lg:min-w-[320px]">
                <CardContent className="p-5 sm:p-6">
                  <div className="flex items-center justify-between">
                    <span className="grid h-10 w-10 place-items-center rounded-xl bg-lime-400 text-black transition-transform hover:scale-110 sm:h-12 sm:w-12 sm:rounded-2xl">
                      <step.icon className="h-4 w-4 sm:h-5 sm:w-5" />
                    </span>
                    <span className="text-xs font-semibold text-white/35">0{index + 1}</span>
                  </div>
                  <h3 className="mt-5 text-lg font-semibold sm:mt-6 sm:text-xl">{step.title}</h3>
                  <p className="mt-2 text-xs leading-5 text-white/60 sm:mt-3 sm:text-sm sm:leading-6">{step.text}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-white/10 bg-white/[.025] px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <div className="mb-6 flex items-end justify-between gap-4 sm:mb-8 lg:gap-6">
            <div>
              <p className="eyebrow">Merchant stories</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight sm:mt-3 sm:text-3xl lg:text-4xl">
                Trusted by teams that want safer SEO execution.
              </h2>
            </div>
          </div>

          <div className="flex snap-x gap-3 overflow-x-auto pb-4 sm:gap-4 [scrollbar-width:thin]">
            {outcomes.map((item) => (
              <Card key={item.name} className="min-w-[280px] snap-start border-white/10 bg-black/40 text-white backdrop-blur-xl transition-all hover:border-lime-400/20 hover:shadow-lg hover:shadow-lime-400/5 sm:min-w-[340px] lg:min-w-[360px]">
                <CardContent className="p-5 sm:p-6">
                  <div className="flex gap-1 text-lime-400">
                    {Array.from({ length: 5 }).map((_, index) => <Star key={index} className="h-3 w-3 fill-current sm:h-4 sm:w-4" />)}
                  </div>
                  <p className="mt-4 text-sm leading-6 text-white/70 sm:mt-5 sm:leading-7">"{item.quote}"</p>
                  <div className="mt-5 border-t border-white/10 pt-4 sm:mt-6">
                    <p className="font-medium">{item.name}</p>
                    <p className="mt-1 text-xs text-white/45">{item.role}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-black px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24">
        <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[.85fr_1.15fr] lg:gap-10">
          <div>
            <p className="eyebrow">FAQs</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight sm:mt-3 sm:text-3xl lg:text-4xl">
              Clear answers before you connect your store.
            </h2>
            <Button onClick={() => router.push("/register")} className="mt-5 bg-lime-400 text-black transition-all hover:bg-lime-300 hover:shadow-lg hover:shadow-lime-400/20 sm:mt-7">
              Start with your store<ArrowRight className="h-4 w-4" />
            </Button>
          </div>
          <div className="grid gap-2 sm:gap-3">
            {faqs.map((faq) => (
              <Card key={faq.question} className="border-white/10 bg-white/[.04] text-white transition-all hover:border-lime-400/20 hover:bg-white/[.06]">
                <CardContent className="flex gap-3 p-4 sm:gap-4 sm:p-5">
                  <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-lime-400 sm:mt-1 sm:h-5 sm:w-5" />
                  <div>
                    <h3 className="text-sm font-medium sm:text-base">{faq.question}</h3>
                    <p className="mt-1.5 text-xs leading-5 text-white/60 sm:mt-2 sm:text-sm sm:leading-6">{faq.answer}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-[#050505] px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-4 text-sm text-white/50 sm:gap-6 md:flex-row md:items-center">
          <div>
            <p className="text-sm font-semibold text-white sm:text-base">Signal SEO</p>
            <p className="mt-1 text-xs sm:text-sm">Shopify SEO intelligence with human-approved execution.</p>
          </div>
          <div className="flex flex-wrap gap-3 text-xs sm:gap-4 sm:text-sm">
            <button onClick={() => router.push("/login")} className="transition-colors hover:text-white">Login</button>
            <button onClick={() => router.push("/register")} className="transition-colors hover:text-white">Register</button>
            <span>© {new Date().getFullYear()} Signal SEO</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
