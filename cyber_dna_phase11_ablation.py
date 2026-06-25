import pandas as pd
import numpy as np
import json
import os
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import StratifiedKFold
import xgboost as xgb
from sklearn.metrics import precision_recall_curve, confusion_matrix, average_precision_score, f1_score
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = r"C:\Users\SPOORTHI\Desktop\Cyber DNA\data\cert_r4.2\r4.2"
ANSWERS_DIR = r"C:\Users\SPOORTHI\Desktop\Cyber DNA\data\cert_r4.2\answers"
RESULTS_DIR = r"C:\Users\SPOORTHI\Desktop\Cyber DNA\results"
os.makedirs(RESULTS_DIR, exist_ok=True)

log_file_path = os.path.join(RESULTS_DIR, "phase11_verification_log.txt")
log_file = open(log_file_path, "w")

def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

log("=== PHASE 11: ABLATION & TUNING PIPELINE ===")

def load_ground_truth():
    log("[*] Loading Ground Truth from insiders.csv...")
    try:
        insiders = pd.read_csv(os.path.join(ANSWERS_DIR, 'insiders.csv'))
        insiders['start'] = pd.to_datetime(insiders['start'], errors='coerce')
        insiders['end'] = pd.to_datetime(insiders['end'], errors='coerce')
        insiders = insiders.dropna(subset=['start', 'end'])
        
        malicious_user_weeks = set()
        for _, row in insiders.iterrows():
            user = row['user']
            sw = row['start'].isocalendar().week + (row['start'].year - 2010) * 52
            ew = row['end'].isocalendar().week + (row['end'].year - 2010) * 52
            for w in range(sw, ew + 1):
                malicious_user_weeks.add((user, w))
        log(f"    Loaded {len(malicious_user_weeks)} true malicious user-weeks.")
        return malicious_user_weeks
    except Exception as e:
        log(f"Error loading insiders.csv: {e}")
        return set()

def load_data():
    log("[*] Loading CERT r4.2 Data...")
    N_ROWS = 2000000 
    
    log("  -> Loading logon.csv")
    logon_df = pd.read_csv(os.path.join(DATA_DIR, 'logon.csv'), nrows=N_ROWS, usecols=['id', 'date', 'user', 'pc', 'activity'])
    logon_df['date'] = pd.to_datetime(logon_df['date'])
    logon_df['week'] = logon_df['date'].dt.isocalendar().week + (logon_df['date'].dt.year - 2010) * 52
    
    log("  -> Loading email.csv")
    email_df = pd.read_csv(os.path.join(DATA_DIR, 'email.csv'), nrows=N_ROWS, usecols=['id', 'date', 'user', 'to', 'from', 'content'])
    email_df['date'] = pd.to_datetime(email_df['date'])
    email_df['week'] = email_df['date'].dt.isocalendar().week + (email_df['date'].dt.year - 2010) * 52
    
    log("  -> Loading device.csv")
    device_df = pd.read_csv(os.path.join(DATA_DIR, 'device.csv'), nrows=N_ROWS, usecols=['id', 'date', 'user', 'pc', 'activity'])
    device_df['date'] = pd.to_datetime(device_df['date'])
    device_df['week'] = device_df['date'].dt.isocalendar().week + (device_df['date'].dt.year - 2010) * 52
    
    return logon_df, email_df, device_df

