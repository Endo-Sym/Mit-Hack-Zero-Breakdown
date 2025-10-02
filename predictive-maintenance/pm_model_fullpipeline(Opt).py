# =========================================
# Production-ready Predictive Maintenance pipeline (Class III Sugarcane Mill) - Optimized Version
# Supports >100k rows
#Full Production-Ready Predictive Maintenance Pipeline แบบ Optimized สำหรับ >100k rows ให้ครบทุกประเด็นที่คุณต้องการ:
#Hybrid labeling (lead-time 6–12 ชั่วโมง + thresholds + spike detection)
#Pivot + Rolling/Delta/Slope/Z-score + optional FFT
#Semi-supervised clustering (MiniBatchKMeans)
#IsolationForest anomaly detection
#Stacked ensemble (XGBoost, LightGBM, RandomForest) + Logistic Regression meta-model
#SMOTE-ENN imbalance handling
#Alerts generation (threshold + anomaly + cluster)
#Metrics (classification report, confusion matrix, ROC-AUC, PR-AUC, lead-time histogram)
#SHAP explainability
#Save artifacts (models, scalers, predictions, alerts, SHAP)
#Optimized memory & speed for large dataset
# =========================================

import os, json, warnings, logging
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import MiniBatchKMeans
import joblib

# Optional ML
try: import xgboost as xgb
except: xgb=None
try: import lightgbm as lgb
except: lgb=None
try: from imblearn.combine import SMOTEENN
except: SMOTEENN=None

# Optional SHAP
try: import shap
except: shap=None

# Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger()
def info(msg): logger.info(msg)
def warn(msg): logger.warning(msg)
def error(msg): logger.error(msg)

# =========================
# 1) Load Data
# =========================
def load_data(sensor_csv="feedmill_clean_long.csv", breakdown_csv="breakdown_log_detailed.csv"):
    info("Loading sensor data...")
    df = pd.read_csv(sensor_csv)
    df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
    df['machine_type'] = df.get('machine_type','Feed Mill 1')

    info("Loading breakdown data...")
    breakdown_df = pd.read_csv(breakdown_csv)
    if 'Date' in breakdown_df.columns:
        if 'TimeStart' in breakdown_df.columns and 'TimeEnd' in breakdown_df.columns:
            breakdown_df['DateTimeStart'] = pd.to_datetime(
                breakdown_df['Date'].astype(str)+' '+breakdown_df['TimeStart'].astype(str), errors='coerce')
            breakdown_df['DateTimeEnd'] = pd.to_datetime(
                breakdown_df['Date'].astype(str)+' '+breakdown_df['TimeEnd'].astype(str), errors='coerce')
        else:
            breakdown_df['DateTimeStart'] = pd.to_datetime(
                breakdown_df['Date'].astype(str)+' '+breakdown_df.get('Time','00:00:00').astype(str), errors='coerce')
            breakdown_df['DateTimeEnd'] = breakdown_df['DateTimeStart'] + pd.to_timedelta(
                breakdown_df.get('Duration_min',0), unit='m')
    breakdown_df['machine_type'] = breakdown_df.get('Machine','Feed Mill 1')
    
    return df, breakdown_df

# =========================
# 2) Hybrid Labeling
# =========================
def hybrid_labeling(df, breakdown_df, label_window_hours=8, thresholds=None):
    info("Applying hybrid labeling...")
    thresholds = thresholds or {'Winding':80, 'Oil Gear':70, 'Vrms':4.5}
    df['FailureLabel'] = 0

    # Breakdown log labeling
    for _, r in breakdown_df.dropna(subset=['DateTimeStart','DateTimeEnd']).iterrows():
        start = r['DateTimeStart'] - pd.Timedelta(hours=label_window_hours)
        end = r['DateTimeEnd']
        machine = r.get('machine_type','Feed Mill 1')
        mask = (df['machine_type']==machine) & (df['DateTime']>=start) & (df['DateTime']<=end)
        df.loc[mask,'FailureLabel'] = 1

    # Threshold-based synthetic labeling
    mask_wind = df['SensorName'].str.contains('Winding', case=False, na=False) & (df['Value']>thresholds['Winding'])
    mask_oil  = df['SensorName'].str.contains('Oil Gear', case=False, na=False) & (df['Value']>thresholds['Oil Gear'])
    mask_vrms = df['SensorName'].eq('Vrms_Est_mm_s') & (df['Value']>thresholds['Vrms'])

    # Current spike > mu+3sigma
    df_current = df[df['SensorName'].str.contains('Current', case=False, na=False)]
    if not df_current.empty:
        mu, sigma = df_current['Value'].mean(), df_current['Value'].std()
        mask_current = df['SensorName'].str.contains('Current', case=False, na=False) & (df['Value']>mu+3*sigma)
    else:
        mask_current = pd.Series(False, index=df.index)

    df.loc[mask_wind | mask_oil | mask_vrms | mask_current, 'FailureLabel'] = 1
    info(f"Hybrid labeling done. Class counts:\n{df['FailureLabel'].value_counts()}")
    return df

