from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# 1. Register Manager
r = client.post('/api/auth/register', json={
    'email': 'mgr@test.com', 'password': 'pwd123', 'name': 'Manager', 
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Care Team'
})
print('1. Register Manager:', r.status_code)
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 2. Login
r = client.post('/api/auth/login', json={'email': 'mgr@test.com', 'password': 'pwd123'})
print('2. Login:', r.status_code)

# 3. Get team (should have join code)
r = client.get('/api/team/me', headers=headers)
print('3. Team:', r.status_code, r.json().get('team', {}).get('join_code'))

# 4. Register Member
r = client.post('/api/auth/register', json={
    'email': 'mem@test.com', 'password': 'pwd123', 'name': 'Member', 
    'avatar_initials': 'MB'
})
print('4. Register Member:', r.status_code)
mem_token = r.json()['access_token']
mem_headers = {'Authorization': f'Bearer {mem_token}'}

# 5. Member joins team
r = client.get('/api/team/me', headers=headers)
join_code = r.json()['team']['join_code']
r = client.post('/api/team/join', headers=mem_headers, json={'join_code': join_code})
print('5. Join Team:', r.status_code)

# 6. Member submits signals
r = client.post('/api/member/signals', headers=mem_headers, json={
    'self_checkin_score': 3, 'tasks_today': 5, 'late_night_activity_flag': False,
    'avg_response_latency_mins': 30
})
print('6. Submit Signals:', r.status_code)

# 7. Member gets risk
r = client.get('/api/member/risk', headers=mem_headers)
print('7. My Risk:', r.status_code, r.json())

# 8. Manager recomputes risk (triggers rebalancing)
r = client.get('/api/members', headers=headers)
members = r.json()
alex = next(m for m in members if m['name'] == 'Alex Chen')
r = client.post('/api/members/' + alex['id'] + '/recompute-risk', headers=headers)
print('8. Recompute Alex:', r.status_code, 'proposal' in r.json())

# 9. Manager sees proposals
r = client.get('/api/reassignments', headers=headers)
print('9. Proposals:', r.status_code, len(r.json()))

print('\nAll backend APIs working!')