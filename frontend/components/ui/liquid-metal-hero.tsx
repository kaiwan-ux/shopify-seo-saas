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
      <LiquidMetal {...liquidMetalPresets[2]} style={{ position: "absolute", inset: 0, zIndex: 0 }} />
      <div className="absolute inset-0 z-[1] bg-gradient-to-b from-black/20 via-black/35 to-black/80" />
      <motion.div
        className="relative z-10 mx-auto w-full max-w-7xl px-6 py-24 text-center lg:px-8"
        initial="hidden"
        animate="visible"
        transition={{ staggerChildren: 0.12 }}
      >
        {badge && (
          <motion.div variants={item} className="mb-8 flex justify-center">
            <Badge className="border-white/20 bg-black/25 px-4 py-2 text-white backdrop-blur-xl" variant="outline">
              <span className="mr-2 h-1.5 w-1.5 rounded-full bg-lime-300 shadow-[0_0_12px_#bef264]" />
              {badge}
            </Badge>
          </motion.div>
        )}
        <motion.h1
          variants={item}
          className="mx-auto max-w-5xl text-5xl font-semibold leading-[.92] tracking-[-.055em] sm:text-7xl lg:text-[104px]"
        >
          {title}
        </motion.h1>
        <motion.p variants={item} className="mx-auto mt-7 max-w-2xl text-base leading-7 text-white/70 sm:text-lg">
          {subtitle}
        </motion.p>
        <motion.div variants={item} className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button onClick={onPrimaryCtaClick} size="lg" className="min-w-44 bg-white text-black hover:bg-white/90">
            {primaryCtaLabel}<ArrowUpRight className="h-4 w-4" />
          </Button>
          {secondaryCtaLabel && onSecondaryCtaClick && (
            <Button onClick={onSecondaryCtaClick} variant="outline" size="lg" className="min-w-44 border-white/20 bg-black/20 text-white hover:bg-white/10">
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
