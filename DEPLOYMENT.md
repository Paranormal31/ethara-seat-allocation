# Ethara Deployment Guide
## Render (Backend) + Vercel (Frontend)

---

## Prerequisites
- GitHub account with this repo pushed
- Render account: https://render.com
- Vercel account: https://vercel.com

---

## Step 1 — Push to GitHub

```bash
git init                        # if not already a git repo
git add .
git commit -m "ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/ethara.git
git push -u origin main
```

---

## Step 2 — Deploy Backend on Render

### 2a. Create PostgreSQL Database
1. Go to https://dashboard.render.com
2. Click **New** ? **PostgreSQL**
3. Name: ethara-postgres
4. Plan: **Free**
5. Region: Singapore (or nearest to you)
6. Click **Create Database**
7. Copy the **Internal Database URL** (shown after creation)

### 2b. Create Web Service
1. Click **New** ? **Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Name**: ethara-backend
   - **Root Directory**: *(leave blank — Dockerfile is at root)*
   - **Runtime**: **Docker**
   - **Dockerfile Path**: ./Dockerfile
   - **Plan**: Free
4. Under **Environment Variables**, add:
   | Key | Value |
   |-----|-------|
   | DATABASE_URL | *(paste the Internal DB URL from Step 2a)* |
   | ALLOWED_ORIGINS | *(leave blank for now — fill after Vercel step)* |
5. Click **Create Web Service**

> **First deploy takes 5-10 minutes** — the seed script runs and inserts 5,000+ records.

6. Copy your Render backend URL: https://ethara-backend.onrender.com

---

## Step 3 — Deploy Frontend on Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Set **Root Directory** to: rontend
4. Framework Preset: **Vite** (auto-detected)
5. Under **Environment Variables**, add:
   | Key | Value |
   |-----|-------|
   | VITE_API_URL | https://ethara-backend.onrender.com |
6. Click **Deploy**

> Vercel will run 
pm run build and deploy the static site to a CDN.

7. Copy your Vercel URL: https://ethara.vercel.app

---

## Step 4 — Connect Frontend ? Backend (CORS)

1. Go back to Render ? your backend service ? **Environment**
2. Set ALLOWED_ORIGINS = https://ethara.vercel.app
3. Click **Save Changes** ? Render will auto-redeploy

---

## Step 5 — Verify

- Open https://ethara.vercel.app
- Dashboard should load with real data from Render PostgreSQL
- Test seat allocation, AI chatbot, reservations

---

## Local Development (unchanged)

```bash
docker-compose up --build    # uses Dockerfile.local — bundles everything
```

Open http://localhost:8001

---

## Architecture Summary

```
GitHub (source of truth)
    |
    +-- Render (Backend + PostgreSQL)
    |   URL: https://ethara-backend.onrender.com
    |   - FastAPI / Uvicorn
    |   - Auto-seeds 5,000 employees on first boot
    |   - Managed PostgreSQL (persistent)
    |
    +-- Vercel (Frontend)
        URL: https://ethara.vercel.app
        - React + Vite (static CDN)
        - Calls Render API via VITE_API_URL
```

## Free Tier Limitations

| Service | Limitation |
|---------|-----------|
| Render Web (free) | Spins down after 15 min inactivity. First request takes ~30s to cold start. |
| Render PostgreSQL (free) | 1 GB storage, expires after 90 days. Upgrade for production. |
| Vercel (hobby) | Unlimited for personal projects. |

> **Tip**: To avoid cold starts on Render free tier, use a cron job or UptimeRobot to ping /api/health every 10 minutes.
