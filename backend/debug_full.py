import sys
sys.path.insert(0, '.')
import os
import shutil

mock_dir = os.path.join(os.path.dirname(__file__), 'mock_data')
shutil.rmtree(mock_dir, ignore_errors=True)
os.makedirs(mock_dir, exist_ok=True)

sys.path.insert(0, '.')
from app.db.supabase_client import get_supabase_admin
from scripts.seed_data import seed_members, MEMBERS

sb = get_supabase_admin()

print("=== FULL SEED DEBUG ===")

# Clear
shutil.rmtree('mock_data', ignore_errors=True)
os.makedirs(mock_dir, exist_ok=True)

sb = get_supabase_admin()

# 1. seed_members
print("\n=== seed_members ===")
member_ids = seed_members()
print(f"Member IDs: {member_ids}")

# Check after seed_members
res = sb.table("team_members").select("id,name,role").execute()
print("After seed_members:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')

# 2. Create manager
manager_data = {
    "name": "Demo Manager",
    "avatar_initials": "DM",
    "timezone": "America/Los_Angeles",
    "role": "manager"
}
manager_res = sb.table("team_members").insert(manager_data).execute()
manager_id = manager_res.data[0]["id"]
print(f"\nCreated manager: {manager_id}")

# Check after manager insert
res = sb.table("team_members").select("id,name,role").execute()
print("After manager insert:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')

# Create team
team_data = {
    "name": "Care Team Alpha",
    "manager_id": manager_id,
    "join_code": "DEMO1234"
}
team_res = sb.table("teams").insert(team_data).execute()
team = team_res.data[0]
team_id = team["id"]
print(f"\nCreated team: {team_id}")

# Assign members to team
print("\nAssigning members to team...")
for name, mid in member_ids.items():
    print(f"  Assigning {name} (id={mid})...")
    r = sb.table("team_members").update({"team_id": team_id, "role": "member"}).eq("id", mid).execute()
    print(f"  Result: {r.data}")

# Check after member assignment
res = sb.table("team_members").select("id,name,role,team_id").execute()
print("\nAfter member assignment:")
for m in res.data:
    print(f'  {m["name"]}: team_id={m.get("team_id")}, role={m.get("role")}')

# Assign manager
print(f"\nAssigning manager {manager_id} to team...")
r = sb.table("team_members").update({"team_id": team_id, "role": "manager"}).eq("id", manager_id).execute()
print(f"  Result: {r.data}")

# Final check
res = sb.table("team_members").select("id,name,role,team_id").execute()
print("\nFinal roles:")
for m in res.data:
    print(f'  {m["name"]}: team_id={m.get("team_id")}, role={m.get("role")}')