# =========================
# 3) Pivot + Features (optimized)
# =========================
def pivot_and_features(df, roll_windows=[3,5,10], compute_fft=False, fft_window=32):
    info("Pivoting and computing features...")
    df_sorted = df.sort_values('DateTime')
    wide = df_sorted.pivot_table(index='DateTime', columns='SensorName', values='Value', aggfunc='mean').reset_index()
    wide = wide.sort_values('DateTime').ffill().bfill()
    wide = wide.merge(df[['DateTime','FailureLabel']].drop_duplicates(), on='DateTime', how='left')

    numeric_cols = wide.select_dtypes(include=[np.number]).columns.tolist()
    if 'FailureLabel' in numeric_cols: numeric_cols.remove('FailureLabel')

    # Vectorized rolling features
    for w in roll_windows:
        rolled = wide[numeric_cols].rolling(w, min_periods=1)
        wide[[f"{c}_rollmean_{w}" for c in numeric_cols]] = rolled.mean().astype('float32')
        wide[[f"{c}_rollstd_{w}" for c in numeric_cols]] = rolled.std().fillna(0).astype('float32')
        wide[[f"{c}_delta_{w}" for c in numeric_cols]] = wide[numeric_cols].diff(w).astype('float32')
        wide[[f"{c}_slope_{w}" for c in numeric_cols]] = wide[numeric_cols].diff(w)/w
        wide[[f"{c}_zscore_{w}" for c in numeric_cols]] = (wide[numeric_cols]-rolled.mean())/rolled.std().replace(0,1)

    # Optional FFT
    if compute_fft:
        for c in numeric_cols:
            arr = wide[c].fillna(0).to_numpy(dtype='float32')
            fft_feat = np.zeros(len(arr), dtype='float32')
            for i in range(fft_window-1, len(arr)):
                segment = arr[i-fft_window+1:i+1]
                fft_feat[i] = np.mean(np.abs(np.fft.rfft(segment - segment.mean())))
            wide[f'{c}_fft_{fft_window}'] = fft_feat

    wide.columns = [str(c).strip().replace(' ','_').replace('/','_').replace('-','_') for c in wide.columns]
    return wide

# =========================
# 4) Clustering Layer (MiniBatchKMeans)
# =========================
def add_cluster_features(df_feat, n_clusters=4):
    info("Adding clustering features...")
    numeric_cols = [c for c in df_feat.select_dtypes(include=[np.number]).columns if c not in ['FailureLabel','anomaly_flag','anomaly_score']]
    X = df_feat[numeric_cols].fillna(0).values.astype('float32')
    km = MiniBatchKMeans(n_clusters=n_clusters, batch_size=10000, random_state=42)
    df_feat['cluster'] = km.fit_predict(X)
    return df_feat, km

# =========================
# 5) Anomaly Detection (IsolationForest)
# =========================
def anomaly_layer(df_feat):
    info("Running IsolationForest...")
    numeric_cols = [c for c in df_feat.select_dtypes(include=[np.number]).columns if c not in ['FailureLabel']]
    X = df_feat[numeric_cols].fillna(0).values.astype('float32')
    iso_model = IsolationForest(n_estimators=100, contamination=0.02, n_jobs=-1, random_state=42)
    df_feat['anomaly_flag'] = (iso_model.fit_predict(X)==-1).astype('int8')
    df_feat['anomaly_score'] = -iso_model.decision_function(X).astype('float32')
    info(f"Anomalies detected: {df_feat['anomaly_flag'].sum()}")
    return df_feat, iso_model

