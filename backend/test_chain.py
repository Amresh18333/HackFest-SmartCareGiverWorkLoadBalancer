from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()

# Test the chain
table = sb.table("tasks")
print(f"Table id: {id(table)}")

# Simulate update().eq().execute()
result = table.update({"assignee_id": "test"}).eq("id", "test-id")
print(f"After update().eq(): {type(result)}")
print(f"Result _query_filters: {getattr(result, '_query_filters', 'N/A')}")
print(f"Result _update_data: {getattr(result, '_update_data', 'N/A')}")

# Check if it's the same table
print(f"Same table: {result is table}")