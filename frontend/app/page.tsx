import {
  Brain,
  GitBranch,
  Network,
  ScanSearch,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { Header } from "@/components/Header";
import { Workspace } from "@/components/Workspace";

const FEATURES = [
  {
    icon: Network,
    title: "Multi-agent orchestration",
    desc: "A LangGraph pipeline routes work across specialist agents that run in parallel.",
  },
  {
    icon: ScanSearch,
    title: "RAG over real code",
    desc: "Repos are chunked and embedded into pgvector for grounded, cited answers.",
  },
  {
    icon: ShieldCheck,
    title: "Verified review",
    desc: "Security, performance, and logic agents — each finding checked against source.",
  },
  {
    icon: Brain,
    title: "Critic anti-hallucination",
    desc: "A critic agent confirms or rejects every claim before it reaches you.",
  },
  {
    icon: GitBranch,
    title: "MCP tool calling",
    desc: "Agents act through the GitHub MCP server with a human-approval gate.",
  },
  {
    icon: Sparkles,
    title: "Full observability",
    desc: "Live trace of every step with token, latency, and cost accounting.",
  },
];

export default function Home() {
  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 pb-24">
        {/* Hero */}
        <section className="py-14 text-center sm:py-20">
          <div className="mx-auto mb-5 inline-flex items-center gap-2 rounded-full border border-border bg-white/[0.03] px-3 py-1.5 text-xs text-zinc-400">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            Agentic AI · LangGraph · RAG · MCP
          </div>
          <h1 className="mx-auto max-w-3xl text-balance text-4xl font-bold tracking-tight sm:text-6xl">
            <span className="text-gradient">Understand any codebase</span>
            <br />
            in minutes, not hours.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-pretty text-[15px] leading-relaxed text-zinc-400">
            CodeAtlas points a team of AI agents at any public repository — chat with the code,
            map its architecture, and run a verified security, performance, and logic review.
          </p>
        </section>

        {/* The product */}
        <Workspace />

        {/* Features */}
        <section id="features" className="mt-24">
          <h2 className="text-center text-sm font-semibold uppercase tracking-[0.2em] text-zinc-500">
            Built like a production AI system
          </h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => {
              const Icon = f.icon;
              return (
                <div
                  key={f.title}
                  className="glass rounded-2xl p-5 transition-colors hover:border-accent/30"
                >
                  <div className="grid h-10 w-10 place-items-center rounded-xl bg-accent/15 text-accent-soft">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-3.5 text-[15px] font-semibold text-zinc-100">{f.title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-zinc-400">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      <footer className="border-t border-border py-8 text-center text-xs text-zinc-600">
        CodeAtlas — built by M. Sharjeel Saleem ·{" "}
        <a
          href="https://github.com/m-sharjeel-saleem/CodeAtlas"
          className="text-zinc-400 hover:text-white"
        >
          source
        </a>
      </footer>
    </>
  );
}
