import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import time

client = TestClient(app)

def unique_email(prefix='test'):
    return f'{prefix}{int(time.time() * 1000)}@test.com'

print('=== DEBUG MANAGER TEAM VIEW ===')

# 1. Register Manager
r = client.post('/api/auth/register', json={
    'email': f'mgr{int(time.time()*1000)}@test.com', 'password': 'pwd123', 'name': 'Manager',
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Care Team Alpha'
})
mgr_token = r.json()['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}
print(f'1. Register Manager: {r.status_code}')

# 2. Get team info
r = client.get('/api/team/me', headers=mgr_headers)
team = r.json()
print(f'2. Team: {r.status_code}')
print(f'   Team ID: {team["team"]["id"]}')
print(f'   Manager ID: {team["team"]["manager_id"]}')
print(f'   Members count: {len(team["members"])}')
for m in team['members']:
    print(f'   - {m["name"]}: id={m["id"]}, role={m["role"]}')

# 3. Get members via /api/members
r = client.get('/api/members', headers=mgr_headers)
members = r.json()
print(f'\n3. Members API: {r.status_code}')
print(f'   Response type: {type(members)}')
print(f'   Members: {members}')

# 4. Check DB directly
from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
print('\n4. All DB members:')
all_members = sb.table('team_members').select('id,name,email,role,team_id').execute()
for m in all_members.data:
    print(f'  {m["name"]}: id={m["id"]}, team_id={m.get("team_id")}, role={m.get("role")}')