/** Mirrors the FastAPI backend response shapes. */

export type Intent = "chat" | "architecture" | "review" | "generate";

export type Severity = "low" | "medium" | "high" | "critical";

export interface Finding {
  agent: "security" | "performance" | "logic";
  title: string;
  detail: string;
  file: string;
  line: number | null;
  severity: Severity;
  verified: boolean;
}

export interface RunTrace {
  steps: string[];
  cost_usd: number;
  tokens_in: number;
  tokens_out: number;
}

export interface IngestResponse {
  repo: string;
  files_indexed: number;
  chunks: number;
  embedded: boolean;
  persisted: boolean;
  error: string | null;
}

export interface AnalyzeResponse {
  repo: string;
  intent: Intent;
  answer: string | null;
  architecture: string | null;
  findings: Finding[];
  trace: RunTrace;
}
