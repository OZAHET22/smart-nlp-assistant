# Vercel Deployment & Multi-Device Responsive Guide — Smart NLP Assistant

This guide provides end-to-end instructions for deploying the **Smart Reading & Writing Assistant (Enterprise NLP Studio)** to **Vercel** with full multi-device responsiveness across smartphones, tablets, laptops, desktops, and ultra-wide displays.

---

## 📱 1. Multi-Device Responsive Architecture

The entire UI/UX has been engineered according to modern responsive web standards:

| Device Category | Screen Resolution | UI/UX Optimizations |
|-----------------|-------------------|---------------------|
| **Small Smartphones** | 320px – 480px (iPhone SE, Galaxy S, Pixel) | Compact header, adaptive `⚡ Edge` toggle chip, mobile view switcher (`[Split]` / `[Input]` / `[Output]`), mobile stage dropdown selector, fluid 2-column metrics cards, horizontal swipe hints with touch inertia. |
| **Standard Phablets** | 480px – 768px (iPhone 14/15/16 Pro Max, Pixel Fold) | Responsive tab bar with touch momentum, fluid typography `clamp()`, clean flex-wrapping for action toolbars. |
| **Tablets & iPads** | 768px – 1024px (iPad Air, iPad Pro, Galaxy Tab) | Side-by-side or stacked editor layouts, interactive Levenshtein matrix with dynamic scaling, full sentence CYK parse trees. |
| **Laptops & Desktops** | 1024px – 1440px | Full dual-pane side-by-side live diff editor, comprehensive 11-column benchmark studio table, SRL semantic frame flow diagrams. |
| **Ultra-Wide & 4K** | > 1440px (1920px, 2560px+) | Contained max-width container (1600px) with centered ambient glow, zero distortion or text-stretch. |
| **Print / PDF Export** | Any device (`window.print()`) | High-contrast black & white ink-friendly stylesheet (`@media print`), hides navigation and buttons, page-break optimized. |

---

## 🚀 2. Instant One-Click Vercel Deployment

### Step A: Commit & Push to GitHub
From the repository root (`smart_assistant`):

```bash
git add .
git commit -m "feat(ui): complete all-device responsive UI/UX and Vercel edge deployment optimization"
git push origin master
```

### Step B: Connect to Vercel
1. Log in to your [Vercel Dashboard](https://vercel.com).
2. Click **"Add New..."** → **"Project"**.
3. Import your GitHub repository: `OZAHET22/smart-nlp-assistant`.
4. Vercel automatically detects the preset from `vercel.json` and `package.json`:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `./` (or `smart_assistant` if deploying from the parent directory)
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`
5. Click **"Deploy"**.
6. Within ~45 seconds, your application will be live at:
   `https://smart-nlp-assistant.vercel.app` (or your assigned Vercel URL).

---

## ⚡ 3. Deployment via Vercel CLI (Alternative)

Deploy directly from your terminal:

```bash
# 1. Install Vercel CLI globally
npm i -g vercel

# 2. Login
vercel login

# 3. Deploy to preview
vercel

# 4. Deploy to production
vercel --prod
```

---

## 🧠 4. Dual-Engine Architecture Explained

### Engine 1: Native Vercel Edge / Serverless Engine (Default)
- **Zero cold starts (<15ms latency)**.
- **Zero Python dependency headaches** (no spaCy/NLTK unzipped size limit issues on Vercel's serverless limit).
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

## 🧪 5. Verifying on All Devices

Once deployed, verify on your live Vercel domain:
- **Web App:** `https://<your-app>.vercel.app/`
- **Mobile Check:** Open on iOS Safari or Android Chrome — verify the compact header, mobile stage dropdown, and responsive editor tabs (`[Split]`, `[Input]`, `[Output]`).
- **Full Pipeline API:** `POST https://<your-app>.vercel.app/api/process`
- **Levenshtein Matrix API:** `POST https://<your-app>.vercel.app/api/levenshtein-matrix`
- **Automated Benchmark API:** `GET https://<your-app>.vercel.app/api/benchmark`
