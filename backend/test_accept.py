from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# Get Alex's ID
resp = client.get("/api/members")
members = resp.json()
alex = next((m for m in members if m["name"] == "Alex Chen"), None)
alex_id = alex["id"]
print(f"Alex ID: {alex_id}")

# Get proposal
resp = client.get("/api/reassignments")
proposals = resp.json()
proposal_id = proposals[0]["id"]
print(f"Proposal ID: {proposal_id}")

# Accept the proposal
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
        for m in members:
            if m["id"] == t["assignee_id"]:
                assignee_name = m["name"]
                break
    print(f"  {t['title']} - {t['status']} - assignee: {assignee_name}")

# Check Casey's tasks
casey = next((m for m in members if m["name"] == "Casey Brooks"), None)
print(f"\nCasey's tasks:")
resp = client.get(f"/api/members/{casey['id']}")
detail = resp.json()
for t in detail["tasks"]:
    assignee_name = "Unknown"
    if t.get("assignee_id"):
        for m in members:
            if m["id"] == t["assignee_id"]:
                assignee_name = m["name"]
                break
    print(f"  {t['title']} - {t['status']} - assignee: {assignee_name}")