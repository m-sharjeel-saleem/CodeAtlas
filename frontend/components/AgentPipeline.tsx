"use client";

import { motion } from "framer-motion";
import { Brain, FileSearch, GitBranch, Search, ShieldCheck, Zap, Bug } from "lucide-react";

import { cn } from "@/lib/utils";

export type PipelineStatus = "idle" | "running" | "done";

const AGENTS = [
  { key: "router", label: "Router", icon: GitBranch, desc: "Classifies intent" },
  { key: "retriever", label: "Retriever", icon: Search, desc: "Hybrid RAG" },
  { key: "security", label: "Security", icon: ShieldCheck, desc: "OWASP / secrets" },
  { key: "performance", label: "Performance", icon: Zap, desc: "Hot-path cost" },
  { key: "logic", label: "Logic", icon: Bug, desc: "Edge cases" },
  { key: "critic", label: "Critic", icon: Brain, desc: "Verifies findings" },
] as const;

interface Props {
  status: PipelineStatus;
  /** Index of the currently active agent while running (0..AGENTS.length-1). */
  activeIndex: number;
}

export function AgentPipeline({ status, activeIndex }: Props) {
  return (
    <div className="flex flex-wrap items-stretch gap-2">
      {AGENTS.map((agent, i) => {
        const state =
          status === "done"
            ? "done"
            : status === "running" && i <= activeIndex
              ? i === activeIndex
                ? "running"
                : "done"
              : "idle";
        const Icon = agent.icon;
        return (
          <motion.div
            key={agent.key}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className={cn(
              "flex min-w-[116px] flex-1 flex-col gap-1.5 rounded-xl border p-3 transition-colors",
              state === "idle" && "border-border bg-white/[0.02]",
              state === "running" && "animate-pulse-ring border-accent/50 bg-accent/10",
              state === "done" && "border-emerald-500/30 bg-emerald-500/[0.06]",
            )}
          >
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "grid h-7 w-7 place-items-center rounded-lg",
                  state === "idle" && "bg-white/5 text-zinc-500",
                  state === "running" && "bg-accent/20 text-accent-soft",
                  state === "done" && "bg-emerald-500/15 text-emerald-300",
                )}
              >
                <Icon className="h-4 w-4" />
              </span>
              <span className="text-xs font-semibold text-zinc-200">{agent.label}</span>
            </div>
            <span className="text-[11px] leading-tight text-zinc-500">{agent.desc}</span>
          </motion.div>
        );
      })}
    </div>
  );
}

export const PIPELINE_LENGTH = AGENTS.length;
