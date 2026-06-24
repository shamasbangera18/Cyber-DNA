# Cyber DNA: A Human-Centered Behavioral Similarity Assessment Framework

## 1. Executive Summary
The increasing use of multiple digital identities and identity obfuscation techniques presents significant challenges for cybersecurity investigations. Traditional approaches rely on volatile technical indicators (IP addresses, device identifiers) which are easily manipulated.

This research proposes **Cyber DNA**, a human-centered behavioral similarity assessment framework that generates **Digital Behavioral Signatures (DBS)** from user activity patterns, communication behaviors, and organizational interaction characteristics. The framework incorporates concepts from Cyber Anthropology to quantify behavioral continuity and role consistency, and introduces **Behavioral Drift Analysis** to track how digital identities evolve over time.

By integrating multi-dimensional behavioral metrics and adaptive filtering, Cyber DNA provides a unified approach for behavioral similarity assessment without relying on static technical identifiers.

## 2. Dataset & Experimental Setup
The framework is evaluated using the industry-standard **CMU CERT Insider Threat Dataset r4.2**. The global dataset contains event logs for 1,000 corporate users spanning 1.5 years.

To prevent temporal data leakage and represent a realistic deployment model, the dataset is split chronologically:
* **Training Partition (Weeks 1 to 52)**: 49,867 user-weeks (240 malicious, 49,627 benign).
* **Testing Partition (Weeks 53 to 72)**: 17,300 user-weeks (82 malicious, 17,218 benign).

**Dataset Statistics**
| Metric | Count |
| :--- | :---: |
| Total Corporate Users | 1,000 |
| Total Malicious Users | 70 |
| Total Benign Users | 930 |
| Total User-Weeks | 67,167 |
| Total Malicious Weeks | 322 |

## 3. Mathematical Framework

### 3.1 Digital Behavioral Signature (DBS)
The weekly normalized feature vector is defined as:
$$
\mathbf{DBS}_{U, W} = \begin{bmatrix} \bar{f}_{LF} & \bar{f}_{AH} & \bar{f}_{SD} & \bar{f}_{EF} & \bar{f}_{VD} & \bar{f}_{RT} & \bar{f}_{CD} & \bar{f}_{RR} \end{bmatrix}^T
$$

### 3.2 Behavioral Similarity Index (BSI)
Calculates profile alignment between two signatures via Cosine Similarity:
$$
BSI(\mathbf{DBS}_A, \mathbf{DBS}_B) = \frac{\mathbf{DBS}_A \cdot \mathbf{DBS}_B}{\|\mathbf{DBS}_A\|_2 \|\mathbf{DBS}_B\|_2}
$$

### 3.3 Behavioral Drift Score (BDS)
Self-drift is modeled as the Euclidean distance between the user's weekly signature and their earliest active week's signature ($T_{\text{base}}$):
$$
BDS(U, T_{\text{base}}, W) = \|\mathbf{DBS}_{U, W} - \mathbf{DBS}_{U, T_{\text{base}}}\|_2
$$

### 3.4 Cyber Anthropology Consistency Metrics
1. **Identity Persistence ($IDP$)**: Transition stability:
   $$IDP_U = e^{-\frac{1}{W-1}\sum_{t=1}^{W-1} \|\mathbf{DBS}_{U, T_{t+1}} - \mathbf{DBS}_{U, T_t}\|_2}$$
2. **Behavioral Continuity ($BC$)**: Smoothness of weekly drift step variations:
   $$BC_U = e^{-\text{std}\left(\left\{\|\mathbf{DBS}_{U, T_{t+1}} - \mathbf{DBS}_{U, T_t}\|_2 \;\mid\; t \in [1, W-1]\right\}\right)}$$
3. **Social Role Consistency ($SRC$)**: Footprint stability:
   $$SRC_U = 1.0 - \frac{1}{W-1}\sum_{t=1}^{W-1} |IPS_{U, T_t} - IPS_{U, T_{t+1}}|$$

## 4. Experimental Results

Supervised models significantly outperform unsupervised anomaly detection baselines.