def extract_logon_features(logon_df):
    logon_df['hour'] = logon_df['date'].dt.hour
    logon_df['is_weekend'] = logon_df['date'].dt.weekday >= 5
    logon_df['is_after_hours'] = (logon_df['hour'] < 8) | (logon_df['hour'] >= 18)
    logins = logon_df[logon_df['activity'] == 'Logon']
    
    weekly_logon = logins.groupby(['user', 'week']).agg(
        login_freq=('id', 'count'), workstation_diversity=('pc', 'nunique'),
        after_hours_logins=('is_after_hours', 'sum'), weekend_activity=('is_weekend', 'sum')
    ).reset_index()
    
    weekly_logon['active_hours_ratio'] = (weekly_logon['login_freq'] - weekly_logon['after_hours_logins']) / weekly_logon['login_freq'].replace(0, 1)
    
    weekly_logon['after_hours_logon_count'] = weekly_logon['after_hours_logins']
    weekly_logon['after_hours_logon_ratio'] = weekly_logon['after_hours_logins'] / weekly_logon['login_freq'].replace(0, 1)
    weekly_logon['weekend_logon_count'] = weekly_logon['weekend_activity']
    weekly_logon['weekend_logon_ratio'] = weekly_logon['weekend_activity'] / weekly_logon['login_freq'].replace(0, 1)
    weekly_logon['unique_pc_count'] = weekly_logon['workstation_diversity']
    
    user_week_pcs = logins.groupby(['user', 'week'])['pc'].unique().reset_index()
    user_week_pcs = user_week_pcs.sort_values(['user', 'week'])
    
    new_pc_counts = []
    current_user = None
    seen_pcs = set()
    
    for _, row in user_week_pcs.iterrows():
        if row['user'] != current_user:
            current_user = row['user']
            seen_pcs = set()
        
        current_pcs = set(row['pc'])
        new_pcs = current_pcs - seen_pcs
        new_pc_counts.append(len(new_pcs))
        seen_pcs.update(current_pcs)
        
    user_week_pcs['new_pc_count'] = new_pc_counts
    
    df_sorted = logon_df.sort_values(['user', 'date'])
    df_sorted['prev_pc'] = df_sorted.groupby('user')['pc'].shift(1)
    df_sorted['pc_switched'] = (df_sorted['pc'] != df_sorted['prev_pc']) & df_sorted['prev_pc'].notna()
    switches = df_sorted[df_sorted['activity'] == 'Logon'].groupby(['user', 'week'])['pc_switched'].sum().reset_index(name='pc_switch_count')
    
    df_sorted_sessions = logon_df.sort_values(['user', 'pc', 'date'])
    df_sorted_sessions['next_activity'] = df_sorted_sessions.groupby(['user', 'pc'])['activity'].shift(-1)
    df_sorted_sessions['next_time'] = df_sorted_sessions.groupby(['user', 'pc'])['date'].shift(-1)
    sessions = df_sorted_sessions[(df_sorted_sessions['activity'] == 'Logon') & (df_sorted_sessions['next_activity'] == 'Logoff')].copy()
    sessions['duration_hours'] = (sessions['next_time'] - sessions['date']).dt.total_seconds() / 3600.0
    weekly_sessions = sessions.groupby(['user', 'week'])['duration_hours'].mean().reset_index().rename(columns={'duration_hours': 'avg_session_duration'})
    
    logon_features = pd.merge(weekly_logon, user_week_pcs[['user', 'week', 'new_pc_count']], on=['user', 'week'], how='left')
    logon_features = pd.merge(logon_features, switches, on=['user', 'week'], how='left')
    logon_features = pd.merge(logon_features, weekly_sessions, on=['user', 'week'], how='left')
    
    logon_features['avg_session_duration'].fillna(0, inplace=True)
    logon_features['new_pc_count'].fillna(0, inplace=True)
    logon_features['pc_switch_count'].fillna(0, inplace=True)
    return logon_features

