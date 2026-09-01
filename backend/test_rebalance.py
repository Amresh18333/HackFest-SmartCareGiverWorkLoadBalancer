from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# Get Alex's ID
resp = client.get("/api/members")
members = resp.json()
alex = next((m for m in members if m["name"] == "Alex Chen"), None)
alex_id = alex["id"]
print(f"Alex ID: {alex_id}")

# Test recompute risk for Alex (should trigger rebalancing)
print("Recompute Alex's risk:")
resp = client.post(f"/api/members/{alex_id}/recompute-risk")
result = resp.json()
print(f"Score: {result['score']}")
if "rebalance_proposal" in result:
    print(f"Proposal created: {result['rebalance_proposal']['id']}")

# Check proposals
print("\nPending proposals:")
resp = client.get("/api/reassignments")
proposals = resp.json()
for p in proposals:
    print(f"  Task: {p.get('tasks', {}).get('title')}")
    print(f"  From: {p.get('from_member', {}).get('name')}")
    print(f"  To: {p.get('to_member', {}).get('name')}")
    print(f"  Reason: {p.get('reason')}")

# Accept the proposal
if proposals:
    proposal_id = proposals[0]["id"]
    print(f"\nAccepting proposal {proposal_id}:")
    resp = client.post(f"/api/reassignments/{proposal_id}/resolve", json={"status": "accepted"})
    print(resp.json())
    
    # Check Alex's tasks now
    print("\nAlex's tasks after reassignment:")
    resp = client.get(f"/api/members/{alex_id}")
    detail = resp.json()
    for t in detail["tasks"]:
        assignee_name = "Unknown"
        if t.get("assignee_id"):
            # Find assignee name
            for m in members:
                if m["id"] == t["assignee_id"]:
                    assignee_name = m["name"]
                    break
        print(f"  {t['title']} - {t['status']} - assignee: {assignee_name}")