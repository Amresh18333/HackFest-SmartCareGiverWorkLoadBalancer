import sys
sys.path.insert(0, '.')
import os
import shutil

mock_dir = os.path.join(os.path.dirname(__file__), 'mock_data')
shutil.rmtree(mock_dir, ignore_errors=True)
os.makedirs(mock_dir, exist_ok=True)

sys.path.insert(0, '.')
from app.db.supabase_client import get_supabase_admin, MockTable

# Create table directly
table = MockTable("team_members")

# Add test records
test_data = [
    {"id": "1", "name": "A", "role": "member"},
    {"id": "2", "name": "B", "role": "member"},
    {"id": "3", "name": "C", "role": "member"},
    {"id": "4", "name": "D", "role": "manager"},
]
table.data = test_data
table._save()

print("Initial data:")
for item in table.data:
    print(f'  {item["name"]}: role={item["role"]}')

# Test update with filter - update id=4 to role=admin
print("\nUpdating record with id='4' to role='admin'")
table.update({"role": "admin"}).eq("id", "4").execute()

print("After update:")
for item in table.data:
    print(f'  {item["name"]}: role={item["role"]}')

# Check file
print("\nFile content:")
with open(table.filepath, 'r') as f:
    import json
    data = json.load(f)
    for item in data:
        print(f'  {item["name"]}: role={item.get("role")}')

# Test select
print("\nSelect all:")
res = table.select("*").execute()
for item in res.data:
    print(f'  {item["name"]}: role={item.get("role")}')