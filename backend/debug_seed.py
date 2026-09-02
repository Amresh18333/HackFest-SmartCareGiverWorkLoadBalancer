import sys
sys.path.insert(0, '.')
from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()

# Clear and re-seed
import shutil
shutil.rmtree('mock_data', ignore_errors=True)

from scripts.seed_data import seed_members, seed_tasks, seed_risk_signals, seed_risk_scores, MEMBERS

member_ids = seed_members()
print(f"Member IDs: {member_ids}")

# Check roles after seed_members
from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
res = sb.table("team_members").select("id,name,role").execute()
print("\nAfter seed_members:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')