import sys
import os
sys.path.insert(0, '.')
import shutil

# Clear and create mock_data in the correct location
mock_dir = os.path.join(os.path.dirname(__file__), 'mock_data')
shutil.rmtree(mock_dir, ignore_errors=True)
os.makedirs(mock_dir, exist_ok=True)

sys.path.insert(0, '.')
from app.db.supabase_client import get_supabase_admin
from scripts.seed_data import seed_members, MEMBERS

print("=== Testing seed_members ===")
member_ids = seed_members()
print(f"Member IDs: {member_ids}")

# Check roles after seed_members
from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
res = sb.table("team_members").select("id,name,role").execute()
print("\nAfter seed_members:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')