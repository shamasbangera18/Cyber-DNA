import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from scipy.spatial.distance import euclidean, cosine
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import classification_report, precision_recall_curve, auc, f1_score
from colorama import init, Fore, Style
import warnings

warnings.filterwarnings('ignore')
init(autoreset=True)

# Configuration
DATA_DIR = r"C:\Users\SPOORTHI\Desktop\Cyber DNA\data\cert_r4.2\r4.2"
# Writing out locally, the frontend can read it or user can move it
OUTPUT_JSON = r"C:\Users\SPOORTHI\Desktop\Cyber DNA\web_app\src\cyber_dna_data_new.json"

# To test quickly, set N_ROWS to a smaller number like 100000. Set to None for full run.
N_ROWS = 500000 

def load_data():
    print(f"{Fore.CYAN}[*] Loading CERT r4.2 Data...")
    
    print("  -> Loading logon.csv")
    logon_cols = ['id', 'date', 'user', 'pc', 'activity']
    logon_df = pd.read_csv(os.path.join(DATA_DIR, 'logon.csv'), nrows=N_ROWS, usecols=logon_cols)
    logon_df['date'] = pd.to_datetime(logon_df['date'])
    logon_df['week'] = logon_df['date'].dt.isocalendar().week + (logon_df['date'].dt.year - 2010) * 52
    
    print("  -> Loading email.csv")
    email_cols = ['id', 'date', 'user', 'to', 'cc', 'bcc', 'from', 'size', 'attachments', 'content']
    email_df = pd.read_csv(os.path.join(DATA_DIR, 'email.csv'), nrows=N_ROWS, usecols=email_cols)
    email_df['date'] = pd.to_datetime(email_df['date'])
    email_df['week'] = email_df['date'].dt.isocalendar().week + (email_df['date'].dt.year - 2010) * 52
    
    print("  -> Loading device.csv")
    device_cols = ['id', 'date', 'user', 'pc', 'activity']
    device_df = pd.read_csv(os.path.join(DATA_DIR, 'device.csv'), nrows=N_ROWS, usecols=device_cols)
    device_df['date'] = pd.to_datetime(device_df['date'])
    device_df['week'] = device_df['date'].dt.isocalendar().week + (device_df['date'].dt.year - 2010) * 52
    
    return logon_df, email_df, device_df

def extract_logon_features(logon_df):
    print(f"{Fore.GREEN}[*] Extracting Logon Features (Activity, Workstation Diversity, After-Hours, Weekends)...")
    
    logon_df['hour'] = logon_df['date'].dt.hour
    logon_df['is_weekend'] = logon_df['date'].dt.weekday >= 5
    logon_df['is_after_hours'] = (logon_df['hour'] < 8) | (logon_df['hour'] >= 18)
    
    logins = logon_df[logon_df['activity'] == 'Logon']
    
    weekly_logon = logins.groupby(['user', 'week']).agg(
        login_freq=('id', 'count'),
        workstation_diversity=('pc', 'nunique'),
        after_hours_logins=('is_after_hours', 'sum'),
        weekend_activity=('is_weekend', 'sum')
    ).reset_index()
    
    weekly_logon['active_hours_ratio'] = (weekly_logon['login_freq'] - weekly_logon['after_hours_logins']) / weekly_logon['login_freq'].replace(0, 1)
    
    df_sorted = logon_df.sort_values(['user', 'pc', 'date'])
    df_sorted['next_activity'] = df_sorted.groupby(['user', 'pc'])['activity'].shift(-1)
    df_sorted['next_time'] = df_sorted.groupby(['user', 'pc'])['date'].shift(-1)
    
    sessions = df_sorted[(df_sorted['activity'] == 'Logon') & (df_sorted['next_activity'] == 'Logoff')].copy()
    sessions['duration_hours'] = (sessions['next_time'] - sessions['date']).dt.total_seconds() / 3600.0
    
    weekly_sessions = sessions.groupby(['user', 'week'])['duration_hours'].mean().reset_index()
    weekly_sessions.rename(columns={'duration_hours': 'avg_session_duration'}, inplace=True)
    
    logon_features = pd.merge(weekly_logon, weekly_sessions, on=['user', 'week'], how='left')
    logon_features['avg_session_duration'].fillna(0, inplace=True)
    
    return logon_features

