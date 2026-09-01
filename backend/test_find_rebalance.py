from app.db.queries import find_rebalance_candidate, get_member_tasks, get_all_members
from app.db.supabase_client import get_supabase

sb = get_supabase()

# Check Alex's tasks
alex_id = "800d3876-4013-4f6a-a8e0-405d0d44e57d"
tasks = get_member_tasks(alex_id)
incomplete = [t for t in tasks if t["status"] != "done"]
print(f"Alex's incomplete tasks: {len(incomplete)}")
for t in incomplete:
    print(f"  {t['title']} - {t['priority']} - {t['status']}")

# Check all members
members = get_all_members()
print(f"\nAll members:")
for m in members:
    m_tasks = get_member_tasks(m["id"])
    m_incomplete = [t for t in m_tasks if t["status"] != "done"]
    total_hours = sum(t["estimated_hours"] for t in m_incomplete)
    print(f"  {m['name']}: {len(m_incomplete)} tasks, {total_hours:.1f}h")

# Try find_rebalance_candidate
print("\nTrying find_rebalance_candidate:")
proposal = find_rebalance_candidate(alex_id)
print(f"Proposal: {proposal}")