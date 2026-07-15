"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const trend = [
  { day: "May 1", score: 71, organic: 42 },
  { day: "May 8", score: 73, organic: 47 },
  { day: "May 15", score: 76, organic: 51 },
  { day: "May 22", score: 78, organic: 53 },
  { day: "May 29", score: 82, organic: 61 },
  { day: "Jun 5", score: 86, organic: 68 },
];

export function AuditTimeline({ data = trend }: { data?: { day: string; score: number; organic?: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ left: -24, right: 8, top: 10 }}>
        <defs>
          <linearGradient id="score" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#bef264" stopOpacity={0.35} />
            <stop offset="1" stopColor="#bef264" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="currentColor" opacity={0.06} vertical={false} />
        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#888" }} />
        <YAxis domain={[60, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#888" }} />
        <Tooltip contentStyle={{ borderRadius: 14, borderColor: "#333", background: "#111", color: "#fff", fontSize: 12 }} />
        <Area type="monotone" dataKey="score" stroke="#bef264" strokeWidth={2} fill="url(#score)" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function IssueDistribution({ critical = 0, high = 0, medium = 0, low = 0 }: { critical?: number; high?: number; medium?: number; low?: number }) {
  const issueData = [
    { name: "Critical", value: critical, color: "#ef4444" },
    { name: "High", value: high, color: "#f59e0b" },
    { name: "Medium", value: medium, color: "#a3a3a3" },
    { name: "Low", value: low, color: "#bef264" },
  ];
  const chartData = issueData.some((item) => item.value > 0) ? issueData : [{ name: "None", value: 1, color: "#27272a" }];
  return (
    <div className="grid grid-cols-[1fr_120px] items-center">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={chartData} dataKey="value" innerRadius={58} outerRadius={83} paddingAngle={3}>
            {chartData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
          </Pie>
          <Tooltip contentStyle={{ borderRadius: 14, borderColor: "#333", background: "#111", color: "#fff", fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
      <div className="space-y-3">
        {issueData.map((item) => <div key={item.name}><div className="flex items-center gap-2 text-xs"><span className="h-2 w-2 rounded-full" style={{ background: item.color }} />{item.name}</div><p className="ml-4 mt-1 text-lg font-semibold">{item.value}</p></div>)}
      </div>
    </div>
  );
}

const activity = [
  { name: "Audit", runs: 18 },
  { name: "Technical", runs: 12 },
  { name: "Content", runs: 28 },
  { name: "Auto fix", runs: 9 },
  { name: "Report", runs: 15 },
];

export function AgentActivity({ data = activity }: { data?: { name: string; runs: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ left: -30 }}>
        <CartesianGrid stroke="currentColor" opacity={0.06} vertical={false} />
        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#888" }} />
        <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#888" }} />
        <Tooltip cursor={{ fill: "rgba(255,255,255,.03)" }} contentStyle={{ borderRadius: 14, borderColor: "#333", background: "#111", color: "#fff", fontSize: 12 }} />
        <Bar dataKey="runs" fill="#bef264" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function PerformanceMetrics() {
  const data = [
    { day: "M", lcp: 2.9, inp: 210 },
    { day: "T", lcp: 2.6, inp: 190 },
    { day: "W", lcp: 2.3, inp: 170 },
    { day: "T", lcp: 2.4, inp: 160 },
    { day: "F", lcp: 2.1, inp: 145 },
    { day: "S", lcp: 2.0, inp: 138 },
  ];
  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={data} margin={{ left: -25 }}>
        <CartesianGrid stroke="currentColor" opacity={0.06} vertical={false} />
        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#888" }} />
        <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#888" }} />
        <Tooltip contentStyle={{ borderRadius: 14, borderColor: "#333", background: "#111", color: "#fff", fontSize: 12 }} />
        <Area type="monotone" dataKey="lcp" stroke="#bef264" fill="#bef264" fillOpacity={0.08} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

