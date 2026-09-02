import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import uuid

client = TestClient(app)

print('=== FULL FLOW TEST ===')

# Use the existing seeded team
SEED_TEAM_ID = 'a57aca29-411d-4a78-8e51-047dcbf51fa3'

# 1. Login as existing seeded manager (need to register first with same team)
# Since we can't login to seeded manager (password hashed), 
# let's create a new manager and join the existing team

print('\n1. Register new Manager...')
unique = uuid.uuid4().hex[:8]
r = client.post('/api/auth/register', json={
    'email': f'mgr{uuid}@test.com', 'password': 'pwd123', 'name': 'Test Manager',
    'avatar_initials': 'TM', 'is_manager': True, 'team_name': 'Test Team'
})
print(f'   Status: {r.status_code}')
data = r.json()
mgr_token = data['access_token']
mgr_headers = {'Authorization': f'Bearer {mgr_token}'}

# 2. Join the seeded team instead of creating new
print('\n2. Manager joins seeded team...')
r = client.post('/api/team/join', headers=mgr_headers, json={'join_code': 'BE74D7C1'})  # Use known join code
print(f'   Status: {r.status_code}')
print(f'   Response: {r.json()}')

# 3. Get team to verify
print('\n3. Get team...')
r = client.get('/api/team/me', headers=mgr_headers)
print(f'   Status: {r.status_code}')
print(f'   Response: {r.json()}')