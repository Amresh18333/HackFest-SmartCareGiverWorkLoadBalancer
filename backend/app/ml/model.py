"""
Simple rule-based burnout risk model for hackathon MVP.
No training required - uses deterministic rules based on the spec.
"""
import numpy as np
from typing import Dict, List, Tuple

FEATURE_LABELS = {
    "tasks_today": "high task count today",
    "overdue_tasks": "overdue tasks piling up",
    "late_night_activity_flag": "late-night work activity",
    "avg_response_latency_mins": "slow response times",
    "consecutive_overloaded_days": "back-to-back overloaded days",
    "self_checkin_score": "low self check-in score"
}

PERSONAL_DRIVER_KEYS = {
    "self_checkin_score",
    "late_night_activity_flag",
    "avg_response_latency_mins",
}
PERSONAL_DRIVER_LABELS = {FEATURE_LABELS[k] for k in PERSONAL_DRIVER_KEYS}

def manager_visible_drivers(drivers: List[str]) -> List[str]:
    """Managers see workload drivers only — not personal check-in signals."""
    return [d for d in (drivers or []) if d not in PERSONAL_DRIVER_LABELS and d not in PERSONAL_DRIVER_KEYS]

def format_driver(driver_key: str) -> str:
    return FEATURE_LABELS.get(driver_key, driver_key.replace("_", " "))

def predict_risk(signals: Dict) -> Tuple[int, Dict[str, float]]:
    """
    Predict burnout risk score (0-100) from risk signals using deterministic rules.
    Returns (score, feature_importances_for_this_prediction)
    """
    # Extract signals with defaults
    tasks_today = signals.get("tasks_today", 0)
    overdue_tasks = signals.get("overdue_tasks", 0)
    late_night = signals.get("late_night_activity_flag", False)
    avg_latency = signals.get("avg_response_latency_mins", 0)
    consecutive_overloaded = signals.get("consecutive_overloaded_days", 0)
    self_checkin = signals.get("self_checkin_score", 3)
    
    # Base score components (each contributes 0-20 points)
    score = 0
    importances = {}
    
    # 1. Tasks today (0-20)
    task_score = min(tasks_today / 10.0, 1.0) * 20
    score += task_score
    importances["tasks_today"] = task_score / 20.0
    
    # 2. Overdue tasks (0-20)
    overdue_score = min(overdue_tasks / 5.0, 1.0) * 20
    score += overdue_score
    importances["overdue_tasks"] = overdue_score / 20.0
    
    # 3. Late night activity (0-15)
    late_night_score = 15 if late_night else 0
    score += late_night_score
    importances["late_night_activity_flag"] = late_night_score / 15.0
    
    # 4. Response latency (0-20)
    latency_score = min(avg_latency / 100.0, 1.0) * 20
    score += latency_score
    importances["avg_response_latency_mins"] = latency_score / 20.0
    
    # 5. Consecutive overloaded days (0-20) - strongest predictor
    consecutive_score = min(consecutive_overloaded / 7.0, 1.0) * 20
    score += consecutive_score
    importances["consecutive_overloaded_days"] = consecutive_score / 20.0
    
    # 6. Self check-in (inverted, 0-15)
    checkin_score = (5 - self_checkin) / 4.0 * 15
    score += checkin_score
    importances["self_checkin_score"] = checkin_score / 15.0
    
    # Normalize importances to sum to 1
    total = sum(importances.values())
    if total > 0:
        importances = {k: v/total for k, v in importances.items()}
    
    # Cap score at 100
    final_score = int(min(round(score), 100))
    
    return final_score, importances

def get_top_drivers(importances: Dict[str, float], n: int = 2) -> List[str]:
    """Get top N driver names for plain-language explanation."""
    sorted_features = sorted(importances.items(), key=lambda x: -x[1])
    return [f for f, _ in sorted_features[:n]]