from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
print('Connected to Supabase!')
res = sb.table('team_members').select('id,name,role').execute()
for m in res.data:
    print(f'  {m["name"]}: role={m["role"]}')