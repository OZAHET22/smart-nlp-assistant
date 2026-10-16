# Vercel Deployment Guide — Smart NLP Assistant (Next.js Edition)

This guide provides step-by-step instructions for deploying the **Smart Reading & Writing Assistant (Enterprise NLP Studio)** to **Vercel** with zero-configuration.

---

## 🚀 1. One-Click / Dashboard Deployment

### Step A: Push to GitHub
If you haven't already committed and pushed the latest Next.js updates:

```bash
git add .
git commit -m "feat: upgrade frontend to Next.js 14 App Router, Vercel-ready NLP Studio"
git push origin master
```

### Step B: Connect to Vercel
1. Log in to [Vercel](https://vercel.com).
2. Click **"Add New..."** → **"Project"**.
3. Import your repository: `OZAHET22/smart-nlp-assistant`.
4. Vercel automatically detects **Next.js** from `package.json` and `vercel.json`:
   - **Framework Preset:** `Next.js`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`
5. Click **"Deploy"**.
6. Within ~60 seconds, your application will be live at:
   `https://smart-nlp-assistant.vercel.app` (or your assigned Vercel URL).

---

## ⚡ 2. Deployment via Vercel CLI (Alternative)

If you prefer deploying directly from your terminal:

```bash
# 1. Install Vercel CLI globally
npm i -g vercel

# 2. Login to your Vercel account
vercel login

# 3. Deploy to preview
vercel

# 4. Deploy to production
vercel --prod
```

---

## 🧠 3. Dual-Engine Architecture Explained

### Engine 1: Native Vercel Edge / Serverless Engine (Default)
- **Zero cold starts (<15ms latency)**.
- **Zero Python dependency headaches** (no spaCy/NLTK unzipped size limit issues on Vercel's 250MB serverless limit).
- Built-in TypeScript implementation of all 5 stages:
  1. **Stage 1 (Spelling):** Levenshtein distance matrix + Brown bigram context disambiguation.
  2. **Stage 2 (Syntax):** Token POS tagging + dependency parsing + 15-rule CYK chart parser.
  3. **Stage 3 (Semantics):** Named Entity Recognition + SRL frames (Agent/Action/Patient) + Lesk Word Sense Disambiguation.
  4. **Stage 4 (Discourse):** Coreference resolution chains + discourse connective classifier + indirect speech act detection.
  5. **Stage 5 (Assembly):** Continuous pipeline wiring + readability metrics + export generator.

### Engine 2: Optional Python Backend Delegation
If you deploy your Python backend (e.g., on Render, Railway, Fly.io, or AWS) or run it locally:
1. Add an Environment Variable in Vercel:
   - **Name:** `PYTHON_BACKEND_URL`
   - **Value:** `https://your-python-api.onrender.com`
2. The `/api/process` endpoint will automatically proxy requests to the Python backend when requested, while gracefully falling back to the native engine if the backend is unavailable.

---

## 🧪 4. Verifying the Deployment

Once deployed, test the following endpoints on your live Vercel domain:
- **Web App:** `https://<your-app>.vercel.app/`
- **Samples API:** `https://<your-app>.vercel.app/api/samples`
- **Full Pipeline API:** `POST https://<your-app>.vercel.app/api/process` with JSON `{ "text": "hey prof..." }`
- **Levenshtein Matrix API:** `POST https://<your-app>.vercel.app/api/levenshtein-matrix`
- **Automated Benchmark API:** `GET https://<your-app>.vercel.app/api/benchmark`
