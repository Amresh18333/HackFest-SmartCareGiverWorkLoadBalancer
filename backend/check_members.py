from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
members = sb.table('team_members').select('*').execute()
for m in members.data:
    print(f'{m["name"]}: id={m["id"]}, team_id={m.get("team_id")}, role={m.get("role")}')