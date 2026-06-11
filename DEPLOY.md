# Deploy CodeAtlas — 100% Free

Two free deploys: **backend → Render**, **frontend → Vercel**. Plus your existing free Supabase, Gemini, and (optional) Upstash. ~15 minutes.

```
Browser (Vercel, Next.js)  ──HTTPS──>  Render (FastAPI)  ──>  Supabase (pgvector) · Gemini · Upstash
```

---

## ⚠️ One required change first: Supabase pooler URL

Hosted platforms reach Supabase over IPv4, but the direct `db.xxx.supabase.co:5432` host is IPv6-only. Use the **Session Pooler** string for the deployed `DATABASE_URL`:

1. Supabase → **Project Settings → Database → Connection string → Session pooler**.
2. Copy the URI (looks like `postgresql://postgres.<ref>:[PASSWORD]@aws-0-<region>.pooler.supabase.com:5432/postgres`).
3. Substitute your password (URL-encode special characters, e.g. `@` → `%40`).
4. Use this as `DATABASE_URL` in Render below.

---

## 1. Backend → Render (free)

1. Go to **https://render.com** → sign up with GitHub.
2. **New + → Blueprint** → pick the `m-sharjeel-saleem/CodeAtlas` repo → Render reads `render.yaml` automatically.
3. It creates the `codeatlas-api` web service. Click in and add the secret env vars (the blueprint marks them as required):
   | Key | Value |
   |---|---|
   | `GEMINI_API_KEY` | your `AQ…`/`AIza…` key |
   | `GITHUB_TOKEN` | your `ghp_…` token |
   | `DATABASE_URL` | the **pooler** URI from above |
   | `REDIS_URL` | your Upstash `rediss://…` (or leave blank — cache degrades gracefully) |
   | `CORS_ORIGINS` | leave as `http://localhost:3000` for now; update after step 2 |
4. **Create** → wait for the build. When live, your API is at `https://codeatlas-api.onrender.com` (copy this).
5. Verify: open `https://codeatlas-api.onrender.com/health` → `{"status":"ok"}`.

> **Free-tier note:** the service sleeps after 15 min idle, so the *first* request after a nap takes ~50s to wake. Fine for a portfolio demo. (Optional: a free cron-ping every 10 min keeps it warm.)

---

## 2. Frontend → Vercel (free)

1. Go to **https://vercel.com** → sign up with GitHub → **Add New → Project** → import `CodeAtlas`.
2. **Root Directory:** click *Edit* → select **`frontend`**.
3. Framework preset auto-detects **Next.js**. Leave build settings default.
4. **Environment Variables** → add:
   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://codeatlas-api.onrender.com` (your Render URL) |
5. **Deploy.** You get a URL like `https://code-atlas.vercel.app`.

---

## 3. Connect the two (CORS)

1. Back in **Render → codeatlas-api → Environment**, set:
   `CORS_ORIGINS = https://code-atlas.vercel.app` (your Vercel URL; add `,http://localhost:3000` to keep local working).
2. Save → Render redeploys.

Done. Open your Vercel URL, enter a small repo (e.g. `octocat/Spoon-Knife`), ask a question — it indexes, then answers from the real code.

---

## 4. Add the live link to your portfolio

In `new-portfolio/src/data/portfolio.ts`, set the CodeAtlas entry's `liveUrl` to your Vercel URL, then commit + push. Now it shows a **“View Live Site”** button instead of just code.

---

## Free-tier guardrails (already configured)

- `MAX_FILES_PER_REPO=150` on Render so ingest fits in 512MB RAM. Keep demo repos small.
- `SESSION_COST_CAP_USD=1.00` caps spend per analysis.
- Gemini free tier covers demo traffic; Upstash/Supabase free tiers are ample.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Frontend: “Cannot reach the CodeAtlas API” | Render asleep (wait ~50s) or `NEXT_PUBLIC_API_URL` wrong |
| CORS error in browser console | `CORS_ORIGINS` on Render must include your exact Vercel URL |
| DB connection fails on Render | You must use the **Session Pooler** URL, not the direct `db.xxx:5432` one |
| Build fails on Render | Confirm `PYTHON_VERSION=3.12.7` (set in the blueprint) |
