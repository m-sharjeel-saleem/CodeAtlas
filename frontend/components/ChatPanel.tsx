"use client";

import { MessageSquareText, Sparkles } from "lucide-react";

import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  answer: string | null;
  architecture: string | null;
  loading: boolean;
}

function Shimmer() {
  return (
    <div className="space-y-2">
      {[90, 75, 82].map((w, i) => (
        <div
          key={i}
          className="relative h-3 overflow-hidden rounded bg-white/5"
          style={{ width: `${w}%` }}
        >
          <div className="animate-shimmer absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </div>
      ))}
    </div>
  );
}

export function ChatPanel({ answer, architecture, loading }: Props) {
  const content = architecture ?? answer;
  return (
    <Card>
      <CardHeader>
        <MessageSquareText className="h-4 w-4 text-accent-soft" />
        <CardTitle>{architecture ? "Architecture Overview" : "Answer"}</CardTitle>
      </CardHeader>
      <CardBody>
        {loading ? (
          <Shimmer />
        ) : content ? (
          <p className="whitespace-pre-wrap text-[14px] leading-relaxed text-zinc-200">
            {content}
          </p>
        ) : (
          <div className="flex flex-col items-center gap-2 py-10 text-center text-sm text-zinc-500">
            <Sparkles className="h-5 w-5 text-zinc-600" />
            Ask a question about the repository to get a grounded, cited answer.
          </div>
        )}
      </CardBody>
    </Card>
  );
}
