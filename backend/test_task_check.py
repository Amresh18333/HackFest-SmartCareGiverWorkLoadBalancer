from app.db.supabase_client import get_supabase
sb = get_supabase()

# Check all tasks
tasks = sb.table('tasks').select('*').execute()
print(f"Total tasks: {len(tasks.data)}")
for t in tasks.data:
    print(f'  {t["id"]}: {t["title"]} (assignee: {t.get("assignee_id")})')

# Check the specific task
task_id = '48d1f589-9dfc-455b-9316-bd9687362e41'
print(f"\nLooking for task: {task_id}")
for t in tasks.data:
    if t["id"] == task_id:
        print(f"Found: {t}")
        break