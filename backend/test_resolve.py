from app.db.supabase_client import get_supabase
from app.db.queries import resolve_proposal

sb = get_supabase()

# Check current proposals
props = sb.table('proposed_reassignments').select('*').execute()
print(f"Before resolve: {len(props.data)} proposals")
for p in props.data:
    print(f'  {p["id"][:8]}: status={p.get("status")}, task={p["task_id"][:8]}')

# Resolve the first one
if props.data:
    proposal_id = props.data[0]["id"]
    print(f"\nResolving {proposal_id}...")
    result = resolve_proposal(proposal_id, "accepted")
    print(f"Result: {result}")

# Check again
props = sb.table('proposed_reassignments').select('*').execute()
print(f"\nAfter resolve: {len(props.data)} proposals")
for p in props.data:
    print(f'  {p["id"][:8]}: status={p.get("status")}, task={p["task_id"][:8]}')