"use client";

import { motion } from "framer-motion";
import { BadgeCheck, Bug, ShieldCheck, Zap } from "lucide-react";

import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/badge";
import type { Finding } from "@/lib/types";

const agentIcon = {
  security: ShieldCheck,
  performance: Zap,
  logic: Bug,
} as const;

export function FindingsPanel({ findings }: { findings: Finding[] }) {
  return (
    <Card>
      <CardHeader>
        <Bug className="h-4 w-4 text-accent-soft" />
        <CardTitle>Verified Findings</CardTitle>
        <span className="ml-auto text-xs text-zinc-500">{findings.length} total</span>
      </CardHeader>
      <CardBody>
        {findings.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border py-10 text-center text-sm text-zinc-500">
            No findings yet. Run a review (e.g. “run a security review”) to populate this panel.
          </div>
        ) : (
          <div className="space-y-2.5">
            {findings.map((f, i) => {
              const Icon = agentIcon[f.agent];
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="rounded-xl border border-border bg-white/[0.02] p-3.5"
                >
                  <div className="flex items-start gap-2">
                    <Icon className="mt-0.5 h-4 w-4 shrink-0 text-zinc-400" />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-medium text-zinc-100">{f.title}</span>
                        <SeverityBadge severity={f.severity} />
                        {f.verified && (
                          <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400">
                            <BadgeCheck className="h-3.5 w-3.5" /> verified
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-[13px] leading-relaxed text-zinc-400">{f.detail}</p>
                      <code className="mt-1.5 inline-block rounded bg-black/40 px-1.5 py-0.5 font-mono text-[11px] text-accent-soft">
                        {f.file}
                        {f.line ? `:${f.line}` : ""}
                      </code>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
