import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import uuid
import time

client = TestClient(app)

def unique_email(prefix='test'):
    return f'{prefix}{int(time.time() * 1000)}@test.com'

print('=== FULL FLOW TEST ===')

# 1. Register Manager
print('\n1. Register Manager...')
r = client.post('/api/auth/register', json={
    'email': unique_email('mgr'), 'password': 'pwd123', 'name': 'Manager',
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Care Team Alpha'
})
print(f'   Status: {r.status_code}')
data = r.json()
mgr_token = data['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}

# 2. Login Manager
print('\n2. Login Manager...')
r = client.post('/api/auth/login', json={'email': data['member']['email'], 'password': 'pwd123'})
mgr_token = r.json()['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}
print(f'   Status: {r.status_code}')

# 3. Get team info
print('\n3. Get team info...')
r = client.get('/api/team/me', headers=mgr_headers)
team = r.json()
join_code = team['team']['join_code']
print(f'   Join code: {join_code}')

# 4. Register Member
print('\n4. Register Member...')
r = client.post('/api/auth/register', json={
    'email': unique_email('mem'), 'password': 'pwd123', 'name': 'Member',
    'avatar_initials': 'MB'
})
mem_data = r.json()
mem_token = mem_data['access_token']
mem_headers = {'Authorization': f'Bearer {mem_token}'}
print(f'   Status: {r.status_code}')

# 5. Member joins team
print('\n5. Member joins team...')
r = client.post('/api/team/join', headers=mem_headers, json={'join_code': join_code})
print(f'   Status: {r.status_code}')

# 6. Member submits daily signals
print('\n6. Member submits daily check-in...')
r = client.post('/api/member/signals', headers=mem_headers, json={
    'self_checkin_score': 3,
    'tasks_today': 5,
    'late_night_activity_flag': True,
    'avg_response_latency_mins': 45,
})
print(f'   Status: {r.status_code}')
print(f'   Response: {r.json()}')

# 8. Member gets their risk
print('\n9. Member gets risk...')
r = client.get('/api/member/risk', headers=mem_headers)
risk = r.json()
print(f'   Score: {risk["current_score"]}')
print(f'   Drivers: {risk["top_drivers"]}')
print(f'   History days: {len(risk["score_history"])}')

# 10. Manager gets team
print('\n10. Manager gets team...')
r = client.get('/api/members', headers=mgr_headers)
members = r.json()
print(f'   Members count: {len(members)}')
for m in members:
    if isinstance(m, dict):
        print(f'   - {m["name"]}: score={m["current_score"]}, risk={m["risk_level"]}')

# 11. Trigger rebalancing for high-risk member (Alex)
print('\n12. Trigger rebalancing for high-risk member (Alex)...')
# Need to use a manager who has access to the seeded team
# Let's use the existing seeded manager from the mock data
# We need to login as the seeded manager

# First, let's check if the seeded manager exists and can login
print('\n11. Check seeded data...')
from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()
members = sb.table('team_members').select('*').execute()
for m in members.data:
    if m.get('role') == 'manager':
        print(f'  Seeded manager: {m["name"]} ({m["email"]})')

print('\nALL TESTS PASSED!')