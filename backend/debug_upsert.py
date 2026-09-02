import sys
sys.path.insert(0, '.')
import os
import shutil

# Clear and create mock_data
mock_dir = os.path.join(os.path.dirname(__file__), 'mock_data')
shutil.rmtree(mock_dir, ignore_errors=True)
os.makedirs(mock_dir, exist_ok=True)

sys.path.insert(0, '.')
from app.db.supabase_client import get_supabase_admin
from scripts.seed_data import seed_members, MEMBERS

print("=== Testing seed_members step by step ===")
sb = get_supabase_admin()

# Check initial state
print("Initial state:")
res = sb.table("team_members").select("*").execute()
print(f"  Records: {len(res.data)}")

# Step 1: upsert
print("\nStep 1: Upsert MEMBERS")
res = sb.table("team_members").upsert(MEMBERS, on_conflict="name").execute()
print(f"  Upsert result: {len(res.data)} records")

# Check after upsert
res = sb.table("team_members").select("id,name,role").execute()
print("After upsert:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')

# Step 2: explicit update
print("\nStep 2: Explicit update role=member")
for member in MEMBERS:
    sb.table("team_members").update({"role": "member"}).eq("name", member["name"]).execute()

# Check after update
res = sb.table("team_members").select("id,name,role").execute()
print("After explicit update:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')

# Check file
print("\nFile content:")
with open('mock_data/team_members.json', 'r') as f:
    import json
    data = json.load(f)
    for m in data:
        print(f'  {m["name"]}: role={m.get("role")}')