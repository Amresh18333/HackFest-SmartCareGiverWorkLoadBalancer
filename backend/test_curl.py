import requests

BASE = "http://localhost:8002/api"

print("=== Register Manager ===")
r = requests.post(f"{BASE}/auth/register", json={
    "email": "manager3@example.com",
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
    r = requests.get(f"{BASE}/auth/me", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.json())
    
    # Get my team
    print("\n=== Get My Team ===")
    r = requests.get(f"{BASE}/team/me", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.json())