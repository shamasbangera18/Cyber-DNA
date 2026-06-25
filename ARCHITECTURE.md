# Cyber DNA System Architecture

This document describes the complete end-to-end data flow and the engineering techniques used within the Cyber DNA system.

---

## 1. Full System Data Flow

```text
CERT r4.2 Raw Logs
  (logon.csv, email.csv, device.csv)
          │
          ▼
┌─────────────────────────────────────┐
│  cyber_dna_phase11_ablation.py      │
│                                     │
│  • Categorical memory mapping       │
│  • C-level vectorized feature eng.  │
│  • Chronological train/test split   │
│    (Weeks 1-52 Train / 53-72 Test)  │
│  • XGBoost + 5-fold CV threshold    │
│  • Ablation study (5 configs)       │
└─────────────────────────────────────┘
          │
          ▼ writes to results/
  phase11_ablation_metrics.csv
  phase11_feature_importance.csv
  phase11_run_summary.json
          │
          ▼
┌─────────────────────────────────────┐
│  src/export_to_web.py               │
│                                     │
│  • Reads results CSVs & JSON        │
│  • Builds a single dashboard JSON   │
└─────────────────────────────────────┘
          │
          ▼
  web_app/src/cyber_dna_data.json
          │
          ▼
┌─────────────────────────────────────┐
│  React Dashboard (web_app/)         │
│                                     │
│  • Overview tab                     │
│  • Ablation Study tab               │
│  • Feature Importance tab           │
│  • Research Results tab             │
└─────────────────────────────────────┘
```

---

## 2. Memory Optimization: Categorical Mapping

Processing millions of rows of string-heavy logs (like `user`, `pc`, `activity`, `department`, `role`) natively as standard Python objects results in massive memory inflation.

To combat this, `cyber_dna_phase11_ablation.py` uses **8-bit and 16-bit Categorical Memory Mapping**.

### How it works
- When `email.csv`, `device.csv`, and `logon.csv` are ingested, all repeating alphanumeric fields are cast to `category` types immediately on load.
- Instead of storing the string `"Sales Manager"` 10,000 times, Pandas stores it once in an underlying lookup table and replaces the 10,000 rows with tiny integer pointers (e.g., `0`, `1`, `2`).
- **Impact:** The memory footprint of the 2.6 million-row `email.csv` drops from roughly 4.8 GB (in pure object format) to under 880 MB.

---

## 3. Processing Speed: C-Level Vectorization

A common mistake in ML data engineering is relying on Python `for-loops` or `.iterrows()` to calculate historical features. These methods run at standard Python bytecode speeds and are computationally devastating for large time-series datasets.

`cyber_dna_phase11_ablation.py` enforces strict **C-level Pandas Vectorization**.

### How it works
- **Grouped Shifts:** Chronological behavioral sequences (BDS, IDP, BC, SRC) are computed using `df.groupby('user').shift(N)`, which is pushed down to C/Cython loops natively embedded within Pandas.
- **Rolling Windows:** Weekly activity thresholds use vectorized `.rolling()` and `.sum()` instead of manual iteration.
- **Impact:** Full feature engineering across 72 weeks for 1,000 users completes in under 3 minutes.

---

## 4. Decoupled Export Architecture

Rather than building a Flask or Django backend to serve XGBoost models live, Cyber DNA uses a **Deterministic Static Export** strategy.

### How it works
- Once the Phase 11 ablation study concludes, `src/export_to_web.py` reads the `results/` CSVs and JSON files and writes a single `cyber_dna_data.json` payload into `web_app/src/`.
- The React frontend consumes only this static JSON file.
- **Impact:** The dashboard can be hosted as a pure HTML/JS static bundle with zero server cost, massive scalability, and zero risk of live-model manipulation. The ML pipeline and the presentation layer are completely independent.
