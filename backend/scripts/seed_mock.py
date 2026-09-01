"""
Seed mock data for local development.
"""
import os
import sys
from datetime import date, timedelta
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.supabase_client import get_supabase_admin
from app.ml.model import predict_risk, get_top_drivers, format_driver

sb = get_supabase_admin()

# Demo team members
MEMBERS = [
    {"name": "Alex Chen", "avatar_initials": "AC", "timezone": "America/Los_Angeles"},
    {"name": "Jordan Kim", "avatar_initials": "JK", "timezone": "America/New_York"},
    {"name": "Sam Rivera", "avatar_initials": "SR", "timezone": "America/Chicago"},
    {"name": "Taylor Moore", "avatar_initials": "TM", "timezone": "America/Denver"},
    {"name": "Casey Brooks", "avatar_initials": "CB", "timezone": "America/Toronto"},
]

def seed_members():
    print("Seeding team members...")
    res = sb.table("team_members").upsert(MEMBERS, on_conflict="name").execute()
    return {m["name"]: m["id"] for m in res.data}

def seed_tasks(member_ids):
    print("Seeding tasks...")
    tasks = [
        {"title": "Patient intake review", "assignee_id": member_ids["Alex Chen"], "priority": "high", "status": "in_progress", "estimated_hours": 3.0, "due_date": (date.today() + timedelta(days=1)).isoformat()},
        {"title": "Care plan updates (5 patients)", "assignee_id": member_ids["Alex Chen"], "priority": "high", "status": "todo", "estimated_hours": 4.0, "due_date": (date.today() + timedelta(days=2)).isoformat()},
        {"title": "Medication reconciliation", "assignee_id": member_ids["Alex Chen"], "priority": "medium", "status": "todo", "estimated_hours": 2.5, "due_date": (date.today() + timedelta(days=3)).isoformat()},
        {"title": "Family communication log", "assignee_id": member_ids["Alex Chen"], "priority": "low", "status": "todo", "estimated_hours": 1.0, "due_date": (date.today() + timedelta(days=5)).isoformat()},
        {"title": "Weekly schedule coordination", "assignee_id": member_ids["Alex Chen"], "priority": "medium", "status": "in_progress", "estimated_hours": 2.0, "due_date": (date.today() + timedelta(days=1)).isoformat()},
        {"title": "New patient onboarding", "assignee_id": member_ids["Jordan Kim"], "priority": "high", "status": "in_progress", "estimated_hours": 3.0, "due_date": (date.today() + timedelta(days=2)).isoformat()},
        {"title": "Discharge planning", "assignee_id": member_ids["Jordan Kim"], "priority": "medium", "status": "todo", "estimated_hours": 2.0, "due_date": (date.today() + timedelta(days=4)).isoformat()},
        {"title": "Equipment requests", "assignee_id": member_ids["Jordan Kim"], "priority": "low", "status": "todo", "estimated_hours": 1.0, "due_date": (date.today() + timedelta(days=7)).isoformat()},
        {"title": "Documentation audit", "assignee_id": member_ids["Sam Rivera"], "priority": "low", "status": "todo", "estimated_hours": 2.0, "due_date": (date.today() + timedelta(days=10)).isoformat()},
        {"title": "Training module completion", "assignee_id": member_ids["Sam Rivera"], "priority": "low", "status": "in_progress", "estimated_hours": 1.5, "due_date": (date.today() + timedelta(days=14)).isoformat()},
        {"title": "Shift handoff prep", "assignee_id": member_ids["Taylor Moore"], "priority": "medium", "status": "in_progress", "estimated_hours": 2.0, "due_date": (date.today() + timedelta(days=1)).isoformat()},
        {"title": "Incident report review", "assignee_id": member_ids["Taylor Moore"], "priority": "high", "status": "todo", "estimated_hours": 1.5, "due_date": (date.today() + timedelta(days=3)).isoformat()},
        {"title": "Supply inventory check", "assignee_id": member_ids["Taylor Moore"], "priority": "low", "status": "todo", "estimated_hours": 1.0, "due_date": (date.today() + timedelta(days=7)).isoformat()},
        {"title": "Care team meeting prep", "assignee_id": member_ids["Casey Brooks"], "priority": "medium", "status": "todo", "estimated_hours": 1.5, "due_date": (date.today() + timedelta(days=2)).isoformat()},
        {"title": "Patient education materials", "assignee_id": member_ids["Casey Brooks"], "priority": "low", "status": "in_progress", "estimated_hours": 2.0, "due_date": (date.today() + timedelta(days=5)).isoformat()},
    ]
    res = sb.table("tasks").upsert(tasks, on_conflict="title,assignee_id").execute()
    return res.data

