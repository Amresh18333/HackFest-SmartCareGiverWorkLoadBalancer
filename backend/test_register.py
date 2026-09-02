import sys
sys.path.insert(0, '.')
from app.main import app
from starlette.testclient import TestClient
import uuid
import time

client = TestClient(app)

print('=== TEST REGISTER ===')
unique = str(int(time.time() * 1000))
r = client.post('/api/auth/register', json={
    'email': f'test{unique}@test.com', 'password': 'pwd123', 'name': 'Test Manager',
    'avatar_initials': 'TM', 'is_manager': True, 'team_name': 'Test Team'
})
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')