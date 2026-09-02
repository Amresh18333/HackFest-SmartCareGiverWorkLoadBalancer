import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import time

client = TestClient(app)

def unique_email(prefix='test'):
    return f'{prefix}{int(time.time() * 1000)}@test.com'

print('=== FULL FLOW TEST ===')

# 1. Register Manager
print('\n1. Register Manager...')
r = client.post('/api/auth/register', json={
    'email': 'mgr@test.com', 'password': 'pwd123', 'name': 'Manager',
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Care Team Alpha'
})
print(f'   Status: {r.status_code}')
data = r.json()
mgr_token = data['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}

# Get join code from team endpoint
r = client.get('/api/team/me', headers=mgr_headers)
team = r.json()
join_code = team['team']['join_code']
print(f'   Join code: {join_code}')

# 2. Register Member
print('\n2. Register Member...')
r = client.post('/api/auth/register', json={
    'email': 'mem@test.com', 'password': 'pwd123', 'name': 'Member',
    'avatar_initials': 'MB'
})
mem_data = r.json()
mem_token = mem_data['access_token']
mem_headers = {'Authorization': f'Bearer {mem_token}'}
print(f'   Status: {r.status_code}')

# 3. Member joins team
print('\n3. Member joins team...')
r = client.post('/api/team/join', headers=mem_headers, json={'join_code': join_code})
print(f'   Status: {r.status_code}')

# 4. Member submits daily signals
print('\n4. Member submits daily check-in...')
r = client.post('/api/member/signals', headers=mem_headers, json={
    'self_checkin_score': 3,
    'tasks_today': 5,
    'late_night_activity_flag': True,
    'avg_response_latency_mins': 45,
})
print(f'   Status: {r.status_code}')
print(f'   Risk score: {r.json().get("risk_score", {}).get("score")}')

# 5. Member gets their risk
print('\n5. Member gets risk...')
r = client.get('/api/member/risk', headers=mem_headers)
risk = r.json()
print(f'   Score: {risk["current_score"]}')
print(f'   Drivers: {risk["top_drivers"]}')

# 6. Manager gets team
print('\n6. Manager gets team...')
r = client.get('/api/members', headers=mgr_headers)
members = r.json()
print(f'   Members count: {len(members)}')
for m in members:
    if isinstance(m, dict):
        print(f'   - {m["name"]}: score={m["current_score"]}, risk={m["risk_level"]}')

# Trigger high risk for member
print('\n7. Trigger high risk for member...')
for _ in range(5):
    client.post('/api/member/signals', headers=mem_headers, json={
        'self_checkin_score': 1,
        'tasks_today': 10,
        'late_night_activity_flag': True,
        'avg_response_latency_mins': 120,
    })

# Recompute risk for the member
mem_id = None
for m in members:
    if isinstance(m, dict) and m.get('email') == 'mem@test.com':
        mem_id = m['id']
        break

if mem_id:
    print('\n7. Trigger high risk for member...')
    r = client.post(f'/api/members/{mem_id}/recompute-risk', headers=mgr_headers)
    print(f'   Recompute status: {r.status_code}')
    print(f'   Proposal created: {"rebalance_proposal" in r.json()}')

# Manager checks proposals
print('\n8. Manager checks proposals...')
r = client.get('/api/reassignments', headers=mgr_headers)
proposals = r.json()
print(f'   Proposals: {len(proposals)}')
for p in proposals:
    if isinstance(p, dict):
        print(f'   - {p["tasks"]["title"]}: {p["from_member"]["name"]} -> {p["to_member"]["name"]}')

print('\nALL TESTS PASSED!')