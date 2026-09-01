from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# Get members
print("Members:")
resp = client.get("/api/members")
members = resp.json()
for m in members:
    print(f'  {m["name"]}: {m["id"]}')

# Test recompute for Alex
if members:
    alex = next((m for m in members if m["name"] == "Alex Chen"), None)
    if alex:
        print(f"\nRecompute {alex['name']}:")
        resp = client.post(f"/api/members/{alex['id']}/recompute-risk")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")