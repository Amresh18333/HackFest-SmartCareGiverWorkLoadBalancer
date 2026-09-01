from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

print("=== Register new member ===")
r = client.post("/api/auth/register", json={
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "avatar_initials": "TU"
})
print(f"Status: {r.status_code}")
print(r.json())

print("\n=== Login ===")
r = client.post("/api/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
data = r.json()
print(f"Status: {r.status_code}")
print(data)

if "access_token" in data:
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current member
    print("\n=== Get Me ===")
    r = client.get("/api/auth/me", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.json())
    
    # Get my tasks
    print("\n=== My Tasks ===")
    r = client.get("/api/member/tasks", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.json())
    
    # Get my risk
    print("\n=== My Risk ===")
    r = client.get("/api/member/risk", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.json())
    
    # Submit daily signals
    print("\n=== Submit Daily Signals ===")
    r = client.post("/api/member/signals", headers=headers, json={
        "self_checkin_score": 3,
        "tasks_today": 5,
        "late_night_activity_flag": False,
        "avg_response_latency_mins": 30
    })
    print(f"Status: {r.status_code}")
    print(r.json())
    
    # Update task status (if tasks exist)
    tasks = client.get("/api/member/tasks", headers=headers).json()
    if tasks:
        task_id = tasks[0]["id"]
        print(f"\n=== Update Task {task_id} ===")
        r = client.patch(f"/api/member/tasks/{task_id}", headers=headers, json={
            "status": "in_progress"
        })
        print(f"Status: {r.status_code}")
        print(r.json())