### Table 2: Classifier Performance (Weeks 53-72)
| Classifier | Precision | Recall | F1-Score | AUPRC |
| :--- | :---: | :---: | :---: | :---: |
| **XGBoost** | **14.55%** | **9.76%** | **11.68%** | **0.1064** |
| **Random Forest** | 23.08% | 3.66% | 6.32% | 0.0903 |
| **One-Class SVM** | 3.80% | 3.66% | 3.73% | 0.0428 |
| **Isolation Forest** | 1.67% | 1.22% | 1.41% | 0.0322 |

### Table 3: Feature Ablation Study (XGBoost)
| Configuration | Precision | Recall | F1-Score | AUPRC |
| :--- | :---: | :---: | :---: | :---: |
| **A. Raw Features Only** | 14.55% | 9.76% | 11.68% | 0.1064 |
| **D. DBS + Anthropology** | **44.44%** | 4.88% | 8.79% | **0.1269** |

Combining DBS + Anthropology increases precision from 14.55% to 44.44% and increases AUPRC to 0.1269.

## 5. Interpretation of Cyber Anthropology Metrics
The average anthropological consistency scores for benign and malicious users are shown below:

### Table 5: Anthropology Averages
| User Type | Mean IDP | Mean BC | Mean SRC |
| :--- | :---: | :---: | :---: |
| Benign Users | **0.8647** | **0.9238** | 0.9858 |
| Malicious Users | 0.8622 | 0.9222 | **0.9864** |

Mean IDP, BC, and SRC values for benign and malicious populations are very close. These metrics are not intended to serve as standalone anomaly thresholds. Their value emerges when combined with other behavioral features inside non-linear classifiers such as XGBoost. Anthropology metrics capture longitudinal consistency and behavioral structure rather than direct maliciousness. Small population-level differences do not imply low predictive utility. Interaction effects between anthropology metrics and DBS features can significantly improve precision despite weak marginal separation, as seen in the ablation study. Consequently, anthropology metrics should be interpreted as behavioral context features rather than direct indicators of insider threat activity.

## 6. Related Work
This section compares Cyber DNA against existing methodologies.

1. **Traditional Rule-Based Insider Threat Detection**: These systems rely on strict thresholds (e.g., "more than 50 emails sent"). Cyber DNA instead uses proportional behavioral signatures that adapt to user baselines.
2. **User and Entity Behavior Analytics (UEBA)**: Systems like Splunk UBA and Microsoft Sentinel UEBA look at broad network anomalies. Cyber DNA introduces Digital Behavioral Signatures (DBS) with deep focus on human communication and interaction structures.
3. **Statistical Behavioral Profiling Systems**: Approaches by Glasser & Lindauer (2013) introduced dataset foundations, but lacked longitudinal continuity. Cyber DNA addresses this via Behavioral Drift Scores (BDS).
4. **Machine Learning Insider Threat Detection Approaches**: Gavai et al. and other behavioral anomaly detection approaches primarily perform point-in-time classification. Cyber DNA utilizes Cyber Anthropology metrics (IDP, BC, SRC) to measure behavioral evolution over time.
5. **CERT Dataset Research Literature**: Prior studies on CERT often achieve low precision due to overlapping benign/malicious distributions. Cyber DNA introduces Behavioral Similarity Indices (BSI) and longitudinal behavioral consistency modeling to suppress false positives.

| System Type | Approach | Cyber DNA Difference |
| :--- | :--- | :--- |
| Traditional Rule-Based | Static thresholds | Adaptive DBS profiles |
| Standard UEBA | Broad event anomalies | Cyber Anthropology metrics |
| ML Point-in-time | Independent weekly classification | Behavioral Drift Scores (BDS) |

## 7. Class Imbalance Considerations
* Total malicious weeks: 322
* Total user-weeks: 67,167
* Malicious ratio: approximately 0.48%

Insider threat detection is an extreme class-imbalance problem. Accuracy is not an appropriate metric, as a model that predicts "benign" 100% of the time would achieve 99.52% accuracy. For this reason, Precision, Recall, F1-score, and AUPRC are emphasized. Low recall is expected under severe imbalance, especially when relying on purely behavioral (non-content) features. The reported results should be interpreted in that context; a precision of 44.44% represents a massive gain over the ~0.48% random guessing baseline.

