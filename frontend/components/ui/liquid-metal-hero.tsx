"use client";

import { LiquidMetal, liquidMetalPresets } from "@paper-design/shaders-react";
import { motion } from "framer-motion";
import { ArrowUpRight, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface LiquidMetalHeroProps {
  badge?: string;
  title: string;
  subtitle: string;
  primaryCtaLabel: string;
  secondaryCtaLabel?: string;
  onPrimaryCtaClick: () => void;
  onSecondaryCtaClick?: () => void;
  features?: string[];
}

export default function LiquidMetalHero({
  badge,
  title,
  subtitle,
  primaryCtaLabel,
  secondaryCtaLabel,
  onPrimaryCtaClick,
  onSecondaryCtaClick,
  features = [],
}: LiquidMetalHeroProps) {
  const item = { hidden: { opacity: 0, y: 28 }, visible: { opacity: 1, y: 0 } };

  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden bg-black text-white">
      {/* Green-tinted overlay for the liquid metal */}
      <div className="absolute inset-0 z-0">
        <LiquidMetal {...liquidMetalPresets[2]} style={{ position: "absolute", inset: 0 }} />
        {/* Green color overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-lime-950/40 via-emerald-950/30 to-lime-900/40 mix-blend-multiply" />
        <div className="absolute inset-0 bg-gradient-to-t from-lime-500/10 via-transparent to-emerald-500/10" />
      </div>
      <div className="absolute inset-0 z-[1] bg-gradient-to-b from-black/30 via-black/40 to-black/85" />
      <motion.div
        className="relative z-10 mx-auto w-full max-w-7xl px-6 py-24 text-center lg:px-8"
        initial="hidden"
        animate="visible"
        transition={{ staggerChildren: 0.12 }}
      >
        {badge && (
          <motion.div variants={item} className="mb-8 flex justify-center">
            <Badge className="border-lime-400/30 bg-lime-950/40 px-4 py-2 text-lime-300 backdrop-blur-xl" variant="outline">
              <span className="mr-2 h-1.5 w-1.5 rounded-full bg-lime-400 shadow-[0_0_12px_#a3e635]" />
              {badge}
            </Badge>
          </motion.div>
        )}
        <motion.h1
          variants={item}
          className="mx-auto max-w-5xl bg-gradient-to-r from-lime-400 via-lime-300 to-emerald-400 bg-clip-text text-5xl font-semibold leading-[.92] tracking-[-.055em] text-transparent sm:text-7xl lg:text-[104px]"
        >
          {title}
        </motion.h1>
        <motion.p 
          variants={item} 
          className="mx-auto mt-7 max-w-2xl text-base leading-7 sm:text-lg"
        >
          <span className="bg-gradient-to-r from-white via-lime-100 to-emerald-100 bg-clip-text text-transparent">
            {subtitle}
          </span>
        </motion.p>
        <motion.div variants={item} className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button onClick={onPrimaryCtaClick} size="lg" className="min-w-44 bg-lime-400 text-black hover:bg-lime-300">
            {primaryCtaLabel}<ArrowUpRight className="h-4 w-4" />
          </Button>
          {secondaryCtaLabel && onSecondaryCtaClick && (
            <Button onClick={onSecondaryCtaClick} variant="outline" size="lg" className="min-w-44 border-lime-400/30 bg-lime-400/10 text-lime-300 hover:bg-lime-400/20 hover:border-lime-400/50">
              {secondaryCtaLabel}
            </Button>
          )}
        </motion.div>
        {features.length > 0 && (
          <motion.div variants={item} className="mx-auto mt-14 max-w-3xl">
            <Card className="border-white/15 bg-black/25 p-5 backdrop-blur-2xl">
              <div className="grid gap-3 sm:grid-cols-3">
                {features.map((feature) => (
                  <div key={feature} className="flex items-center justify-center gap-2 text-sm text-white/75">
                    <Check className="h-4 w-4 text-lime-300" />{feature}
                  </div>
                ))}
              </div>
            </Card>
          </motion.div>
        )}
      </motion.div>
    </section>
  );
}
