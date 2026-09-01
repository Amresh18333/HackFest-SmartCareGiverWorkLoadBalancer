from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# Get Alex's ID
resp = client.get("/api/members")
members = resp.json()
alex = next((m for m in members if m["name"] == "Alex Chen"), None)
alex_id = alex["id"]
print(f"Alex ID: {alex_id}")

# Test recompute risk for Alex
print("Recompute Alex's risk:")
resp = client.post(f"/api/members/{alex_id}/recompute-risk")
result = resp.json()
print(f"Status: {resp.status_code}")
print(f"Response: {result}")

# Check if proposal created
if "rebalance_proposal" in result:
    print(f"Proposal created: {result['rebalance_proposal']['id']}")
else:
    print("No proposal created")

# Check pending proposals
print("\nPending proposals:")
resp = client.get("/api/reassignments")
proposals = resp.json()
print(f"Count: {len(proposals)}")
for p in proposals:
    print(f"  Task: {p.get('tasks', {}).get('title')}")
    print(f"  From: {p.get('from_member', {}).get('name')}")
    print(f"  To: {p.get('to_member', {}).get('name')}")