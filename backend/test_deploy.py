import os
os.environ['SUPABASE_URL'] = 'https://sknhfirvgnkxinhysnzk.supabase.co'
os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrbmhmaXJ2Z25reGluaHlzbnprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODE3MTI1MywiZXhwIjoyMTAzNzQ3MjUzfQ.OzDkhfbIGPS5qCbe0NKElIqe9X0vTgqqzPUbkmNngVM'

from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
print('Connected to Supabase!')
res = sb.table('team_members').select('id,name,role').execute()
for m in res.data:
    print(f'  {m["name"]}: role={m["role"]}')