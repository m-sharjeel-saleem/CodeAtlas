# CodeAtlas

**An agentic codebase intelligence platform.** Point it at any public GitHub repository and a team of AI agents indexes it, then lets you chat with the code, map its architecture, run a multi-agent security/performance/logic review, and generate missing docs and tests — all streamed live, with traces, evaluation scores, and cost tracking.

> Built to demonstrate production-grade AI engineering: multi-agent orchestration, RAG, tool calling + MCP, evals, observability, and safety guardrails.

---

## What it does

1. **Ingest** — give it a public repo URL; CodeAtlas fetches the source, chunks it, and embeds it into a vector store (Postgres + pgvector).
2. **Chat with the codebase** — ask questions in natural language; get answers grounded in (and citing) the real files. This is retrieval-augmented generation (RAG).
3. **Architecture map** — an agent produces a structured overview of modules and how they connect.
4. **Agentic review** — three specialist agents (Security, Performance, Logic) inspect the code in parallel; a Critic agent verifies each finding against the actual source to suppress hallucinations.
5. **Generate** — draft missing docstrings and unit tests; optionally open a PR via the GitHub MCP tool behind a human-approval gate.
6. **Observe** — a dashboard shows every agent step, token usage, latency, cost, and evaluation scores per run.

## Why it exists

Understanding an unfamiliar codebase is slow. CodeAtlas compresses hours of reading into minutes, and in doing so demonstrates the full stack of skills modern AI Engineer / Agentic AI Engineer roles screen for.

---

## Architecture

```
Next.js (App Router, Tailwind + shadcn/ui)
   │  auth · chat · trace / eval / cost dashboards
   │  SSE (token + agent-step streaming)
   ▼
FastAPI (Python)  ──  LangGraph multi-agent graph
   │                    • Router        decides which path a request takes
   │                    • Indexer       chunk + embed repo into pgvector
   │                    • Retriever     hybrid (semantic + keyword) RAG
   │                    • Reviewers      Security · Performance · Logic (parallel)
   │                    • Critic         verifies findings against real source
   │                    • Generator     docstrings / tests
   ▼
Supabase (Postgres + pgvector + Auth)   Redis (queue · cache · cost counters)
   │
MCP tools: GitHub API (repo, files, PRs, issues)
LLM: Anthropic Claude (Opus 4.8 for reasoning, Sonnet 4.6 for throughput)
```

## Tech stack

| Layer | Choice |
|---|---|
| Agent backend | Python, FastAPI, LangGraph, LangChain |
| LLM | Anthropic Claude (Opus 4.8 / Sonnet 4.6) |
| Vector store | Postgres + pgvector (via Supabase) |
| Queue / cache | Redis |
| Tools | GitHub API via Model Context Protocol (MCP) |
| Frontend | Next.js (App Router), TypeScript, Tailwind, shadcn/ui |
| Auth | Supabase Auth |

---

## Safety & "done right" principles

- **Keys server-side only** — no LLM/API keys in the frontend bundle. `.env` is git-ignored; `.env.example` holds placeholders.
- **Prompt-injection defense** — repo content (READMEs, comments) is treated as untrusted input; retrieved code is delimited and agents are instructed to ignore embedded instructions.
- **No arbitrary execution** — CodeAtlas *analyzes* code; it never runs untrusted code. Generated tests are written to files, never executed against untrusted input.
- **Cost caps & rate limits** — hard per-session and per-user token/cost ceilings, enforced in Redis.
- **Auth + row-level security** — users only see their own runs.
- **Demo data only** — public repositories. Pointing CodeAtlas at private/proprietary code changes the data-handling requirements and hosting choices.

---

## Build roadmap

- **MVP** — ingest → index → chat-with-codebase (RAG) + architecture summary, streaming, auth, deployed.
- **Advanced** — multi-agent review (Security/Performance/Logic) + Critic, trace viewer (cost/latency/tokens), guardrails.
- **Standout** — evals dashboard with real numbers, doc/test generation, human-in-the-loop "open a PR" via MCP, architecture write-up.

---

## Local setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in your keys
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the API, http://localhost:8000/health for a health check.

### Frontend

Scaffolded in a later step (`create-next-app`). See `frontend/`.

---

## Project structure

```
backend/
  app/
    main.py            FastAPI entry (CORS, routers, lifespan)
    config.py          Typed settings loaded from environment
    api/routes.py      Endpoints: /ingest, /chat (SSE), /review, /runs
    agents/
      state.py         Shared LangGraph state
      graph.py         StateGraph wiring
      nodes/           router, indexer, retriever, reviewer, critic
    services/
      llm.py           Claude client
      github.py        Repo fetch via GitHub API
    core/
      guardrails.py    Prompt-injection defense, cost caps
frontend/              Next.js app (added later)
```
