# Cyber DNA Framework: Core Metrics & Mathematical Formulation

The Cyber DNA framework transforms raw enterprise log data into a structured 29-dimensional vector, measures temporal behavioral drift, and incorporates qualitative anthropological stability metrics into strict mathematical equations.

---

## 1. Digital Behavioral Signature (DBS) Feature Space

A Digital Behavioral Signature (DBS) is a numeric feature vector that represents an individual’s characteristic digital behavior over a rolling 7-day observation window ($W$). In the final Expanded Cyber DNA Model, the signature is a 29-dimensional vector partitioned into four major blocks:

1. **Baseline Block**: `login_freq`, `active_hours_ratio`, `avg_session_duration`, `email_freq`, `contact_diversity`, `vocab_diversity`, `reciprocity_ratio`, `response_time`
2. **Temporal / Off-Hours Block**: `after_hours_logon_count`, `after_hours_logon_ratio`, `weekend_logon_count`, `weekend_logon_ratio`, `emails_sent_after_hours`, `emails_sent_weekend`
3. **USB & Device Block**: `usb_event_count`, `usb_active_days`, `usb_after_hours_count`, `usb_weekend_count`
4. **Workstation Diversity Block**: `unique_pc_count`, `new_pc_count`, `pc_switch_count`

All features are normalized to the unit hypercube $[0, 1]$ using Min-Max bounds fit strictly on the training partition to prevent temporal leakage:

$$
\mathbf{DBS}_{U, W} = \begin{bmatrix} \bar{f}_{1} & \bar{f}_{2} & \dots & \bar{f}_{29} \end{bmatrix}^T
$$

---

## 2. Behavioral Drift Score (BDS)

**Definition:** The Behavioral Drift Score (BDS) quantifies how much a user's DBS changes between a historical baseline week ($T_{\text{base}}$) and a target week ($W$) using the Euclidean distance ($L_2$ norm):

$$
BDS(U, T_{\text{base}}, W) = \|\mathbf{DBS}_{U, W} - \mathbf{DBS}_{U, T_{\text{base}}}\|_2
$$

**Interpretation:**
By utilizing the $L_2$ norm across a 29-dimensional space, the BDS captures multivariate behavioral deviations (e.g., a simultaneous spike in USB transfers and off-hours logins).
- **Low Self-Drift**: Indicates normal, stable behavior consistent with the user's historical footprint.
- **Severe Self-Drift**: Indicates a high probability of major workflow shifts, exfiltration phases, credential sharing, or account takeover.

---

## 3. Cyber Anthropology Consistency Metrics

Cyber DNA translates qualitative cyber anthropology concepts into three quantitative, static user-level consistency metrics calculated across all $T$ observed active weeks.

### 3.1 Digital Identity Persistence (IDP)
Measures the long-term stability of a user's weekly signature transitions. Users who dramatically shift their behavior from week to week exhibit low identity persistence.
$$
\text{IDP}_u = 1 - \frac{1}{T-1} \sum_{t=2}^{T} \|\mathbf{DBS}_{u,t} - \mathbf{DBS}_{u,t-1}\|_2
$$

### 3.2 Behavioral Continuity (BC)
Measures how smoothly behavioral characteristics are maintained across time by examining the variance of the weekly drift changes. A high variance indicates erratic, discontinuous behavior.
$$
\text{BC}_u = 1 - \text{Var}(\text{BDS}_{u,2}, \text{BDS}_{u,3}, \ldots, \text{BDS}_{u,T})
$$

### 3.3 Social Role Consistency (SRC)
Measures stability in communication and interaction styles based on the user's weekly interaction footprints (where $\mathbf{S}_{u,t}$ is the communication/interaction subvector representing the social-role behavior at week $t$).
$$
\text{SRC}_u = 1 - \frac{1}{T-1} \sum_{t=2}^{T} \|\mathbf{S}_{u,t} - \mathbf{S}_{u,t-1}\|_2
$$

---

# What I would tell Sir (Summary)

> "We have developed the Cyber DNA framework, which structures enterprise log data into a 29-dimensional **Digital Behavioral Signature (DBS)** normalized strictly on training data to prevent temporal leakage. 
> 
> To track behavioral evolution over time, we compute the **Behavioral Drift Score (BDS)** using the Euclidean distance ($L_2$ norm) between a user's current week and their historical baseline week.
> 
> Furthermore, we formulated three Cyber Anthropology metrics—**Identity Persistence ($IDP$), Behavioral Continuity ($BC$), and Social Role Consistency ($SRC$)**—which capture the transition stability and variance of a user's behavior. 
> 
> By feeding this rich, longitudinal 29-dimensional feature space into an XGBoost classifier with strict chronological evaluation and `scale_pos_weight` imbalance handling, the framework successfully achieves an F1-score of 48.41% on unseen test data, significantly improving visibility into malicious insider activity."
