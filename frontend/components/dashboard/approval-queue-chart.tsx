"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";

const queue = [
  { priority: "Critical", count: 1 },
  { priority: "High", count: 2 },
  { priority: "Medium", count: 4 },
  { priority: "Low", count: 1 },
];

export function ApprovalQueueChart() {
  return <ResponsiveContainer width="100%" height={220}><BarChart data={queue}><XAxis dataKey="priority" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#888" }} /><Tooltip cursor={{ fill: "rgba(255,255,255,.03)" }} contentStyle={{ borderRadius: 14, borderColor: "#333", background: "#111", color: "#fff", fontSize: 12 }} /><Bar dataKey="count" fill="#bef264" radius={[7, 7, 0, 0]} /></BarChart></ResponsiveContainer>;
}
