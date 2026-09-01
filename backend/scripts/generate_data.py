"""
Synthetic data generator for burnout risk model.
Generates ~2000 rows of risk_signals with labels for training.
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import os

np.random.seed(42)

# Configuration
N_MEMBERS = 5
N_DAYS = 120  # ~4 months of daily data per member
START_DATE = date(2025, 1, 1)

# Member profiles (some more prone to burnout)
MEMBER_PROFILES = [
    {"id": 0, "base_load": 3, "burnout_prone": False},   # Healthy
    {"id": 1, "base_load": 4, "burnout_prone": False},   # Moderate
    {"id": 2, "base_load": 5, "burnout_prone": True},    # Prone
    {"id": 3, "base_load": 3, "burnout_prone": False},   # Healthy
    {"id": 4, "base_load": 6, "burnout_prone": True},    # Very prone
]

def generate_synthetic_data():
    rows = []
    
    for profile in MEMBER_PROFILES:
        member_id = profile["id"]
        base_load = profile["base_load"]
        burnout_prone = profile["burnout_prone"]
        
        consecutive_overloaded = 0
        prev_latency = 30  # baseline response latency
        
        for day_offset in range(N_DAYS):
            current_date = START_DATE + timedelta(days=day_offset)
            
            # Daily variation in task load
            daily_load = max(0, int(np.random.normal(base_load, 1.5)))
            is_weekend = current_date.weekday() >= 5
            
            # Weekend effect
            if is_weekend:
                daily_load = max(0, daily_load - 2)
            
            # Overloaded day threshold
            overloaded = daily_load >= 6
            
            if overloaded:
                consecutive_overloaded += 1
            else:
                consecutive_overloaded = max(0, consecutive_overloaded - 1)
            
            # Overdue tasks accumulate when overloaded
            overdue = 0
            if consecutive_overloaded > 2:
                overdue = np.random.poisson(consecutive_overloaded - 1)
            
            # Late night activity more likely when overloaded
            late_night = overloaded and np.random.random() < 0.4
            
            # Response latency increases with load and consecutive overload
            latency_base = 20 + daily_load * 5 + consecutive_overloaded * 10
            if burnout_prone:
                latency_base *= 1.3
            avg_latency = max(5, np.random.normal(latency_base, 15))
            
            # Self check-in: lower when stressed
            checkin_base = 4 - (consecutive_overloaded * 0.5) - (daily_load - 3) * 0.3
            if burnout_prone:
                checkin_base -= 0.5
            checkin = int(np.clip(np.random.normal(checkin_base, 0.8), 1, 5))
            
            # Label: burnout = 1 if high consecutive overloaded days AND high latency
            # With noise so boundary isn't perfectly clean
            burnout_prob = 0.0
            if consecutive_overloaded > 3:
                burnout_prob += 0.4
            if avg_latency > 60:
                burnout_prob += 0.3
            if overdue > 2:
                burnout_prob += 0.2
            if checkin <= 2:
                burnout_prob += 0.15
            if burnout_prone:
                burnout_prob += 0.15
            
            # Add noise
            burnout_prob = np.clip(burnout_prob + np.random.normal(0, 0.1), 0, 1)
            burnout = 1 if np.random.random() < burnout_prob else 0
            
            rows.append({
                "member_id": member_id,
                "date": current_date,
                "tasks_today": daily_load,
                "overdue_tasks": overdue,
                "late_night_activity_flag": late_night,
                "avg_response_latency_mins": round(avg_latency, 1),
                "consecutive_overloaded_days": consecutive_overloaded,
                "self_checkin_score": checkin,
                "burnout": burnout
            })
    
    return pd.DataFrame(rows)

def train_model(df):
    """Train RandomForestClassifier on synthetic data."""
    feature_cols = [
        "tasks_today", "overdue_tasks", "late_night_activity_flag",
        "avg_response_latency_mins", "consecutive_overloaded_days", "self_checkin_score"
    ]
    
    X = df[feature_cols]
    y = df["burnout"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")
    
    # Feature importances
    importances = dict(zip(feature_cols, model.feature_importances_))
    print("\nFeature Importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        print(f"  {feat}: {imp:.3f}")
    
    return model, feature_cols

def save_model(model, feature_cols, path="backend/ml/burnout_model.joblib"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump({"model": model, "features": feature_cols}, path)
    print(f"\nModel saved to {path}")

if __name__ == "__main__":
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    print(f"Generated {len(df)} rows")
    print(f"Burnout rate: {df['burnout'].mean():.2%}")
    print(df["burnout"].value_counts())
    
    print("\nTraining model...")
    model, features = train_model(df)
    
    save_model(model, features)
    
    # Also save a sample for seeding Supabase
    df.to_csv("backend/scripts/synthetic_risk_signals.csv", index=False)
    print("Synthetic data saved to backend/scripts/synthetic_risk_signals.csv")