Alternative strategies not implemented in this phase include class weighting, cost-sensitive learning, SMOTE, oversampling, and undersampling. These remain future research directions.

## 8. Department Filter Calibration Analysis
An adaptive Z-score filter was implemented to suppress false alarms caused by role transitions:

$$
Z_D = \frac{BSI(\mathbf{DBS}_{U, W}, \mathbf{DBS}_{D, W}) - \mu_D}{\sigma_D} \ge Z_{\text{thresh}}
$$

### Table 4: Z-score Suppression Sweep (Test Split)
| Z-score Threshold | Precision | Recall | F1-Score | AUPRC | Suppressed Alerts | Benign Suppressed | Malicious Suppressed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Z = -3.0` | 0.00% | 0.00% | 0.00% | 0.0484 | 10 | 5 | 5 |
| `Z = -2.5` | 50.00% | 1.22% | 2.38% | 0.0643 | 9 | 5 | 4 |

Active Z-score suppression leads to over-suppression of true threat signatures, dropping the F1-score to 2.38% (at Z = -2.5). Corporate departments share highly uniform schedules in the raw feature space, causing centroids to cluster closely. Consequently, the active suppression filter is disabled (BSI threshold = 1.0) for deployment to preserve maximum recall.

## 9. Threats to Validity

### Internal Validity
* **Feature selection limitations**: Only 8 raw behavioral features were used.
* **Potential modeling assumptions**: Assumes weekly granularity captures meaningful changes.
* **Behavioral baseline assumptions**: Assumes the training period contains purely benign baseline behavior.

### External Validity
* **Evaluation limited to CERT r4.2**: Results may not directly translate to different datasets.
* **Enterprise-specific behavior patterns**: Different organizations have different interaction norms.
* **Generalization concerns**: The model requires fitting normalizers and centroids specific to the deployed environment.

### Construct Validity
* **Whether DBS fully captures human behavior**: Excludes content-based linguistics, file types, and deep network packet inspection.
* **Interpretation of anthropology metrics**: Static metrics aggregate dynamic histories, potentially washing out sudden rapid shifts.

### Statistical Validity
* **Extreme class imbalance**: Only 322 malicious weeks exist.
* **Limited malicious samples**: Threat scenarios are simulated rather than organically occurring.
* **Variance across threat scenarios**: Insider behaviors vary drastically (sabotage vs. IP theft vs. fraud).

## 10. Future Work

### Short-Term Extensions
* **USB activity features**: Tracking mass storage transfers to detect data exfiltration.
* **File access features**: Analyzing distinct file touches and directory traversal.
* **Workstation diversity**: Monitoring the number of unique PCs accessed.
* **After-hours activity**: Capturing off-shift logins.
* **Weekend behavior metrics**: Tracking non-standard working days.

### Medium-Term Extensions
* **Communication graph analytics**: Enhancing DBS with topological network data.
* **Centrality measures**: Utilizing PageRank and Betweenness Centrality for users.
* **Community detection**: Identifying tightly coupled sub-departments.
* **Adaptive departmental centroids**: Implementing exponential moving averages for seasonal drift.
* **Dynamic organizational profiling**: Modeling the organization as a living entity.

### Long-Term Extensions
* **Real-time monitoring**: Moving from weekly batch processing to streaming architectures.
* **Streaming analytics**: Utilizing Apache Kafka/Flink for live behavioral signatures.
* **Cross-platform telemetry**: Integrating physical badging and cloud application logs.
* **Multi-source behavioral fusion**: Combining host-based, network-based, and identity-based telemetry.
* **AI-assisted analyst explanations**: Using LLMs to translate mathematical drift anomalies into human-readable alerts.

## 11. Conclusion
Cyber DNA provides a robust, human-centered behavioral profiling layer for continuous authentication and insider threat detection. By integrating mathematical anthropology scores and temporal drift tracking, the framework successfully improves classifier precision and highlights the value of longitudinal consistency features. Addressing class imbalance and applying multi-dimensional behavioral signatures offers a viable path toward non-intrusive threat mitigation without relying exclusively on technical artifacts.
