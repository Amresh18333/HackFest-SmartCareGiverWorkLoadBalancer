from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

print("=== Register Manager ===")
r = client.post("/api/auth/register", json={
    "email": "manager@example.com",
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
    
    # Get my team
    print("\n=== Get My Team ===")
    r = client.get("/api/team/me", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.json())
    
    # Create team (should already be created)
    print("\n=== Create Team ===")
    r = client.post("/api/team/create", headers=headers, json={
        "team_name": "Care Team Alpha"
    })
    print(f"Status: {r.status_code}")
    print(r.json())
    
    # Register member
    print("\n=== Register Member ===")
    r = client.post("/api/auth/register", json={
        "email": "member@example.com",
        "password": "password123",
        "name": "Member User",
        "avatar_initials": "MB"
    })
    print(f"Status: {r.status_code}")
    member_data = r.json()
    print(member_data)
    
    if "access_token" in member_data:
        member_token = member_data["access_token"]
        member_headers = {"Authorization": f"Bearer {member_token}"}
        
        # Join team
        join_code = data.get("member", {}).get("join_code") or data.get("team", {}).get("join_code")
        # Get join code from team
        r = client.get("/api/team/me", headers=headers)
        team_data = r.json()
        join_code = team_data.get("team", {}).get("join_code")
        print(f"\nJoin code: {join_code}")
        
        print("\n=== Member Join Team ===")
        r = client.post("/api/team/join", headers=member_headers, json={
            "join_code": join_code
        })
        print(f"Status: {r.status_code}")
        print(r.json())
        
        # Get member's team
        print("\n=== Member Get Team ===")
        r = client.get("/api/team/me", headers=member_headers)
        print(f"Status: {r.status_code}")
        print(r.json())