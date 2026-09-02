from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()

# Check team_members table directly
res = sb.table("team_members").select("*").execute()
print("All team members:")
for m in res.data:
    print(f'  {m["name"]}: team_id={m.get("team_id")}, role={m.get("role")}')

# Check specific team
team_id = "40c60f15-841f-460c-9b29-b554971c2663"
res = sb.table("team_members").select("*").eq("team_id", team_id).execute()
print(f"\nTeam members for team_id={team_id}:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')