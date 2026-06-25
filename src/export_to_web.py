import os
import json
import pandas as pd
import math

def safe_float(val):
    if pd.isna(val) or math.isnan(val):
        return 0.0
    return float(val)

def safe_int(val):
    if pd.isna(val) or math.isnan(val):
        return 0
    return int(val)

def main():
    print("Exporting Verified Phase 11 Results to Web Dashboard...")

    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    ablation_path = os.path.join(results_dir, 'phase11_ablation_metrics.csv')
    feat_imp_path = os.path.join(results_dir, 'phase11_feature_importance.csv')
    
    # 1. Read ablation metrics
    ablation_df = pd.read_csv(ablation_path)
    ablation_results = []
    baseline_data = {}
    final_data = {}

    for _, row in ablation_df.iterrows():
        config = row['configuration']
        entry = {
            "configuration": config,
            "num_features": safe_int(row['num_features']),
            "threshold_selected": safe_float(row['threshold_selected']),
            "num_test_alerts": safe_int(row['num_test_alerts']),
            "tp": safe_int(row['tp']),
            "fp": safe_int(row['fp']),
            "fn": safe_int(row['fn']),
            "precision": safe_float(row['precision']),
            "recall": safe_float(row['recall']),
            "f1": safe_float(row['f1']),
            "auprc": safe_float(row['auprc']),
            "test_support_malicious": safe_int(row['test_support_malicious'])
        }
        ablation_results.append(entry)
        
        if config == "A. Baseline Verified":
            baseline_data = {
                "name": config,
                "precision": entry['precision'],
                "recall": entry['recall'],
                "f1": entry['f1'],
                "auprc": entry['auprc'],
                "tp": entry['tp'],
                "fp": entry['fp'],
                "fn": entry['fn'],
                "threshold": entry['threshold_selected'],
                "num_features": entry['num_features']
            }
        elif config == "E. Full Phase 11":
            final_data = {
                "name": config,
                "precision": entry['precision'],
                "recall": entry['recall'],
                "f1": entry['f1'],
                "auprc": entry['auprc'],
                "tp": entry['tp'],
                "fp": entry['fp'],
                "fn": entry['fn'],
                "threshold": entry['threshold_selected'],
                "num_features": entry['num_features']
            }

    # 2. Read feature importance
    feat_imp_df = pd.read_csv(feat_imp_path)
    feature_importance = []
    for _, row in feat_imp_df.iterrows():
        feature_importance.append({
            "feature": row['feature'],
            "importance": safe_float(row['importance'])
        })

    # 3. Build target JSON structure
    payload = {
      "project_title": "Cyber DNA: Leakage-Free Behavioral Authentication on CMU CERT r4.2",
      "dataset": {
        "name": "CMU CERT r4.2",
        "train_split": "Weeks 1-52",
        "test_split": "Weeks 53-72",
        "evaluation_protocol": "Strict chronological leakage-free split",
        "test_support_malicious": 82
      },
      "final_summary": {
        "best_configuration": final_data['name'],
        "final_f1": final_data['f1'],
        "final_precision": final_data['precision'],
        "final_recall": final_data['recall'],
        "final_auprc": final_data['auprc'],
        "threshold": final_data['threshold'],
        "tp": final_data['tp'],
        "fp": final_data['fp'],
        "fn": final_data['fn'],
        "num_features": final_data['num_features']
      },
      "baseline_vs_final": {
        "baseline": baseline_data,
        "final": final_data
      },
      "ablation_results": ablation_results,
      "feature_importance": feature_importance,
      "key_findings": [
        "Full Phase 11 was the best-performing configuration, improving F1 from 44.44% to 48.41% and recall from 34.15% to 46.34%.",
        "The improvement came from richer behavioral context, especially when USB, off-hours, email-intensity, and baseline temporal features were combined.",
        "USB and off-hours features alone mainly improved ranking/precision behavior, but did not independently maximize recall.",
        "Workstation diversity features underperformed in isolation and likely introduced noise in CERT due to benign multi-machine usage patterns.",
        "The final operating threshold shifted to 0.30, indicating that the richer feature space benefited from a more recall-oriented decision boundary.",
        "The evaluation remained strictly leakage-free, preserving chronological splitting and train-only threshold tuning."
      ],
      "final_model_details": {
        "name": "E. Full Phase 11",
        "feature_blocks": [
          "Baseline behavioral features",
          "USB features",
          "Workstation diversity features",
          "Off-hours behavior features",
          "Email-intensity features",
          "BDS / IDP / BC / SRC mathematical features"
        ],
        "threshold_strategy": "5-fold Stratified CV on training partition only",
        "selected_threshold": 0.30,
        "why_selected": "Maximized F1 on train-only validation folds",
        "leakage_free": True
      },
      "research_notes": {
        "main_conclusion": "Leakage-free Phase 11 feature expansion improved overall insider-threat detection quality on CERT r4.2.",
        "precision_recall_tradeoff": "Full Phase 11 increased false positives relative to the baseline, but captured 10 additional malicious weeks and improved F1/AUPRC.",
        "weak_block": "Workstation diversity features were noisy in isolation.",
        "final_recommendation": "Freeze the project on the verified Full Phase 11 model for final presentation and report submission."
      }
    }

    output_path = os.path.join(os.path.dirname(__file__), '..', 'web_app', 'src', 'cyber_dna_data.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

    print(f"Exported successfully to {output_path}")

if __name__ == '__main__':
    main()
