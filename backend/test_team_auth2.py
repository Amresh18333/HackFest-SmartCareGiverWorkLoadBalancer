from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

print("=== Register Manager ===")
r = client.post("/api/auth/register", json={
    "email": "manager2@example.com",
    "password": "password123",
    "name": "Manager User",
    "avatar_initials": "MU",
    "is_manager": True,
    "team_name": "Care Team Alpha"
})
print(f"Status: {r.status_code}")
data = r.json()
print(data)

if "access_token" in data:
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get me
    print("\n=== Get Me ===")
    r = client.get("/api/auth/me", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.json())