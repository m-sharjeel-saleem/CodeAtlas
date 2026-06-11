"use client";

import { motion } from "framer-motion";
import { Activity, Coins, Cpu } from "lucide-react";

import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import type { RunTrace } from "@/lib/types";

function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-white/[0.02] p-3">
      <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wide text-zinc-500">
        {icon}
        {label}
      </div>
      <div className="mt-1 font-mono text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

export function TracePanel({ trace }: { trace: RunTrace }) {
  return (
    <Card>
      <CardHeader>
        <Activity className="h-4 w-4 text-accent-soft" />
        <CardTitle>Run Trace & Observability</CardTitle>
      </CardHeader>
      <CardBody className="space-y-4">
        <div className="grid grid-cols-3 gap-2">
          <Metric
            icon={<Coins className="h-3 w-3" />}
            label="Cost"
            value={`$${trace.cost_usd.toFixed(4)}`}
          />
          <Metric
            icon={<Cpu className="h-3 w-3" />}
            label="Tokens in"
            value={trace.tokens_in.toLocaleString()}
          />
          <Metric
            icon={<Cpu className="h-3 w-3" />}
            label="Tokens out"
            value={trace.tokens_out.toLocaleString()}
          />
        </div>

        <div className="space-y-1.5">
          {trace.steps.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06 }}
              className="flex items-start gap-2 font-mono text-[12px] text-zinc-400"
            >
              <span className="mt-0.5 text-accent-soft">›</span>
              <span>{step}</span>
            </motion.div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
