from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# Test recompute risk for Alex
print("Recompute Alex's risk:")
resp = client.post("/api/members/e8b9c1eb-8d53-42cf-835d-a5e950b52b15/recompute-risk")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")