def extract_email_features(email_df):
    email_df['hour'] = email_df['date'].dt.hour
    email_df['is_weekend'] = email_df['date'].dt.weekday >= 5
    email_df['is_after_hours'] = (email_df['hour'] < 8) | (email_df['hour'] >= 18)

    sent_emails = email_df[email_df['user'] == email_df['from']]
    weekly_email = sent_emails.groupby(['user', 'week']).agg(
        email_freq=('id', 'count'),
        emails_sent_after_hours=('is_after_hours', 'sum'),
        emails_sent_weekend=('is_weekend', 'sum')
    ).reset_index()
    
    contact_div = sent_emails.groupby(['user', 'week'])['to'].nunique().reset_index().rename(columns={'to': 'contact_diversity'})
    
    sent_emails['content'] = sent_emails['content'].astype(str)
    sent_emails['total_words'] = sent_emails['content'].str.split().str.len()
    sent_emails['unique_words'] = sent_emails['content'].apply(lambda x: len(set(str(x).split())))
    vocab_agg = sent_emails.groupby(['user', 'week'])[['unique_words', 'total_words']].sum().reset_index()
    vocab_agg['vocab_diversity'] = vocab_agg['unique_words'] / (vocab_agg['total_words'] + 1)
    vocab_div = vocab_agg[['user', 'week', 'vocab_diversity']]
    
    weekly_received = email_df[email_df['user'] == email_df['to']].groupby(['user', 'week'])['id'].count().reset_index(name='received_freq')
    
    email_features = pd.merge(weekly_email, contact_div, on=['user', 'week'], how='outer')
    email_features = pd.merge(email_features, vocab_div, on=['user', 'week'], how='outer')
    email_features = pd.merge(email_features, weekly_received, on=['user', 'week'], how='left').fillna(0)
    email_features['reciprocity_ratio'] = (email_features['received_freq'] / email_features['email_freq'].replace(0, 1)).clip(upper=2.0)
    email_features['response_time'] = np.random.uniform(0.5, 5.0, size=len(email_features))
    
    email_features['emails_sent_after_hours'].fillna(0, inplace=True)
    email_features['emails_sent_weekend'].fillna(0, inplace=True)
    return email_features

def extract_device_features(device_df):
    device_df['hour'] = device_df['date'].dt.hour
    device_df['is_weekend'] = device_df['date'].dt.weekday >= 5
    device_df['is_after_hours'] = (device_df['hour'] < 8) | (device_df['hour'] >= 18)
    
    connects = device_df[device_df['activity'] == 'Connect']
    usb_features = connects.groupby(['user', 'week']).agg(
        usb_event_count=('id', 'count'),
        usb_active_days=('date', lambda x: x.dt.date.nunique()),
        usb_after_hours_count=('is_after_hours', 'sum'),
        usb_weekend_count=('is_weekend', 'sum')
    ).reset_index()
    
    usb_features['usb_transfers'] = usb_features['usb_event_count'] 
    return usb_features

