import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import uuid
import time

client = TestClient(app)

def unique_email(prefix='test'):
    return f'{prefix}{int(time.time() * 1000)}@test.com'

print('=== DEBUG LOGIN ===')

# 1. Register Manager
print('\n1. Register Manager...')
r = client.post('/api/auth/register', json={
    'email': f'mgr{int(time.time()*1000)}@test.com', 'password': 'pwd123', 'name': 'Manager',
    'avatar_initials': 'MG', 'is_manager': True, 'team_name': 'Care Team Alpha'
})
print(f'Status: {r.status_code}')
data = r.json()
print(f'Response: {data}')

# 2. Login Manager
print('\n2. Login Manager...')
r = client.post('/api/auth/login', json={'email': 'mgr@test.com', 'password': 'pwd123'})
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')