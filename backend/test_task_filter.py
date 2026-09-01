from app.db.supabase_client import get_supabase
sb = get_supabase()

# Check all tasks
tasks = sb.table('tasks').select('*').execute()
print(f"Total tasks: {len(tasks.data)}")
for t in tasks.data:
    print(f'  {t["id"]}: {t["title"]} (assignee: {t.get("assignee_id")})')

# Test update filter
task_id = '29c00b85-bdac-40a7-933a-d92afa00f253'  # Family communication log
print(f"\nUpdating task: {task_id}")
table = sb.table('tasks')
table._query_filters = [("eq", "id", task_id)]
table._update_data = {"assignee_id": "75ac7965-dc12-4c75-9216-6288d4c9821b"}  # Casey Brooks
result = table._execute_update()
print(f"Updated: {len(result.data)} items")

# Check after
tasks = sb.table('tasks').select('*').execute()
print(f"\nAfter update:")
for t in tasks.data:
    if t["assignee_id"] == "75ac7965-dc12-4c75-9216-6288d4c9821b":
        print(f'  {t["id"]}: {t["title"]} (assignee: {t.get("assignee_id")})')