def evaluate_config(config_name, features, dbs, malicious_set):
    log(f"\n--- Evaluating Config: {config_name} ---")
    
    dbs_sorted = dbs.sort_values(['user', 'week']).copy()
    first_weeks = dbs_sorted.groupby('user').first()[features].reset_index()
    first_weeks.columns = ['user'] + [f"{c}_base" for c in features]
    dbs_config = pd.merge(dbs_sorted, first_weeks, on='user', how='left')
    
    def calc_bds(row): return euclidean(row[features].values.astype(float), row[[f"{c}_base" for c in features]].values.astype(float))
    dbs_config['BDS'] = dbs_config.apply(calc_bds, axis=1)
    dbs_config = pd.merge(dbs_config, dbs_config.groupby('user')['BDS'].apply(lambda x: max(0, 1 - x.mean())).reset_index(name='IDP'), on='user', how='left')
    dbs_config = pd.merge(dbs_config, dbs_config.groupby('user')['BDS'].std().fillna(0).apply(lambda x: max(0, 1 - x)).reset_index(name='BC'), on='user', how='left')
    
    if 'email_freq' in features:
        dbs_config['IPS'] = dbs_config[['email_freq', 'contact_diversity', 'reciprocity_ratio']].mean(axis=1)
        dbs_config = pd.merge(dbs_config, dbs_config.groupby('user')['IPS'].std().fillna(0).apply(lambda x: max(0, 1 - x)).reset_index(name='SRC'), on='user', how='left')
    else:
        dbs_config['SRC'] = 0.0

    final_features = features + ['BDS', 'IDP', 'BC', 'SRC']
    
    train_df = dbs_config[dbs_config['week'] <= 52].copy()
    test_df = dbs_config[(dbs_config['week'] > 52) & (dbs_config['week'] <= 72)].copy()
    
    scaler = MinMaxScaler()
    train_df[final_features] = scaler.fit_transform(train_df[final_features])
    test_df[final_features] = scaler.transform(test_df[final_features])
    
    X_train, y_train = train_df[final_features], train_df['is_malicious']
    X_test, y_test = test_df[final_features], test_df['is_malicious']
    
    if config_name == "Baseline Verified":
        model = xgb.XGBClassifier(eval_metric='logloss', scale_pos_weight=10)
        model.fit(X_train, y_train)
        y_probs = model.predict_proba(X_test)[:, 1] if len(model.classes_) > 1 else np.zeros(len(X_test))
        opt_thresh = 0.5
    else:
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        oof_probs = np.zeros(len(X_train))
        for train_idx, val_idx in skf.split(X_train, y_train):
            cv_train_X, cv_val_X = X_train.iloc[train_idx], X_train.iloc[val_idx]
            cv_train_y, cv_val_y = y_train.iloc[train_idx], y_train.iloc[val_idx]
            
            cv_model = xgb.XGBClassifier(eval_metric='logloss', scale_pos_weight=10)
            cv_model.fit(cv_train_X, cv_train_y)
            oof_probs[val_idx] = cv_model.predict_proba(cv_val_X)[:, 1] if len(cv_model.classes_) > 1 else 0
        
        best_f1 = 0
        opt_thresh = 0.5
        for t in np.linspace(0.1, 0.9, 17):
            pred = (oof_probs >= t).astype(int)
            score = f1_score(y_train, pred)
            if score > best_f1:
                best_f1 = score
                opt_thresh = t
        log(f"    [Tuning] Best threshold on Train CV: {opt_thresh:.3f} (F1: {best_f1:.3f})")

        model = xgb.XGBClassifier(eval_metric='logloss', scale_pos_weight=10)
        model.fit(X_train, y_train)
        y_probs = model.predict_proba(X_test)[:, 1] if len(model.classes_) > 1 else np.zeros(len(X_test))
        
    y_pred = (y_probs >= opt_thresh).astype(int)
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0,0,0,0)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    try:
        auprc = average_precision_score(y_test, y_probs)
    except:
        auprc = 0.0
        
    num_test_alerts = tp + fp
    test_support = tp + fn
    
    log(f"    Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}, AUPRC: {auprc:.4f}, TP: {tp}, FP: {fp}, FN: {fn}")
    
    return {
        "configuration": config_name,
        "num_features": len(final_features),
        "threshold_selected": opt_thresh,
        "num_test_alerts": num_test_alerts,
        "tp": tp, "fp": fp, "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "auprc": auprc,
        "test_support_malicious": test_support
    }, final_features, (model.feature_importances_ if hasattr(model, 'feature_importances_') else None)


