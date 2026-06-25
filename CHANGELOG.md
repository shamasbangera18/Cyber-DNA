# Changelog

All notable changes to the Cyber DNA project are documented here.

---

## [Phase 11 — Final Frozen Model] — 2026-06

### Added
- **Leakage-Free Chronological Protocol:** Enforced strict Train (Weeks 1–52) / Test (Weeks 53–72) partitions, eliminating all forms of temporal data leakage.
- **Automated Ablation Grid:** XGBoost feature ablation study comparing 5 configurations — Verified Baseline, +USB, +Workstation Diversity, +Off-Hours, and the full Expanded Cyber DNA Model.
- **Static Export Bridge:** `src/export_to_web.py` deterministically converts `results/` CSVs and JSON into a single `cyber_dna_data.json` payload consumed by the React dashboard.
- **Modular React Dashboard:** Built with Vite + Tailwind CSS v4 + Recharts, refactored into a modular component architecture (`/components`, `/views`). Four tabs: **Overview**, **Ablation Study**, **Feature Importance**, **Research Results**.

### Changed
- **Memory Optimization:** Replaced string object fields with 8-bit Pandas categorical mapping, compressing 1.5GB of raw logs to under 900 MB in-memory.
- **Vectorized Preprocessing:** Replaced all iterative loops with Cython-backed Pandas `.groupby().shift()` commands for leakage-safe chronological feature construction.
- **Evaluation Metrics:** Migrated from random-split accuracy to imbalance-robust metrics — F1-Score, AUPRC, Precision, Recall — as primary evaluation criteria.

### Removed
- All legacy multi-script pipeline references (`data_loader.py`, `ml_engine.py`, `run_pipeline.py`) replaced by the single consolidated `cyber_dna_phase11_ablation.py`.
- Old prototype tab structure (Cyber Anthropology, Temporal Drift, BSI Heatmap, Research & Sweeps) replaced by the final 4-tab dashboard.

---

## [Phases 1–10 — Prototyping] — Archived

### Notes
- Initial data exploration of CMU CERT r4.2.
- Preliminary experiments with SVM, Random Forests, and Isolation Forests — now used strictly as benchmark baselines to demonstrate XGBoost superiority.
- Development of the initial JSON export concept later formalized in `src/export_to_web.py`.
