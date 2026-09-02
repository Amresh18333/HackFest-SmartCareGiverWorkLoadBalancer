import sys
sys.path.insert(0, '.')
import os
import shutil

mock_dir = os.path.join(os.path.dirname(__file__), 'mock_data')
shutil.rmtree(mock_dir, ignore_errors=True)
os.makedirs(mock_dir, exist_ok=True)

sys.path.insert(0, '.')
from app.db.supabase_client import get_supabase_admin, MockTable
import uuid
from datetime import datetime, date, timedelta
import random

sb = get_supabase_admin()

# Create test data manually
print("=== Testing mock client update ===")

# Create table directly
table = MockTable("test_table")

# Add test records
test_data = [
    {"id": "1", "name": "A", "role": "member"},
    {"id": "2", "name": "B", "role": "member"},
    {"id": "3", "name": "C", "role": "member"},
]
table.data = test_data
table._save()

print("Initial data:")
for item in table.data:
    print(f'  {item["name"]}: role={item["role"]}')

# Test update with filter
print("\nUpdating record with id='2' to role='manager'")
table.update({"role": "manager"}).eq("id", "2").execute()

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