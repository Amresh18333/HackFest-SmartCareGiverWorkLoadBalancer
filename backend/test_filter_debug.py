from app.db.supabase_client import get_supabase
sb = get_supabase()

table = sb.table('tasks')
print(f"Table data count: {len(table.data)}")
print(f"Table _query_filters before: {table._query_filters}")

# Set filter
task_id = '29c00b85-bdac-40a7-933a-d92afa00f253'
table._query_filters = [("eq", "id", task_id)]
print(f"Table _query_filters after set: {table._query_filters}")

# Check first item
item = table.data[0]
print(f"First item id: {item.get('id')}")
print(f"Match: {item.get('id') == task_id}")

# Set update data
table._update_data = {"assignee_id": "test"}
print(f"Table _update_data: {table._update_data}")

# Manually run filter logic
filters = table._query_filters
print(f"Filters in _execute_update: {filters}")
updated = []
for item in table.data:
    match = True
    for filter_item in filters:
        if filter_item[0] == "eq":
            _, field, value = filter_item
            print(f"  Checking {field} = {value} vs item {item.get(field)}")
            if item.get(field) != value:
                match = False
                break
    if match:
        print(f"  MATCH: {item.get('id')}")
        updated.append(item)
    else:
        print(f"  NO MATCH: {item.get('id')}")

print(f"\nMatched {len(updated)} items")