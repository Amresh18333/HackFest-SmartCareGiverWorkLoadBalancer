from app.db.supabase_client import get_supabase
sb = get_supabase()

# Reset - reload from file
table = sb.table("proposed_reassignments")
print("Before update:")
for item in table.data:
    print(f"  {item['id'][:8]}: status={item.get('status')}")

# Test the filter directly
table._query_filters = [("eq", "id", "4e40e692-3e83-4600-be24-9fe75c61aff7")]
table._update_data = {"status": "test2"}
result = table._execute_update()
print(f"\nUpdated: {len(result.data)} items")

print("\nAfter update (in memory):")
for item in table.data:
    print(f"  {item['id'][:8]}: status={item.get('status')}")

# Check file
import json
with open(table.filepath) as f:
    file_data = json.load(f)
print("\nIn file:")
for item in file_data:
    print(f"  {item['id'][:8]}: status={item.get('status')}")