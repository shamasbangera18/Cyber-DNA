# Deployment Guide

The Cyber DNA system has two independent parts: a **Python ML pipeline** and a **React dashboard**. This guide explains how to run both.

---

## Step 1 — Run the Phase 11 Ablation Pipeline

This generates all model metrics, feature importance, and results CSVs.

1. Install Python dependencies (only needed once):
   ```bash
   pip install -r requirements.txt
   ```
2. Place the raw CERT r4.2 data files (`logon.csv`, `email.csv`, `device.csv`) in the `data/` directory.
3. Run the pipeline:
   ```bash
   python cyber_dna_phase11_ablation.py
   ```
4. Output will be written to the `results/` directory:
   - `phase11_ablation_metrics.csv`
   - `phase11_feature_importance.csv`
   - `phase11_run_summary.json`
   - `phase11_findings.md`

---

## Step 2 — Export Results to Dashboard JSON

This converts the `results/` CSVs into the single JSON payload the React dashboard reads.

```bash
python src/export_to_web.py
```

This writes `web_app/src/cyber_dna_data.json`. The React dashboard will not load correctly without this file.

---

## Step 3 — Run or Build the React Dashboard

### Option A: Local Development

1. Navigate to the `web_app` directory:
   ```bash
   cd web_app
   ```
2. Install dependencies (only needed once):
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:5173/` in your browser.

### Option B: Build for Production

Compile the React app into an optimized static bundle for hosting:

```bash
cd web_app
npm run build
```

Vite will generate a `dist/` folder. This folder is all you need to deploy.

> [!IMPORTANT]
> The `dist/` folder must include `cyber_dna_data.json` (copied into it during the build). Verify this file is present before deploying.

---

## Step 4 — Deploy to a Hosting Provider (Optional)

Because the dashboard compiles to static files, you can host it for free on any modern provider.

### Vercel (Recommended)
1. Create a free account at [vercel.com](https://vercel.com).
2. Connect your GitHub repository or use the CLI:
   ```bash
   npm i -g vercel
   cd web_app
   vercel
   ```
3. Vercel auto-detects Vite and provides a live URL after deploy.

### Netlify
1. Create a free account at [netlify.com](https://netlify.com).
2. Drag and drop your `dist/` folder into the Netlify UI, or connect your GitHub repository with Build Command `npm run build` and Publish Directory `dist`.

### GitHub Pages
1. Install the `gh-pages` package:
   ```bash
   npm install gh-pages --save-dev
   ```
2. Add to `package.json`:
   ```json
   "homepage": "https://<username>.github.io/<repo-name>",
   "scripts": { "deploy": "gh-pages -d dist" }
   ```
3. Deploy:
   ```bash
   npm run build
   npm run deploy
   ```
