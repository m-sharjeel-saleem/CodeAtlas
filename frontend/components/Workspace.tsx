"use client";

import { AlertCircle, Database, Loader2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { AgentPipeline, PIPELINE_LENGTH, type PipelineStatus } from "@/components/AgentPipeline";
import { ChatPanel } from "@/components/ChatPanel";
import { FindingsPanel } from "@/components/FindingsPanel";
import { RepoInput } from "@/components/RepoInput";
import { TracePanel } from "@/components/TracePanel";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import type { AnalyzeResponse, IngestResponse } from "@/lib/types";

type Phase = "idle" | "indexing" | "analyzing" | "done";

export function Workspace() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [activeIndex, setActiveIndex] = useState(0);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [ingest, setIngest] = useState<IngestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const indexedRepo = useRef<string | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const loading = phase === "indexing" || phase === "analyzing";
  const pipelineStatus: PipelineStatus =
    phase === "analyzing" ? "running" : phase === "done" ? "done" : "idle";

  useEffect(() => {
    if (phase === "analyzing") {
      timer.current = setInterval(
        () => setActiveIndex((i) => Math.min(i + 1, PIPELINE_LENGTH - 1)),
        450,
      );
    }
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [phase]);

  const run = async (repo: string, question: string) => {
    setError(null);
    setResult(null);
    setActiveIndex(0);
    try {
      // 1. Index the repo once per session (RAG needs it before we can answer).
      if (indexedRepo.current !== repo) {
        setPhase("indexing");
        const report = await api.ingest(repo);
        setIngest(report);
        indexedRepo.current = repo;
      }
      // 2. Run the agent graph.
      setPhase("analyzing");
      const res = await api.analyze(repo, question);
      setResult(res);
      setPhase("done");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong.");
      setPhase("idle");
    }
  };

  return (
    <div className="space-y-5">
      <RepoInput loading={loading} onSubmit={run} />

      {phase === "indexing" && (
        <div className="flex items-center gap-2 rounded-xl border border-accent/30 bg-accent/10 px-4 py-3 text-sm text-accent-soft">
          <Loader2 className="h-4 w-4 animate-spin" />
          Indexing repository — fetching, chunking, and embedding source files…
        </div>
      )}

      {(phase !== "idle" || error) && phase !== "indexing" && (
        <Card className="animate-fade-up">
          <CardHeader>
            <CardTitle>Agent Pipeline</CardTitle>
            {ingest && (
              <span className="ml-auto inline-flex items-center gap-1.5 text-xs text-zinc-500">
                <Database className="h-3.5 w-3.5" />
                {ingest.chunks} chunks · {ingest.files_indexed} files
                {ingest.embedded ? " · embedded" : " · keyword-only"}
              </span>
            )}
          </CardHeader>
          <CardBody>
            <AgentPipeline status={pipelineStatus} activeIndex={activeIndex} />
          </CardBody>
        </Card>
      )}

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {(loading || result) && (
        <div className="grid gap-5 lg:grid-cols-2">
          <div className="space-y-5">
            <ChatPanel
              answer={result?.answer ?? null}
              architecture={result?.architecture ?? null}
              loading={phase === "analyzing"}
            />
            {result?.intent === "review" && <FindingsPanel findings={result.findings} />}
          </div>
          {result && <TracePanel trace={result.trace} />}
        </div>
      )}
    </div>
  );
}