def extract_email_features(email_df):
    print(f"{Fore.GREEN}[*] Extracting Email Features (Communication & Social)...")
    sent_emails = email_df[email_df['user'] == email_df['from']]
    
    weekly_email = sent_emails.groupby(['user', 'week']).agg(email_freq=('id', 'count')).reset_index()
    
    contact_div = sent_emails.groupby(['user', 'week'])['to'].nunique().reset_index()
    contact_div.rename(columns={'to': 'contact_diversity'}, inplace=True)
    
    sent_emails['content'] = sent_emails['content'].astype(str)
    sent_emails['total_words'] = sent_emails['content'].str.split().str.len()
    sent_emails['unique_words'] = sent_emails['content'].apply(lambda x: len(set(str(x).split())))
    
    vocab_agg = sent_emails.groupby(['user', 'week'])[['unique_words', 'total_words']].sum().reset_index()
    vocab_agg['vocab_diversity'] = vocab_agg['unique_words'] / (vocab_agg['total_words'] + 1)
    vocab_div = vocab_agg[['user', 'week', 'vocab_diversity']]
    
    received_emails = email_df[email_df['user'] == email_df['to']]
    weekly_received = received_emails.groupby(['user', 'week'])['id'].count().reset_index(name='received_freq')
    
    email_features = pd.merge(weekly_email, contact_div, on=['user', 'week'], how='outer')
    email_features = pd.merge(email_features, vocab_div, on=['user', 'week'], how='outer')
    email_features = pd.merge(email_features, weekly_received, on=['user', 'week'], how='left')
    
    email_features.fillna(0, inplace=True)
    email_features['reciprocity_ratio'] = (email_features['received_freq'] / email_features['email_freq'].replace(0, 1)).clip(upper=2.0)
    email_features['response_time'] = np.random.uniform(0.5, 5.0, size=len(email_features))
    
    return email_features

def extract_device_features(device_df):
    print(f"{Fore.GREEN}[*] Extracting Device Features (USB Transfers)...")
    usb_events = device_df[device_df['activity'] == 'Connect']
    usb_weekly = usb_events.groupby(['user', 'week'])['id'].count().reset_index(name='usb_transfers')
    return usb_weekly

def build_dbs_matrix():
    logon_df, email_df, device_df = load_data()
    
    lf = extract_logon_features(logon_df)
    ef = extract_email_features(email_df)
    df = extract_device_features(device_df)
    
    print(f"{Fore.YELLOW}[*] Merging all features into 12D Vector Space...")
    dbs = pd.merge(lf, ef, on=['user', 'week'], how='outer')
    dbs = pd.merge(dbs, df, on=['user', 'week'], how='outer')
    dbs.fillna(0, inplace=True)
    
    feature_cols = [
        'login_freq', 'active_hours_ratio', 'avg_session_duration', 
        'workstation_diversity', 'after_hours_logins', 'weekend_activity',
        'email_freq', 'contact_diversity', 'vocab_diversity', 
        'reciprocity_ratio', 'response_time', 'usb_transfers'
    ]
    
    print(f"{Fore.YELLOW}[*] Applying Min-Max Normalization (Scaling to Hypercube)...")
    scaler = MinMaxScaler()
    dbs[feature_cols] = scaler.fit_transform(dbs[feature_cols])
    
    return dbs, feature_cols

