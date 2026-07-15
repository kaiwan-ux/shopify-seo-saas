"use client";

import { useAppStore } from "@/stores/app-store";
import type { User } from "@/lib/types";

export function RoleGate({ allow, children, fallback = null }: { allow: User["role"][]; children: React.ReactNode; fallback?: React.ReactNode }) {
  const role = useAppStore((state) => state.user?.role ?? "viewer");
  return allow.includes(role) ? children : fallback;
}
