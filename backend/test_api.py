from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# Test health
print("Health:", client.get("/health").json())

# Test predict
print("\nPredict:")
resp = client.post("/api/predict", json={
    "tasks_today": 8, "overdue_tasks": 3, "late_night_activity_flag": True,
    "avg_response_latency_mins": 80, "consecutive_overloaded_days": 5, "self_checkin_score": 2
})
print(resp.json())

# Test members
print("\nMembers:")
resp = client.get("/api/members")
members = resp.json()
for m in members:
    print(f'  {m["name"]}: score={m["current_score"]}, risk={m["risk_level"]}')

# Test member detail
if members:
    member_id = members[0]["id"]
    print(f"\nMember detail ({member_id}):")
    resp = client.get(f"/api/members/{member_id}")
    detail = resp.json()
    print(f'  Name: {detail["name"]}')
    print(f'  Score: {detail["current_score"]}')
    print(f'  Drivers: {detail["top_drivers"]}')
    print(f'  History: {len(detail["score_history"])} days')
    print(f'  Tasks: {len(detail["tasks"])}')
    print(f'  Proposals: {len(detail["pending_reassignments"])}')

# Test summary
print("\nSummary:")
resp = client.post("/api/summary", json={
    "team_risk_summary": "1 high, 1 medium, 3 low risk",
    "top_concerns": ["Alex at 85", "Jordan at 72"]
})
print(resp.json())