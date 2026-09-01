from app.db.supabase_client import get_supabase_admin
from app.ml.model import predict_risk

# Test the model directly
score, imp = predict_risk({
    'tasks_today': 8, 'overdue_tasks': 3, 'late_night_activity_flag': True,
    'avg_response_latency_mins': 80, 'consecutive_overloaded_days': 5, 'self_checkin_score': 2
})
print(f'Score: {score}')
print(f'Top drivers: {imp}')

# Test database
sb = get_supabase_admin()
members = sb.table('team_members').select('*').execute()
print(f'Members: {len(members.data)}')
for m in members.data:
    print(f'  {m["name"]} ({m["avatar_initials"]})')

# Test member detail
member_id = members.data[0]["id"]
detail = sb.table('team_members').select('*').eq('id', member_id).single().execute()
print(f'Member detail: {detail.data}')