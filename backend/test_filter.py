from app.db.supabase_client import get_supabase
sb = get_supabase()

# Test the filter directly
table = sb.table("proposed_reassignments")
table._query_filters = [("eq", "id", "4e40e692-3e83-4600-be24-9fe75c61aff7")]
table._update_data = {"status": "test"}
result = table._execute_update()
print(f"Updated: {len(result.data)} items")
for item in result.data:
    print(f"  {item['id'][:8]}: status={item.get('status')}")

# Check all
props = sb.table('proposed_reassignments').select('*').execute()
print(f"\nAll proposals:")
for p in props.data:
    print(f'  {p["id"][:8]}: status={p.get("status")}')