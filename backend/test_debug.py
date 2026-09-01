from app.db.supabase_client import get_supabase
sb = get_supabase()
tasks = sb.table('tasks').select('*').execute()
for t in tasks.data:
    print(f'{t["id"][:8]}: {t["title"]} (assignee: {t["assignee_id"][:8]})')

props = sb.table('proposed_reassignments').select('*').execute()
for p in props.data:
    print(f'Proposal task_id: {p["task_id"][:8]} -> {p["to_member_id"][:8]}')