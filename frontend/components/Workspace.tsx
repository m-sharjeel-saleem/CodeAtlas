"use client";

import { AlertCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { AgentPipeline, PIPELINE_LENGTH, type PipelineStatus } from "@/components/AgentPipeline";
import { ChatPanel } from "@/components/ChatPanel";
import { FindingsPanel } from "@/components/FindingsPanel";
import { RepoInput } from "@/components/RepoInput";
import { TracePanel } from "@/components/TracePanel";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import type { AnalyzeResponse } from "@/lib/types";

export function Workspace() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<PipelineStatus>("idle");
  const [activeIndex, setActiveIndex] = useState(0);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  // Animate the pipeline forward while a request is in flight.
  useEffect(() => {
    if (status === "running") {
      timer.current = setInterval(() => {
        setActiveIndex((i) => Math.min(i + 1, PIPELINE_LENGTH - 1));
      }, 450);
    }
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [status]);

  const run = async (repo: string, question: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveIndex(0);
    setStatus("running");
    try {
      const res = await api.analyze(repo, question);
      setResult(res);
      setStatus("done");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong.");
      setStatus("idle");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <RepoInput loading={loading} onSubmit={run} />

      {(status !== "idle" || error) && (
        <Card className="animate-fade-up">
          <CardHeader>
            <CardTitle>Agent Pipeline</CardTitle>
            {result && (
              <code className="ml-auto font-mono text-xs text-accent-soft">{result.repo}</code>
            )}
          </CardHeader>
          <CardBody>
            <AgentPipeline status={status} activeIndex={activeIndex} />
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
              loading={loading}
            />
            {result && result.findings.length >= 0 && result.intent === "review" && (
              <FindingsPanel findings={result.findings} />
            )}
          </div>
          {result && <TracePanel trace={result.trace} />}
        </div>
      )}
    </div>
  );
}
