# CodeAtlas — Complete Setup Guide

Everything you need to do **from your side** to run CodeAtlas locally and deploy it. Follow top to bottom.

---

## 0. Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Node.js | 18+ (20 LTS recommended) | for the frontend |
| Python | **3.11 or 3.12** | 3.13/3.14 may lack wheels for some pinned deps — use 3.12 to be safe |
| Git | any | |

Check:
```bash
node -v
python3 --version
```

---

## 1. Accounts & keys to create (≈15 min)

You need four things. All have free tiers.

### 1a. Anthropic API key (the LLM)
1. Go to <https://console.anthropic.com/> → sign up.
2. **Billing** → add a small amount of credit (≈ $5 is plenty for testing).
3. **API Keys** → *Create key* → copy it (starts with `sk-ant-`).

### 1b. GitHub personal access token (read public repos)
1. <https://github.com/settings/tokens> → *Generate new token (classic)*.
2. Scope: **`public_repo`** is enough. Copy it (`ghp_…`).
   *(Optional — without it CodeAtlas still works but hits GitHub's lower anonymous rate limit.)*

### 1c. Supabase project (Postgres + pgvector)
1. <https://supabase.com/> → *New project*. Pick a region near you; save the DB password.
2. Once created: **Project Settings → Database → Connection string → URI**. Copy it — that's your `DATABASE_URL`.
3. Enable the vector extension: **SQL Editor → New query**, run:
   ```sql
   create extension if not exists vector;
   ```
   *(The table schema for code chunks gets added in the "real ingest" build step.)*

### 1d. Redis (queue + cost counters)
Easiest is **Upstash** (free, serverless):
1. <https://upstash.com/> → *Create database* → copy the **Redis URL** (`redis://…` or `rediss://…`).

*Or* run Redis locally: `brew install redis && redis-server` → `redis://localhost:6379/0`.

---

## 2. Backend setup

```bash
cd CodeAtlas/backend

# Use Python 3.12 if you have it (pyenv users: `pyenv local 3.12`)
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Open `.env` and fill in the four values from Step 1:
```ini
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxx.supabase.co:5432/postgres
REDIS_URL=redis://default:...@xxxx.upstash.io:6379
```

Run it:
```bash
uvicorn app.main:app --reload
```
- API docs: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

Run the tests anytime:
```bash
pytest -q
```

---

## 3. Frontend setup

In a **second terminal**:
```bash
cd CodeAtlas/frontend

npm install

cp .env.local.example .env.local   # default points at http://localhost:8000
npm run dev
```
Open <http://localhost:3000>. With both servers running, paste a repo (e.g. `facebook/react`), ask a question, and watch the agent pipeline run.

---

## 4. Deployment (when ready)

CodeAtlas runs as **two deploys**:

| Part | Recommended host | How |
|---|---|---|
| Frontend (Next.js) | **Vercel** | Import the repo, set root dir to `frontend/`, add env `NEXT_PUBLIC_API_URL` = your backend URL |
| Backend (FastAPI) | **Render** or **Railway** | New web service, root `backend/`, start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, add the same `.env` values |
| Database | Supabase (already cloud) | reuse your `DATABASE_URL` |
| Redis | Upstash (already cloud) | reuse your `REDIS_URL` |

After the backend is live, set the frontend's `NEXT_PUBLIC_API_URL` to the backend URL and add the backend's domain to `CORS_ORIGINS` in the backend env.

> **Data note:** this is a public-repo demo, so these hosts are fine. If you ever point CodeAtlas at private or proprietary code, the data-handling and hosting requirements change — keep that for company-approved infrastructure.

---

## 5. Cost control (already built in)

- `SESSION_COST_CAP_USD` in the backend `.env` caps spend per analysis session.
- `MAX_FILES_PER_REPO` bounds how much of a repo gets indexed.
- The trace panel shows real token + cost numbers per run, so nothing is a surprise.

Keep models cheap during development by leaving `MODEL_FAST=claude-sonnet-4-6` as the default for most steps; reserve `MODEL_REASONING=claude-opus-4-8` for the critic and architecture passes.

---

## Quick reference — what you provide

| Secret | Where it goes | From |
|---|---|---|
| `ANTHROPIC_API_KEY` | `backend/.env` | console.anthropic.com |
| `GITHUB_TOKEN` | `backend/.env` | github.com/settings/tokens |
| `DATABASE_URL` | `backend/.env` | Supabase → Database → Connection string |
| `REDIS_URL` | `backend/.env` | Upstash |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | your backend URL |

Never commit `.env` / `.env.local` — both are already git-ignored.
