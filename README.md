<div align="center">

# 🧭 CodeAtlas

### Agentic Codebase Intelligence

**Point CodeAtlas at any public repository. A team of AI agents indexes it — then you can chat with the code, map its architecture, and run a verified security, performance, and logic review, all with live cost and trace observability.**

`Python` · `FastAPI` · `LangGraph` · `Google Gemini` · `RAG` · `pgvector` · `MCP` · `Next.js` · `TypeScript`

</div>

---

## 📌 Status

| | |
|---|---|
| **Stage** | Active development |
| **Backend** | ✅ Multi-agent graph (router → retriever → parallel reviewers → critic), guardrails, tests passing |
| **Frontend** | ✅ Production UI (chat, animated agent pipeline, findings, trace dashboard), build verified |
| **In progress** | Real ingest + RAG (GitHub fetch → chunk → embed → pgvector), live Gemini calls, SSE streaming, evals |

This repository is a working foundation: the agent orchestration, safety layer, API, and full UI are built and verified. The LLM-backed steps currently return structured placeholders so the system runs end-to-end before keys are wired — the next milestone replaces them with real Gemini-powered retrieval and review.

---

## 🎯 What it does

Understanding an unfamiliar codebase is slow. CodeAtlas compresses hours of reading into minutes:

1. **Ingest** — give it a public repo (e.g. `facebook/react`); CodeAtlas fetches, chunks, and embeds the source into a vector store.
2. **💬 Chat with the codebase** — ask in natural language; get answers grounded in and citing the real files (RAG).
3. **🗺️ Architecture map** — an agent produces a structured overview of modules and how they connect.
4. **🔍 Agentic review** — Security, Performance, and Logic agents inspect the code in parallel; a **Critic** agent verifies each finding against the actual source to suppress hallucinations.
5. **📝 Generate** — draft missing docstrings and tests; optionally open a PR via the GitHub MCP tool behind a human-approval gate.
6. **📊 Observe** — a dashboard shows every agent step, token usage, latency, cost, and evaluation scores per run.

## 💡 What makes it different

Most "chat with your repo" tools are a single model call behind a text box. CodeAtlas is built like a **production AI system**:

- **Multi-agent, not monolithic** — specialist agents run in parallel and converge, orchestrated with a LangGraph state machine.
- **Verified, not trusting** — a Critic agent confirms every finding against source, cutting the false positives that make naive LLM review useless.
- **Observable, not opaque** — real token, latency, and cost numbers surface in the UI for every run.
- **Safe by design** — prompt-injection defense, no arbitrary code execution, and hard cost caps.

---

## 🏗️ Architecture

```
Next.js (App Router · Tailwind · shadcn-style)
   │  auth · chat · animated agent pipeline · trace / cost / eval dashboards
   │  SSE (token + agent-step streaming)
   ▼
FastAPI (Python)  ──  LangGraph multi-agent graph
   │                    • Router        classify intent
   │                    • Retriever     hybrid (semantic + keyword) RAG
   │                    • Reviewers      Security ‖ Performance ‖ Logic  (parallel)
   │                    • Critic         verify findings against real source
   │                    • Generator     docstrings / tests
   ▼
Supabase (Postgres + pgvector + Auth)   Redis (queue · cache · cost counters)
   │
MCP tools: GitHub API (repo, files, PRs, issues)
LLM: Google Gemini (2.5 Pro for reasoning, 2.5 Flash for throughput)
```

## 🧰 Tech stack

| Layer | Choice |
|---|---|
| Agent backend | Python · FastAPI · LangGraph · LangChain |
| LLM & embeddings | Google Gemini (2.5 Pro / 2.5 Flash · `text-embedding-004`) |
| Vector store | Postgres + pgvector (Supabase) |
| Queue / cache | Redis (Upstash) |
| Tools | GitHub API via Model Context Protocol (MCP) |
| Frontend | Next.js (App Router) · TypeScript · Tailwind · framer-motion |
| Auth | Supabase Auth |

---

## 🚀 Quickstart

Full, step-by-step instructions (accounts, keys, database, deploy) are in **[SETUP.md](./SETUP.md)**.

```bash
# Backend  (Python 3.12 recommended)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add GEMINI_API_KEY, GITHUB_TOKEN, DATABASE_URL, REDIS_URL
uvicorn app.main:app --reload  # → http://localhost:8000/docs

# Frontend  (second terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                    # → http://localhost:3000
```

---

## 🛡️ Safety & data handling

- **Keys server-side only.** No LLM/API keys in the frontend bundle. `.env` is git-ignored; `.env.example` holds placeholders.
- **Prompt-injection defense.** Repo content (READMEs, comments) is treated as untrusted; it is delimited and agents are instructed to ignore embedded instructions.
- **No arbitrary execution.** CodeAtlas analyzes code; it never runs untrusted code.
- **Cost caps & rate limits.** Hard per-session ceilings enforced in Redis.
- **Public repos only.** Gemini's free tier may use submitted data to improve Google's products — so CodeAtlas targets public code by design. Do not point it at private/proprietary code on a free-tier key.

---

## 🗺️ Roadmap

- [x] Multi-agent LangGraph orchestration (router → retriever → reviewers → critic)
- [x] Safety guardrails + cost-cap enforcement + smoke tests
- [x] Production frontend (chat, agent pipeline, findings, trace dashboard)
- [ ] Real ingest: GitHub fetch → chunk → embed into pgvector
- [ ] Live Gemini RAG chat with SSE streaming
- [ ] Structured agentic review with critic verification on real code
- [ ] Evals dashboard (retrieval relevance + review precision/recall)
- [ ] Human-in-the-loop "open a PR" via GitHub MCP
- [ ] Deploy (Vercel + Render/Railway)

---

## 📁 Project structure

```
backend/
  app/
    main.py            FastAPI entry (CORS, routers)
    config.py          Typed settings from environment
    api/routes.py      /ingest, /analyze
    agents/            state · graph · nodes (router, retriever, reviewers, critic)
    services/          llm.py (Gemini), github.py
    core/guardrails.py Prompt-injection defense, cost caps
  tests/               passing smoke tests (no keys/network needed)
frontend/
  app/                 layout, page, globals
  components/          Header, RepoInput, AgentPipeline, ChatPanel, FindingsPanel, TracePanel, ui/
  lib/                 api client, types, utils
```

---

<div align="center">

Built by **M. Sharjeel Saleem** — AI Product Engineer
[Portfolio](https://muhammad-sharjeel-portfolio.netlify.app/) · [GitHub](https://github.com/m-sharjeel-saleem)

</div>
