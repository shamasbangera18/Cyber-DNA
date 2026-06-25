# Cyber DNA

Cyber DNA is a continuous behavioral authentication and insider threat detection framework. It addresses the limitations of standard point-in-time perimeter defenses by building longitudinal models of user behavior using enterprise logs.

This repository contains the verified Phase 11 expanded model and the visualization dashboard.

## Final Verified Results

* **Final model** = Full Phase 11
* **Final metrics** = 48.41% F1 / 46.34% Recall / 50.67% Precision / 0.4490 AUPRC
* **Ground truth** = CERT r4.2 `insiders.csv`
* **Chronological split** = Weeks 1–52 train, Weeks 53–72 test

All experiments and evaluations are executed without temporal data leakage. The `MinMaxScaler` normalization and threshold selection are strictly restricted to the training subset.

## Repository Structure
* `cyber_dna_phase11_ablation.py` - The main, final leakage-free execution script.
* `src/export_to_web.py` - Connects the ML outputs to the React dashboard.
* `web_app/` - The React Dashboard source code.
* `results/` - Final CSV/JSON metrics and findings.
* `final_project_report.md` - The comprehensive final academic report.
* `data/` - Put the CMU CERT r4.2 `r4.2.tar.bz2` extracted contents here.
* `legacy_archive/` - Old prototype scripts and historical outputs.

## Reproducing the Project

### 1. Prerequisites
You must download the CMU CERT r4.2 dataset and extract it into `data/cert_r4.2/r4.2`. Also ensure `answers/insiders.csv` is present in `data/cert_r4.2/answers`.

### 2. Final Execution Order
To reproduce the entire pipeline from scratch, follow these three steps exactly:

**1. Run the ML Pipeline**
```bash
python cyber_dna_phase11_ablation.py
```
*This extracts features, runs the chronological ML evaluation, and dumps the results to the `results/` folder.*

**2. Export the Data**
```bash
python src/export_to_web.py
```
*This converts the final CSV metrics into the `cyber_dna_data.json` file for the frontend.*

**3. Run Dashboard from `web_app/`**
```bash
cd web_app
npm install
npm run dev
```
*This launches the React dashboard visualizing the final results.*
