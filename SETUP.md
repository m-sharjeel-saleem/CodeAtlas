# CodeAtlas — Complete Setup Guide (Google Gemini)

Everything you need to do **from your side**, step by step, to run CodeAtlas locally and deploy it. Follow top to bottom. Total time ≈ 20–30 minutes.

---

## 0. Prerequisites

| Tool | Version | Check |
|---|---|---|
| Node.js | 18+ (20 LTS recommended) | `node -v` |
| Python | **3.11 or 3.12** (avoid 3.13/3.14 — some deps lack wheels) | `python3 --version` |
| Git | any | `git --version` |

> **pyenv users:** `pyenv install 3.12.7 && pyenv local 3.12.7` inside `backend/` before making the venv.

---

## 1. The five things you provide

| # | Secret | From | Goes in |
|---|---|---|---|
| 1 | `GEMINI_API_KEY` | Google AI Studio | `backend/.env` |
| 2 | `GITHUB_TOKEN` | GitHub settings | `backend/.env` |
| 3 | `DATABASE_URL` | Supabase | `backend/.env` |
| 4 | `REDIS_URL` | Upstash | `backend/.env` |
| 5 | `NEXT_PUBLIC_API_URL` | your backend URL | `frontend/.env.local` |

Do each below.

---

### 1️⃣ GEMINI_API_KEY — the LLM (free)

1. Go to **<https://aistudio.google.com/apikey>** and sign in with your Google account.
2. Click **“Create API key”**.
3. Choose **“Create API key in new project”** (or pick an existing Google Cloud project).
4. Copy the key — it starts with `AIza…`.
5. Paste it into `backend/.env` as `GEMINI_API_KEY=AIza…`.

> ⚠️ **Data privacy:** Gemini’s **free tier may use your prompts to improve Google’s products.** CodeAtlas only analyzes **public** repositories, so this is fine. **Never** point it at private or proprietary code on a free key. For private code, enable billing (paid tier is not used for training) or use approved infrastructure.

**Free limits** are generous for development (plenty of requests/day on Flash). You do not need to add billing to start.

---

### 2️⃣ GITHUB_TOKEN — read public repos (free)

Optional but recommended (raises GitHub’s rate limit from ~60 to ~5,000 requests/hour).

1. Go to **<https://github.com/settings/tokens>** → **“Generate new token”** → **“Generate new token (classic)”**.
2. Note: `CodeAtlas`. Expiration: your choice (90 days is fine).
3. Scope: tick **`public_repo`** only (under `repo`). Nothing else is needed.
4. Click **Generate token** and copy it (`ghp_…`).
5. Paste into `backend/.env` as `GITHUB_TOKEN=ghp_…`.

---

### 3️⃣ DATABASE_URL — Supabase Postgres + pgvector (free)

1. Go to **<https://supabase.com/>** → **New project**.
2. Name it `codeatlas`, set a **database password** (save it!), pick the nearest region, create.
3. Wait ~2 minutes for provisioning.
4. Get the connection string: **Project Settings (gear) → Database → Connection string → URI**.
   - It looks like `postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres`.
   - Replace `[YOUR-PASSWORD]` with the password from step 2.
5. Paste into `backend/.env` as `DATABASE_URL=postgresql://…`.
6. Enable the vector extension: in Supabase, open **SQL Editor → New query**, paste and **Run**:
   ```sql
   create extension if not exists vector;
   ```
   You should see “Success. No rows returned.” (The code-chunk table is created automatically in the ingest build step.)

---

### 4️⃣ REDIS_URL — Upstash (free)

1. Go to **<https://upstash.com/>** → sign up → **Create Database** (Redis).
2. Name `codeatlas`, pick a region near your backend, create.
3. On the database page, find **“Connect” → copy the `redis://` (or `rediss://`) URL** that includes the password.
4. Paste into `backend/.env` as `REDIS_URL=redis://…`.

> Prefer local? `brew install redis && redis-server`, then use `REDIS_URL=redis://localhost:6379/0`.

---

### 5️⃣ NEXT_PUBLIC_API_URL — frontend → backend link

- **Local:** `http://localhost:8000` (the default in `.env.local.example`).
- **Production:** the URL of your deployed backend (filled in during deploy, Step 4).

---

## 2. Run the backend

```bash
cd CodeAtlas/backend

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env               # then open .env and paste your 4 values
```

Your `backend/.env` should look like:
```ini
GEMINI_API_KEY=AIza...
GITHUB_TOKEN=ghp_...
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxx.supabase.co:5432/postgres
REDIS_URL=redis://default:...@xxxx.upstash.io:6379
MODEL_REASONING=gemini-2.5-pro
MODEL_FAST=gemini-2.5-flash
```

Start it:
```bash
uvicorn app.main:app --reload
```
- API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

Run tests anytime:
```bash
pytest -q
```

---

## 3. Run the frontend

In a **second terminal**:
```bash
cd CodeAtlas/frontend

npm install

cp .env.local.example .env.local   # default points at http://localhost:8000
npm run dev
```
Open <http://localhost:3000>. With both servers running, paste a repo (e.g. `facebook/react`), ask a question, and watch the agent pipeline run.

---

## 4. Deploy (when ready)

CodeAtlas runs as **two deploys**:

| Part | Host | How |
|---|---|---|
| Frontend (Next.js) | **Vercel** | Import repo → set **Root Directory = `frontend`** → add env `NEXT_PUBLIC_API_URL` = backend URL |
| Backend (FastAPI) | **Render** / **Railway** | New Web Service → **Root = `backend`** → Build `pip install -r requirements.txt` → Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT` → add all `backend/.env` values |
| Database | Supabase (already cloud) | reuse `DATABASE_URL` |
| Redis | Upstash (already cloud) | reuse `REDIS_URL` |

After the backend is live:
1. Set the frontend’s `NEXT_PUBLIC_API_URL` to the backend’s public URL and redeploy.
2. Add the frontend’s domain to `CORS_ORIGINS` in the backend env.

---

## 5. Cost control (built in)

- `SESSION_COST_CAP_USD` — hard ceiling per analysis session.
- `MAX_FILES_PER_REPO` — bounds how much of a repo is indexed.
- The trace dashboard shows real token + cost numbers per run.
- Keep `gemini-2.5-flash` as the default for most steps; reserve `gemini-2.5-pro` for the critic and architecture passes.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | You didn’t fill `backend/.env`, or you’re running from the wrong folder. |
| Frontend shows “Cannot reach the CodeAtlas API” | Backend isn’t running, or `NEXT_PUBLIC_API_URL` is wrong. |
| `pip install` fails on Python 3.13/3.14 | Use Python 3.12. |
| Supabase connection refused | Check the password substitution and that the project finished provisioning. |

> Never commit `.env` / `.env.local` — both are already git-ignored.
