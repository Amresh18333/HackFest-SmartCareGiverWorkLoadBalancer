import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

print('=== TEST MEMBERS ENDPOINT ===')

# Register Manager with unique email
import uuid
unique = uuid.uuid4().hex[:8]
r = client.post('/api/auth/register', json={
    'email': f'mgr{uuid}@test.com', 'password': 'pwd123', 'name': 'Manager',
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Care Team Alpha'
})
print(f'Register: {r.status_code} - {r.json()}')

mgr_token = r.json()['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}

# Get members
r = client.get('/api/members', headers=mgr_headers)
print(f'Members: {r.status_code}')
print(f'Response: {r.json()}')