def generate_risk_signals(member_id, member_name, days=60):
    signals = []
    base_date = date.today() - timedelta(days=days)
    
    if member_name == "Alex Chen":
        for i in range(days):
            d = base_date + timedelta(days=i)
            if i < 30:
                tasks_today = random.randint(3, 5)
                consecutive = 0
                overdue = 0
                latency = random.uniform(20, 40)
                late_night = random.random() < 0.1
                checkin = random.randint(3, 5)
            else:
                tasks_today = random.randint(6, 9)
                consecutive = min(i - 30, 8)
                overdue = max(0, consecutive - 2)
                latency = random.uniform(60, 120)
                late_night = random.random() < 0.5
                checkin = max(1, 4 - consecutive // 2)
            
            signals.append({
                "member_id": member_id, "date": d.isoformat(),
                "tasks_today": tasks_today, "overdue_tasks": overdue,
                "late_night_activity_flag": late_night,
                "avg_response_latency_mins": round(latency, 1),
                "consecutive_overloaded_days": consecutive,
                "self_checkin_score": checkin
            })
    
    elif member_name == "Jordan Kim":
        for i in range(days):
            d = base_date + timedelta(days=i)
            if i < 45:
                tasks_today = random.randint(3, 5)
                consecutive = 0; overdue = 0
                latency = random.uniform(25, 45)
                late_night = random.random() < 0.1
                checkin = random.randint(3, 5)
            else:
                tasks_today = random.randint(6, 8)
                consecutive = min(i - 45, 4)
                overdue = max(0, consecutive - 1)
                latency = random.uniform(50, 90)
                late_night = random.random() < 0.3
                checkin = max(2, 4 - consecutive)
            
            signals.append({
                "member_id": member_id, "date": d.isoformat(),
                "tasks_today": tasks_today, "overdue_tasks": overdue,
                "late_night_activity_flag": late_night,
                "avg_response_latency_mins": round(latency, 1),
                "consecutive_overloaded_days": consecutive,
                "self_checkin_score": checkin
            })
    
    elif member_name == "Sam Rivera":
        for i in range(days):
            d = base_date + timedelta(days=i)
            signals.append({
                "member_id": member_id, "date": d.isoformat(),
                "tasks_today": random.randint(2, 4), "overdue_tasks": 0,
                "late_night_activity_flag": random.random() < 0.05,
                "avg_response_latency_mins": round(random.uniform(15, 30), 1),
                "consecutive_overloaded_days": 0,
                "self_checkin_score": random.randint(4, 5)
            })
    
    elif member_name == "Taylor Moore":
        for i in range(days):
            d = base_date + timedelta(days=i)
            signals.append({
                "member_id": member_id, "date": d.isoformat(),
                "tasks_today": random.randint(3, 5),
                "overdue_tasks": random.randint(0, 1),
                "late_night_activity_flag": random.random() < 0.15,
                "avg_response_latency_mins": round(random.uniform(20, 50), 1),
                "consecutive_overloaded_days": random.randint(0, 1),
                "self_checkin_score": random.randint(3, 4)
            })
    
    else:  # Casey Brooks
        for i in range(days):
            d = base_date + timedelta(days=i)
            signals.append({
                "member_id": member_id, "date": d.isoformat(),
                "tasks_today": random.randint(3, 6),
                "overdue_tasks": random.randint(0, 2),
                "late_night_activity_flag": random.random() < 0.2,
                "avg_response_latency_mins": round(random.uniform(25, 60), 1),
                "consecutive_overloaded_days": random.randint(0, 2),
                "self_checkin_score": random.randint(3, 5)
            })
    
    return signals

def seed_risk_signals(member_ids):
    print("Seeding risk signals...")
    all_signals = []
    for name, mid in member_ids.items():
        signals = generate_risk_signals(mid, name)
        all_signals.extend(signals)
    
    batch_size = 500
    for i in range(0, len(all_signals), batch_size):
        batch = all_signals[i:i+batch_size]
        sb.table("risk_signals").upsert(batch, on_conflict="member_id,date").execute()
        print(f"  Inserted {min(i+batch_size, len(all_signals))}/{len(all_signals)} signals")

def seed_risk_scores(member_ids):
    print("Computing and seeding risk scores...")
    for name, mid in member_ids.items():
        res = sb.table("risk_signals").select("*").eq("member_id", mid).order("date").execute()
        signals_list = res.data
        
        for sig in signals_list:
            signal_data = {k: v for k, v in sig.items() 
                          if k not in ["id", "member_id", "date", "created_at"]}
            score, importances = predict_risk(signal_data)
            top_drivers = get_top_drivers(importances)
            driver_texts = [format_driver(d) for d in top_drivers]
            
            risk_score = {
                "member_id": mid, "date": sig["date"],
                "score": score, "top_drivers": driver_texts
            }
            sb.table("risk_scores").upsert(risk_score, on_conflict="member_id,date").execute()
    
    print("Risk scores computed and stored")

def main():
    print("=" * 50)
    print("Seeding Smart Caregiver Workload Balancer Mock Data")
    print("=" * 50)
    
    member_ids = seed_members()
    print(f"Created {len(member_ids)} team members")
    seed_tasks(member_ids)
    print("Tasks seeded")
    seed_risk_signals(member_ids)
    print("Risk signals seeded")
    seed_risk_scores(member_ids)
    print("Risk scores computed")
    
    print("\n✅ Seeding complete!")
    print("  - Alex Chen: Trending to HIGH risk (~85)")
    print("  - Jordan Kim: MEDIUM risk (~72)")
    print("  - Sam Rivera: LOW risk (~15)")
    print("  - Taylor Moore: LOW-MEDIUM risk (~35)")
    print("  - Casey Brooks: MEDIUM risk (~45)")

if __name__ == "__main__":
    main()