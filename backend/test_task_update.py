from app.db.supabase_client import get_supabase
sb = get_supabase()

# Check tasks before
print("Tasks before update:")
tasks = sb.table('tasks').select('*').eq('assignee_id', 'e8b9c1eb-8d53-42cf-835d-a5e950b52b15').execute()
for t in tasks.data:
    print(f'  {t["id"][:8]}: {t["title"]} (assignee: {t["assignee_id"][:8]})')

# Update one task
task_id = '48d1f589-9dfc-455b-9316-bd9687362e41'
new_assignee = '2dfba5bd-8ea6-4bba-a95f-8fb97895b9bb'
print(f"\nUpdating task {task_id[:8]} to assignee {new_assignee[:8]}")
table = sb.table('tasks')
table._query_filters = [("eq", "id", task_id)]
table._update_data = {"assignee_id": new_assignee}
result = table._execute_update()
print(f"Updated: {len(result.data)} items")

# Check after
print("\nTasks after update:")
tasks = sb.table('tasks').select('*').eq('assignee_id', 'e8b9c1eb-8d53-42cf-835d-a5e950b52b15').execute()
for t in tasks.data:
    print(f'  {t["id"][:8]}: {t["title"]} (assignee: {t["assignee_id"][:8]})')

tasks = sb.table('tasks').select('*').eq('assignee_id', '2dfba5bd-8ea6-4bba-a95f-8fb97895b9bb').execute()
for t in tasks.data:
    print(f'  {t["id"][:8]}: {t["title"]} (assignee: {t["assignee_id"][:8]})')