from app.db.supabase_client import get_supabase
sb = get_supabase()

table = sb.table('tasks')

# Check file before
import json
with open(table.filepath) as f:
    file_data = json.load(f)
print(f"File before: {len(file_data)} tasks")
for t in file_data[:3]:
    print(f"  {t['id'][:8]}: assignee={t.get('assignee_id')[:8]}")

# Run the actual _execute_update
task_id = '29c00b85-bdac-40a7-933a-d92afa00f253'
table._query_filters = [("eq", "id", task_id)]
table._update_data = {"assignee_id": "75ac7965-dc12-4c75-9216-6288d4c9821b"}
result = table._execute_update()
print(f"Updated: {len(result.data)} items")

# Check file after
with open(table.filepath) as f:
    file_data = json.load(f)
print(f"File after: {len(file_data)} tasks")
for t in file_data[:3]:
    print(f"  {t['id'][:8]}: assignee={t.get('assignee_id')[:8]}")

# Check in-memory data
print(f"In-memory: {len(table.data)} tasks")
for t in table.data[:3]:
    print(f"  {t['id'][:8]}: assignee={t.get('assignee_id')[:8]}")