import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import time

client = TestClient(app)

print('=== DEBUG MANAGER TEAM VIEW ===')

# Use the seeded Demo Manager credentials
# We need to register the seeded Demo Manager first (since password is hashed)
# Actually, let's just test the seeded data directly

from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()

# Check the seeded team
print('1. Checking seeded data...')
seeded = sb.table('team_members').select('*').eq('role', 'member').execute()
print(f'   Members (role=member): {len(seeded.data)}')
for m in seeded.data:
    print(f'   - {m["name"]}: id={m["id"]}, team_id={m.get("team_id")}')

managers = sb.table('team_members').select('*').eq('role', 'manager').execute()
print(f'   Managers: {len(managers.data)}')
for m in managers.data:
    print(f'   - {m["name"]}: id={m["id"]}, team_id={m.get("team_id")}')

teams = sb.table('teams').select('*').execute()
print(f'   Teams: {len(teams.data)}')
for t in teams.data:
    print(f'   - {t["name"]}: id={t["id"]}, manager_id={t.get("manager_id")}, join_code={t.get("join_code")}')

# Now test with the seeded Demo Manager
# We need to register the Demo Manager first to get a token
# But the password is hashed... let's just use the existing seeded manager
# Actually, we can't login without knowing the password. Let's check if we can register the seeded manager
# The seeded Demo Manager has email... wait, the seed script doesn't set email for the Demo Manager

# Let's just test the members API with a manager that has the correct team
# First, register a new manager and join the seeded team
print('\n2. Testing with new manager joining seeded team...')
from app.main import app
from starlette.testclient import TestClient
import time

client = TestClient(app)

# Register a new manager
r = client.post('/api/auth/register', json={
    'email': f'mgr{int(time.time()*1000)}@test.com', 'password': 'pwd123', 'name': 'Test Manager',
    'avatar_initials': 'TM', 'is_manager': True, 'team_name': 'Test Team'
})
mgr_token = r.json()['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}
print(f'Register Manager: {r.status_code}')

# Join the seeded team (we need the join code from the seeded team)
teams = sb.table('teams').select('*').execute()
seeded_team = None
for t in teams.data:
    if t['name'] == 'Care Team Alpha':
        seeded_team = t
        break

if seeded_team:
    print(f'   Seeded team join code: {seeded_team["join_code"]}')
    r = client.post('/api/team/join', headers=mgr_headers, json={'join_code': seeded_team['join_code']})
    print(f'   Join team: {r.status_code}')
    
    # Now get members
    r = client.get('/api/members', headers=mgr_headers)
    members = r.json()
    print(f'   Members API: {r.status_code}')
    print(f'   Members count: {len(members)}')
    for m in members:
        print(f'   - {m["name"]}: score={m.get("current_score")}, risk={m.get("risk_level")}')
else:
    print('   No seeded team found')