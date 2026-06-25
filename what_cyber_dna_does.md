# What Cyber DNA actually does?

### Input

Enterprise user log data from the **CMU CERT Insider Threat Dataset r4.2** (or corporate logs):

- **Authentication records** (`logon.csv`): Logon/logoff timestamps, session endpoints.
- **Email communications** (`email.csv`): Timestamp, sender, recipients.
- **Device records** (`device.csv`): USB connection and mass-storage events.
- **Organizational context** (`ldap.csv`): Corporate directories mapping users to departments.

---

### Step 1: Extract behavioral features

The system extracts **29 normalized features** across rolling **7-day weekly windows**. These are grouped into blocks:

1. **Baseline Activity**: Login frequency, active hour ratios, average session duration, and email frequency.
2. **Temporal & Off-Hours Behavior**: Weekend activity, after-hours logons, and off-hours emails.
3. **Device & USB Activity**: USB event counts, distinct active USB days, and off-hours USB usage.
4. **Workstation Diversity**: Number of distinct PCs used, and novel (never-before-seen) PCs accessed.

---

### Step 2: Generate a Digital Behavioral Signature (DBS)

These 29 features are scaled to the unit hypercube $[0, 1]^{29}$ using Min-Max bounds fit purely on the training set to prevent data leakage. This forms the **Digital Behavioral Signature (DBS)** vector:

$$
\mathbf{DBS}_{U, W} = \begin{bmatrix} \bar{f}_{1} & \bar{f}_{2} & \dots & \bar{f}_{29} \end{bmatrix}^T
$$

This weekly 29-dimensional vector becomes the user's holistic **behavioral fingerprint**.

---

### Step 3: Compute Cyber Anthropology Metrics

The framework quantifies qualitative anthropological concepts to measure the stability of the user's footprint over time:

- **Identity Persistence ($IDP$)**: Measures the transition stability of consecutive weekly signatures.
- **Behavioral Continuity ($BC$)**: Measures the smoothness of weekly drift shifts (variance of step-to-step drifts).
- **Social Role Consistency ($SRC$)**: Tracks the variation in a user's communication and interaction footprints.

---

### Step 4: Behavioral Drift Analysis

The system generates a DBS for each consecutive week and measures the distance from the user's historical baseline week ($T_{\text{base}}$) using Euclidean distance ($L_2$ norm) to calculate the **Behavioral Drift Score (BDS)**:

$$
BDS(U, T_{\text{base}}, W) = \|\mathbf{DBS}_{U, W} - \mathbf{DBS}_{U, T_{\text{base}}}\|_2
$$

**Output:**

- **Low Drift**: Normal, stable, consistent behavior.
- **High Drift**: Major behavioral shift (e.g. exfiltration spikes, role changes, or account compromise).

[NOTE: Behavioral Drift Analysis is an additional temporal layer that measures how a user's Digital Behavioral Signature changes over time. Existing behavioral analytics methods generally analyze behavior at a single point in time, whereas our approach studies behavioral evolution dynamically.]

---

# Final Output

For every user-week, the classifier generates a **Cyber DNA Profile**:

```
Cyber DNA Profile (User-Week)

Digital Behavioral Signature (DBS):
  29 normalized features (Activity, Temporal, USB, Workstation-Diversity)

Static Anthropology Scores:
  IDP  = 0.8647 (Identity Persistence - Transition stability)
  BC   = 0.9238 (Behavioral Continuity - Drift smoothness)
  SRC  = 0.9858 (Social Role Consistency - Network stability)

Temporal Drift (BDS) = 13.41%

Classification: Malicious / Benign (via XGBoost threshold tuned to 0.30)
```

---

# One-line answer

> **Cyber DNA creates a 29-dimensional weekly behavioral signature from system activity, USB usage, off-hours habits, and temporal indicators, and uses Machine Learning to analyze how those behaviors evolve over time to detect insider threats on the CMU CERT r4.2 dataset.**
> 

---

# What makes it different?

Most existing work does **one thing**:

- **Behavioral biometrics** → typing/login behavior
- **Stylometry** → writing style (vocabulary only)
- **User profiling** → raw activity counts
- **Insider threat systems** → static anomaly detection without temporal context (often using leaky evaluation)

Your project integrates all of these layers with **Cyber Anthropology** and **Chronological Evaluation**:

```
  Baseline Activity Behavior (Logons, Sessions, Emails)
+ Temporal Behavior (Off-hours, Weekends)
+ Device & Diversity Behavior (USB usage, Workstation transitions)
+ Cyber Anthropology (Identity Persistence, Behavioral Continuity, Social Role Consistency)
+ Temporal Behavioral Drift (BDS Timeline tracing)
+ Leakage-Free Chronological Protocol (Train-only tuning)
===================================================================================
= Cyber DNA Framework
```

### Core Differentiators:

1. **Dynamic Temporal Tracking**: Incorporating weekly $BDS$ timelines instead of static point-in-time snapshot audits.
2. **Leakage-Free Evaluation**: Evaluating the pipeline strictly chronologically (Weeks 1-52 train, 53-72 test) to ensure normalizers and thresholds are completely blind to future events, proving its validity for real-world deployment.
3. **Expanded Behavioral Space**: Integrating granular USB tracking, workstation-diversity history, and off-hours activity, which successfully **increased the F1-score from our 44.44% baseline to 48.41%** on the unseen CERT r4.2 test data, recovering 10 additional malicious weeks.