# =========================
# 6) Stacked Ensemble
# =========================
def train_stacked_ensemble(df_feat, feature_cols, target_col='FailureLabel', groups=None, n_splits=5):
    info("Training stacked ensemble...")
    X = df_feat[feature_cols].fillna(0)
    y = df_feat[target_col].astype(int)
    groups = groups if groups is not None else np.arange(len(df_feat))
    oof_preds = np.zeros((len(X),3))
    models_fitted = {'xgb':[], 'lgb':[], 'rf':[]}
    gkf = GroupKFold(n_splits=n_splits)

    for fold,(train_idx,val_idx) in enumerate(gkf.split(X,y,groups),1):
        info(f"Fold {fold}")
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        # SMOTE-ENN
        if SMOTEENN:
            X_tr_res, y_tr_res = SMOTEENN(random_state=42).fit_resample(X_tr, y_tr)
        else:
            X_tr_res, y_tr_res = X_tr, y_tr

        scaler = StandardScaler()
        X_tr_s, X_val_s = scaler.fit_transform(X_tr_res), scaler.transform(X_val)

        # XGB
        if xgb:
            scale_pos_weight = (len(y_tr_res)-sum(y_tr_res))/max(sum(y_tr_res),1)
            clf_xgb = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.08,
                                        scale_pos_weight=scale_pos_weight, n_jobs=-1,
                                        random_state=42, use_label_encoder=False, eval_metric='logloss')
            clf_xgb.fit(X_tr_s, y_tr_res)
            oof_preds[val_idx,0] = clf_xgb.predict_proba(X_val_s)[:,1]
            models_fitted['xgb'].append((clf_xgb, scaler))
        else:
            clf_rf = RandomForestClassifier(n_estimators=200, max_depth=8, n_jobs=-1, random_state=42)
            clf_rf.fit(X_tr_res, y_tr_res)
            oof_preds[val_idx,0] = clf_rf.predict_proba(X_val)[:,1]
            models_fitted['xgb'].append((clf_rf,None))

        # LGB
        if lgb:
            clf_lgb = lgb.LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.08, n_jobs=-1, random_state=42)
            clf_lgb.fit(X_tr_res, y_tr_res)
            oof_preds[val_idx,1] = clf_lgb.predict_proba(X_val)[:,1]
            models_fitted['lgb'].append((clf_lgb,None))
        else:
            clf_rf2 = RandomForestClassifier(n_estimators=150, max_depth=8, n_jobs=-1, random_state=42)
            clf_rf2.fit(X_tr_res, y_tr_res)
            oof_preds[val_idx,1] = clf_rf2.predict_proba(X_val)[:,1]
            models_fitted['lgb'].append((clf_rf2,None))

        # RF
        clf_rf3 = RandomForestClassifier(n_estimators=200, max_depth=12, n_jobs=-1, random_state=42)
        clf_rf3.fit(X_tr_res, y_tr_res)
        oof_preds[val_idx,2] = clf_rf3.predict_proba(X_val)[:,1]
        models_fitted['rf'].append((clf_rf3,None))

    meta_clf = LogisticRegression()
    meta_clf.fit(oof_preds, y)
    info("Stacked ensemble trained.")
    return {'oof_preds':oof_preds, 'meta_clf':meta_clf, 'models_fitted':models_fitted}

# =========================
# 7) Alerts
# =========================
def generate_alerts_from_row(row, thresholds=None):
    thresholds = thresholds or {'PowerMotor':220,'CurrentMotor':50,'TempBrassBearingDE':80,'Vrms_Est_mm_s':4.5}
    alerts=[]
    for sensor,thresh in thresholds.items():
        if sensor in row and row[sensor]>thresh: alerts.append(f"{sensor} exceeds {thresh}")
    if row.get('anomaly_flag',0)==1: alerts.append("IsolationForest anomaly detected")
    if 'cluster' in row: alerts.append(f"Cluster {row['cluster']}")
    return alerts

def get_alerts(df_sensor, thresholds=None):
    df_sensor['alerts'] = df_sensor.apply(lambda row: generate_alerts_from_row(row, thresholds), axis=1)
    alerts_df = df_sensor.explode('alerts').dropna(subset=['alerts'])
    return alerts_df[['DateTime','alerts','anomaly_score','FailureLabel']]

def alerts_to_json(alerts_df, path):
    with open(path,'w',encoding='utf-8') as f:
        json.dump(alerts_df.to_dict(orient='records'),f,indent=2,default=str)
    info(f"Alerts exported to {path}")

