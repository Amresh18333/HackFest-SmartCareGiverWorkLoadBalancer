import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import time

client = TestClient(app)

print('=== TEST MEMBERS ===')

# Register Manager
r = client.post('/api/auth/register', json={
    'email': f'mgr{int(time.time()*1000)}@test.com', 'password': 'pwd123', 'name': 'Manager',
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Care Team Alpha'
})
print('Register Manager:', r.status_code, r.json())
mgr_token = r.json()['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}

# Get team info for manager (includes join code)
r = client.get('/api/team/me', headers=mgr_headers)
print('Team info:', r.status_code, r.json())

# Register Member
r = client.post('/api/auth/register', json={
    'email': f'mem{int(time.time()*1000)}@test.com', 'password': 'pwd123', 'name': 'Member',
    'avatar_initials': 'MB'
})
print('Register Member:', r.status_code)
mem_token = r.json()['access_token']
mem_headers = {'Authorization': f'Bearer {mem_token}'}

# Get join code from manager's team
r = client.get('/api/team/me', headers=mgr_headers)
team = r.json()
join_code = team['team']['join_code']
print('Join code:', join_code)

# Member joins team
r = client.post('/api/team/join', headers=mem_headers, json={'join_code': join_code})
print('Join team:', r.status_code, r.json())

# Now check members
r = client.get('/api/members', headers=mgr_headers)
print('Members:', r.status_code)
print('Members response:', r.json())