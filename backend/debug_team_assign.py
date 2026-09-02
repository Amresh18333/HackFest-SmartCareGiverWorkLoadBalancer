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

print("=== Testing team assignment ===")

# Clear and create mock_data
shutil.rmtree('mock_data', ignore_errors=True)
os.makedirs('mock_data', exist_ok=True)

sb = get_supabase_admin()

print("=== Testing team assignment ===")

# Clear and seed members
shutil.rmtree('mock_data', ignore_errors=True)
os.makedirs('mock_data', exist_ok=True)

from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()

member_ids = seed_members()
print(f"Member IDs: {member_ids}")

# Check after seed_members
res = sb.table("team_members").select("id,name,role").execute()
print("\nAfter seed_members:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')

# Create team and assign members
manager_data = {
    "name": "Demo Manager",
    "avatar_initials": "DM",
    "timezone": "America/Los_Angeles",
    "role": "manager"
}
manager_res = sb.table("team_members").insert(manager_data).execute()
manager_id = manager_res.data[0]["id"]
print(f"\nCreated manager: {manager_id}")

team_data = {
    "name": "Care Team Alpha",
    "manager_id": manager_id,
    "join_code": "DEMO1234"
}
team_res = sb.table("teams").insert(team_data).execute()
team = team_res.data[0]
team_id = team["id"]
print(f"Created team: {team_id}")

# Assign members to team with role=member
print("\nAssigning members to team...")
for name, mid in member_ids.items():
    print(f"  Assigning {name} (id={mid}) to team {team_id} with role=member")
    r = sb.table("team_members").update({"team_id": team_id, "role": "member"}).eq("id", mid).execute()
    print(f"  Update result: {r.data}")

# Assign manager to team
print(f"\nAssigning manager {manager_id} to team with role=manager")
r = sb.table("team_members").update({"team_id": team_id, "role": "manager"}).eq("id", manager_id).execute()
print(f"  Update result: {r.data}")

# Check final roles
res = sb.table("team_members").select("id,name,role,team_id").execute()
print("\nFinal roles:")
for m in res.data:
    print(f'  {m["name"]}: team_id={m.get("team_id")}, role={m.get("role")}')