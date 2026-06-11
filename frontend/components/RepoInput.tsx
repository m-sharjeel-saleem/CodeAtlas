"use client";

import { ArrowRight, Github, Loader2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

const EXAMPLES = ["facebook/react", "vercel/next.js", "tiangolo/fastapi"];

interface Props {
  loading: boolean;
  onSubmit: (repo: string, question: string) => void;
}

export function RepoInput({ loading, onSubmit }: Props) {
  const [repo, setRepo] = useState("");
  const [question, setQuestion] = useState("");

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!repo.trim() || !question.trim() || loading) return;
    onSubmit(repo.trim(), question.trim());
  };

  return (
    <form onSubmit={submit} className="glass rounded-2xl p-4 shadow-card sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-border bg-black/30 px-3">
          <Github className="h-4 w-4 shrink-0 text-zinc-500" />
          <input
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            placeholder="owner/name  (e.g. facebook/react)"
            className="h-11 w-full bg-transparent font-mono text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none"
          />
        </div>
      </div>

      <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask anything, or try 'run a security review'…"
          className="h-11 flex-1 rounded-xl border border-border bg-black/30 px-3 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-accent/50"
        />
        <Button type="submit" size="lg" disabled={loading} className="sm:w-auto">
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Analyzing
            </>
          ) : (
            <>
              Analyze <ArrowRight className="h-4 w-4" />
            </>
          )}
        </Button>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
        <span>Try:</span>
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => setRepo(ex)}
            className="rounded-md border border-border px-2 py-1 font-mono text-zinc-400 transition-colors hover:bg-white/5 hover:text-white"
          >
            {ex}
          </button>
        ))}
      </div>
    </form>
  );
}