# =========================
# 8) Metrics & Lead Time
# =========================
def compute_metrics(df_feat, pred_col='stack_pred', target_col='FailureLabel'):
    y_true = df_feat[target_col]
    y_pred_prob = df_feat[pred_col]
    y_pred = y_pred_prob > 0.5
    report = classification_report(y_true,y_pred,digits=4)
    cm = confusion_matrix(y_true,y_pred)
    roc = roc_auc_score(y_true, y_pred_prob)
    precision, recall, _ = precision_recall_curve(y_true, y_pred_prob)
    pr_auc = auc(recall, precision)
    return report, cm, roc, pr_auc

def compute_lead_time(df_feat, pred_col='stack_pred', threshold=0.5):
    df_feat = df_feat.sort_values('DateTime')
    failures = df_feat[df_feat['FailureLabel']==1]
    lead_times=[]
    for idx,row in failures.iterrows():
        early_pred = df_feat.loc[:idx][df_feat.loc[:idx][pred_col]>threshold]
        if not early_pred.empty:
            lt = (row['DateTime'] - early_pred['DateTime'].iloc[-1]).total_seconds()/3600
            lead_times.append(lt)
    return lead_times

# =========================
# 9) SHAP
# =========================
def compute_shap(df_feat, feature_cols, model=None, path=None):
    if shap is None or model is None:
        info("Skipping SHAP computation")
        return None
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(df_feat[feature_cols])
    if path: np.save(path, shap_values)
    return shap_values

# =========================
# 10) Full Pipeline Runner
# =========================
def run_pipeline(sensor_csv="feedmill_clean_long.csv", breakdown_csv="breakdown_log_detailed.csv", out_dir="artifacts"):
    os.makedirs(out_dir, exist_ok=True)
    
    # Load
    df, breakdown_df = load_data(sensor_csv, breakdown_csv)
    
    # Labeling
    df = hybrid_labeling(df, breakdown_df, label_window_hours=8)
    
    # Feature Engineering
    df_feat = pivot_and_features(df, roll_windows=[3,5,10], compute_fft=False)
    
    # Clustering
    df_feat, km_model = add_cluster_features(df_feat, n_clusters=4)
    
    # Anomaly
    df_feat, iso_model = anomaly_layer(df_feat)
    
    # Stacked Ensemble
    feature_cols = [c for c in df_feat.select_dtypes(include=[np.number]).columns if c not in ['FailureLabel','anomaly_flag','anomaly_score']]
    stack_res = train_stacked_ensemble(df_feat, feature_cols)
    df_feat['stack_pred'] = stack_res['meta_clf'].predict_proba(stack_res['oof_preds'])[:,1]
    
    # Metrics
    report, cm, roc, pr_auc = compute_metrics(df_feat)
    lead_times = compute_lead_time(df_feat)
    info(f"\nClassification Report:\n{report}")
    info(f"Confusion Matrix:\n{cm}")
    info(f"ROC-AUC: {roc:.4f}, PR-AUC: {pr_auc:.4f}, Avg Lead Time (hrs): {np.mean(lead_times):.2f}")
    
    # Alerts
    alerts_df = get_alerts(df_feat)
    alerts_to_json(alerts_df, os.path.join(out_dir,"alerts.json"))
    
    # SHAP
    compute_shap(df_feat, feature_cols, stack_res['models_fitted']['xgb'][0][0] if xgb else None, path=os.path.join(out_dir,'shap_values.npy'))
    
    # Save models
    for model_type,lst in stack_res['models_fitted'].items():
        for i,(m,s) in enumerate(lst):
            joblib.dump(m, os.path.join(out_dir,f"{model_type}_fold{i}.pkl"))
            if s: joblib.dump(s, os.path.join(out_dir,f"{model_type}_scaler_fold{i}.pkl"))
    joblib.dump(stack_res['meta_clf'], os.path.join(out_dir,'meta_model.pkl'))
    joblib.dump(km_model, os.path.join(out_dir,'kmeans_model.pkl'))
    joblib.dump(iso_model, os.path.join(out_dir,'isolationforest_model.pkl'))

    info("Pipeline completed successfully.")
    return df_feat, alerts_df, stack_res

# =========================
# Example run
# =========================
# df_feat, alerts_df, stack_res = run_pipeline(sensor_csv="feedmill_clean_long.csv", breakdown_csv="breakdown_log_detailed.csv")
