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
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Test Team'
})
mgr_token = r.json()['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}
print(f'1. Register Manager: {r.status_code}')
print(f'   Manager ID: {r.json()["member"]["id"]}')

# 2. Get team info for new manager (should be their created team)
r = client.get('/api/team/me', headers=mgr_headers)
team = r.json()
print(f'\n2. Team after register: {r.status_code}')
print(f'   Team ID: {team["team"]["id"]}')
print(f'   Manager ID: {team["team"]["manager_id"]}')
print(f'   Members: {len(team["members"])}')

# 3. Get join code from seeded team
from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
teams = sb.table('teams').select('*').execute()
seeded_team = None
for t in teams.data:
    if t['name'] == 'Care Team Alpha':
        seeded_team = t
        break

if seeded_team:
    print(f'\n3. Seeded team: {seeded_team["name"]}, ID: {seeded_team["id"]}, join_code: {seeded_team["join_code"]}')
    
    # 4. Join seeded team
    print('\n4. Joining seeded team...')
    r = client.post('/api/team/join', headers=mgr_headers, json={'join_code': seeded_team['join_code']})
    print(f'   Join status: {r.status_code}')
    print(f'   Response: {r.json()}')
    
    # 5. Check team after join
    r = client.get('/api/team/me', headers=mgr_headers)
    team = r.json()
    print(f'\n5. Team after join: {r.status_code}')
    print(f'   Team ID: {team["team"]["id"]}')
    print(f'   Members count: {len(team["members"])}')
    for m in team['members']:
        print(f'   - {m["name"]}: role={m["role"]}')
    
    # 5. Get members via /api/members
    r = client.get('/api/members', headers=mgr_headers)
    members = r.json()
    print(f'\n6. Members API: {r.status_code}')
    print(f'   Members count: {len(members)}')
    for m in members:
        if isinstance(m, dict):
            print(f'   - {m["name"]}: score={m.get("current_score")}, risk={m.get("risk_level")}')
else:
    print('No seeded team found')