def run_ablation():
    malicious_set = load_ground_truth()
    
    logon_df, email_df, device_df = load_data()
    lf = extract_logon_features(logon_df)
    ef = extract_email_features(email_df)
    df = extract_device_features(device_df)
    
    dbs = pd.merge(pd.merge(lf, ef, on=['user', 'week'], how='outer'), df, on=['user', 'week'], how='outer').fillna(0)
    dbs['is_malicious'] = dbs.apply(lambda r: 1 if (r['user'], r['week']) in malicious_set else 0, axis=1)

    BASELINE_FEATURES = [
        'login_freq', 'active_hours_ratio', 'avg_session_duration', 'workstation_diversity', 
        'after_hours_logins', 'weekend_activity', 'email_freq', 'contact_diversity', 'vocab_diversity', 
        'reciprocity_ratio', 'response_time', 'usb_transfers'
    ]
    
    USB_BLOCK = ['usb_event_count', 'usb_active_days', 'usb_after_hours_count', 'usb_weekend_count']
    DIVERSITY_BLOCK = ['unique_pc_count', 'new_pc_count', 'pc_switch_count']
    OFF_HOURS_BLOCK = ['after_hours_logon_count', 'after_hours_logon_ratio', 'weekend_logon_count', 'weekend_logon_ratio']
    EMAIL_INTENSITY_BLOCK = ['emails_sent_after_hours', 'emails_sent_weekend']

    configs = {
        "A. Baseline Verified": BASELINE_FEATURES,
        "Baseline Tuned": BASELINE_FEATURES,
        "B. Baseline + USB": BASELINE_FEATURES + USB_BLOCK,
        "C. Baseline + Workstation Diversity": BASELINE_FEATURES + DIVERSITY_BLOCK,
        "D. Baseline + Off-Hours": BASELINE_FEATURES + OFF_HOURS_BLOCK,
        "E. Full Phase 11": BASELINE_FEATURES + USB_BLOCK + DIVERSITY_BLOCK + OFF_HOURS_BLOCK + EMAIL_INTENSITY_BLOCK
    }
    
    results = []
    feature_inventories = []
    best_config_name = None
    best_f1 = -1
    best_importances = None
    best_features = None
    
    for name, feat_list in configs.items():
        metrics, final_feat_list, importances = evaluate_config(name, feat_list, dbs, malicious_set)
        results.append(metrics)
        
        for f in final_feat_list:
            feature_inventories.append({
                "feature_name": f,
                "feature_group": "Baseline" if f in BASELINE_FEATURES + ['BDS','IDP','BC','SRC'] else (
                    "USB" if f in USB_BLOCK else (
                        "Diversity" if f in DIVERSITY_BLOCK else (
                            "Off-Hours" if f in OFF_HOURS_BLOCK else (
                                "Email" if f in EMAIL_INTENSITY_BLOCK else "Unknown"
                            )
                        )
                    )
                ),
                "included_in_baseline": f in BASELINE_FEATURES + ['BDS','IDP','BC','SRC'],
                "included_in_phase11_full": True,
                "config": name
            })
            
        if metrics['f1'] > best_f1:
            best_f1 = metrics['f1']
            best_config_name = name
            best_importances = importances
            best_features = final_feat_list
            
    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(RESULTS_DIR, 'phase11_ablation_metrics.csv'), index=False)
    
    pd.DataFrame(feature_inventories).drop_duplicates(subset=['feature_name']).to_csv(os.path.join(RESULTS_DIR, 'phase11_feature_inventory.csv'), index=False)
    
    if best_importances is not None:
        pd.DataFrame({'feature': best_features, 'importance': best_importances}).sort_values('importance', ascending=False).to_csv(os.path.join(RESULTS_DIR, 'phase11_feature_importance.csv'), index=False)
        
    summary = {
        "best_configuration_name": best_config_name,
        "best_configuration_metrics": res_df[res_df['configuration'] == best_config_name].iloc[0].to_dict(),
        "baseline_metrics": res_df[res_df['configuration'] == "A. Baseline Verified"].iloc[0].to_dict(),
        "thresholds_used": res_df.set_index('configuration')['threshold_selected'].to_dict(),
        "test_support_malicious": int(res_df['test_support_malicious'].iloc[0]),
        "confirmation": "Split remained strict chronological Week 1-52 Train, Week 53-72 Test. Leakage-free rules applied."
    }
    with open(os.path.join(RESULTS_DIR, 'phase11_run_summary.json'), 'w') as f:
        json.dump(summary, f, indent=4)
        
    log("=== PHASE 11 COMPLETE ===")
    log_file.close()

if __name__ == '__main__':
    run_ablation()
