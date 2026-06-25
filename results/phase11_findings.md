# Phase 11 Empirical Findings

## Ablation Study Results

We conducted a strict, chronological, leakage-free ablation study using the confirmed CMU CERT r4.2 ground truth (`insiders.csv`) on a 52-week train / 20-week test split. The malicious class support in the test set was exactly 82 weeks across all runs.

The goal was to measure the marginal gain of new behavioral feature blocks (USB, Workstation Diversity, Off-Hours, Email Intensity) when added to the validated baseline model.

### Summary Metrics Table

| Configuration | Threshold | Precision | Recall | F1 | AUPRC | TP | FP | FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Baseline Verified** | 0.50 | 63.64% | 34.15% | 44.44% | 0.4059 | 28 | 16 | 54 |
| **Baseline Tuned** | 0.50 | 63.64% | 34.15% | 44.44% | 0.4059 | 28 | 16 | 54 |
| **B. Baseline + USB** | 0.50 | 65.85% | 32.93% | 43.90% | 0.4168 | 27 | 14 | 55 |
| **C. Baseline + Workstation Diversity** | 0.65 | 58.33% | 25.61% | 35.59% | 0.3578 | 21 | 15 | 61 |
| **D. Baseline + Off-Hours** | 0.55 | 66.67% | 31.71% | 42.98% | 0.4151 | 26 | 13 | 56 |
| **E. Full Phase 11** | 0.30 | 50.67% | 46.34% | 48.41% | 0.4490 | 38 | 37 | 44 |

## Key Findings

### 1. The Best Configuration: Full Phase 11
The `E. Full Phase 11` configuration clearly outperformed the baseline in overall recall, F1, and AUPRC. 
*   **Improvement**: It improved Recall from **34.15% to 46.34%** (catching 10 more malicious weeks) and improved overall F1 from **44.44% to 48.41%**. AUPRC rose from 0.4059 to **0.4490**.
*   **Trade-off**: This configuration's optimal F1 threshold via train cross-validation was tuned down to `0.30`, increasing false positives from 16 to 37, which dropped precision from 63.6% to 50.7%. However, mathematically and operationally, capturing 35% more true positive weeks for a modest rise in alerts represents a much stronger pipeline.

### 2. Impact of Individual Blocks
*   **USB Features**: Did not materially improve recall (it actually dropped by one TP), but it provided a slight precision and AUPRC boost, suggesting the model found USB features helpful for filtering out a few false positives.
*   **Off-Hours Features**: Similar to USB, adding off-hours features independently tightened precision slightly (66.67%) but missed 2 additional true positives.
*   **Workstation Diversity**: Adding chronological `new_pc_count` and `pc_switch_count` strictly hurt performance. Precision, recall, and AUPRC all degraded significantly. The cross-validation naturally forced a higher threshold (0.65) to compensate for noise introduced by this block. 

### 3. Threshold Tuning Observations
The train-data-only tuning approach found that for the baseline, the optimal threshold on training validation folds happened to perfectly align with `0.50`. However, when adding the high-dimensionality Phase 11 feature block, the model's confidence distribution shifted. The tuning process cleanly identified that lowering the threshold to `0.30` maximized the F1 score, which translated to the highest test-set F1 observed in the project so far without leakage.