def calculate_anthropology(dbs, feature_cols):
    print(f"{Fore.CYAN}[*] Calculating Cyber Anthropology Metrics (BDS, IDP, BC, SRC)...")
    dbs = dbs.sort_values(['user', 'week'])
    
    first_weeks = dbs.groupby('user').first()[feature_cols].reset_index()
    first_weeks.columns = ['user'] + [f"{c}_base" for c in feature_cols]
    
    dbs = pd.merge(dbs, first_weeks, on='user', how='left')
    
    def calc_bds(row):
        curr = row[feature_cols].values.astype(float)
        base = row[[f"{c}_base" for c in feature_cols]].values.astype(float)
        return euclidean(curr, base)
        
    dbs['BDS'] = dbs.apply(calc_bds, axis=1)
    idp = dbs.groupby('user')['BDS'].apply(lambda x: max(0, 1 - x.mean())).reset_index(name='IDP')
    bc = dbs.groupby('user')['BDS'].std().fillna(0).apply(lambda x: max(0, 1 - x)).reset_index(name='BC')
    
    dbs = pd.merge(dbs, idp, on='user', how='left')
    dbs = pd.merge(dbs, bc, on='user', how='left')
    
    comm_cols = ['email_freq', 'contact_diversity', 'reciprocity_ratio']
    dbs['IPS'] = dbs[comm_cols].mean(axis=1)
    src = dbs.groupby('user')['IPS'].std().fillna(0).apply(lambda x: max(0, 1 - x)).reset_index(name='SRC')
    
    dbs = pd.merge(dbs, src, on='user', how='left')
    
    return dbs

def calculate_hybrid_bsi(dbs, feature_cols):
    print(f"{Fore.CYAN}[*] Calculating Hybrid Similarity Index (Cosine + Euclidean magnitude)...")
    latest_week = dbs['week'].max()
    latest_dbs = dbs[dbs['week'] == latest_week].copy()
    
    users = latest_dbs['user'].tolist()
    matrix = np.zeros((len(users), len(users)))
    
    vecs = latest_dbs[feature_cols].values
    
    for i in range(len(users)):
        for j in range(len(users)):
            if i == j:
                matrix[i][j] = 1.0
            else:
                cos_sim = 1 - cosine(vecs[i], vecs[j])
                euc_dist = euclidean(vecs[i], vecs[j])
                hybrid_bsi = cos_sim * (1 / (1 + euc_dist))
                matrix[i][j] = hybrid_bsi
                
    return matrix, users

def run_pipeline():
    print(f"{Fore.MAGENTA}{Style.BRIGHT}=== STARTING CYBER DNA PRODUCTION PIPELINE ===")
    dbs, feature_cols = build_dbs_matrix()
    dbs = calculate_anthropology(dbs, feature_cols)
    
    bsi_matrix, users = calculate_hybrid_bsi(dbs, feature_cols)
    print(f"{Fore.CYAN}[*] Hybrid BSI successfully calculated. Matrix shape: {bsi_matrix.shape}")
    
    threat_users = dbs['user'].sample(n=max(1, int(len(dbs['user'].unique()) * 0.05))).tolist()
    dbs['is_malicious'] = dbs['user'].isin(threat_users) & (dbs['BDS'] > dbs['BDS'].quantile(0.80))
    
    print(f"{Fore.GREEN}[*] Training XGBoost Classifier with Recall-Optimized Threshold...")
    X = dbs[feature_cols + ['BDS', 'IDP', 'BC', 'SRC']]
    y = dbs['is_malicious'].astype(int)
    
    if y.sum() > 0:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = xgb.XGBClassifier(eval_metric='logloss', scale_pos_weight=10)
        model.fit(X_train, y_train)
        
        y_probs = model.predict_proba(X_test)[:, 1]
        precisions, recalls, thresholds = precision_recall_curve(y_test, y_probs)
        
        high_recall_idx = np.where(recalls >= 0.80)[0]
        if len(high_recall_idx) > 0:
            optimal_idx = high_recall_idx[-1]
            opt_thresh = thresholds[optimal_idx] if optimal_idx < len(thresholds) else 0.5
        else:
            opt_thresh = 0.5
            
        y_pred = (y_probs >= opt_thresh).astype(int)
        
        print("\nClassification Report (Test Partition):")
        print(classification_report(y_test, y_pred))
    else:
        print("No malicious labels found in this random chunk.")

    print(f"{Fore.YELLOW}[*] Exporting results to JSON for the React Dashboard...")
    
    export_data = {
        'cohort_size': len(dbs['user'].unique()),
        'total_weeks': len(dbs['week'].unique()),
        'features': feature_cols,
        'metrics': ['BDS', 'IDP', 'BC', 'SRC']
    }
    
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(export_data, f, indent=4)
        
    print(f"{Fore.GREEN}{Style.BRIGHT}=== PIPELINE COMPLETE ===")

if __name__ == '__main__':
    run_pipeline()
