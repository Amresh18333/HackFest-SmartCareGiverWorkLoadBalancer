from app.db.supabase_client import get_supabase_admin
sb = get_supabase_admin()

# Check team_members table directly
team_id = "926f964d-14a0-4595-90eb-235143adf714"  # Replace with actual team ID

# Get all team members
res = sb.table("team_members").select("*").execute()
print("All team members:")
for m in res.data:
    print(f'  {m["name"]}: team_id={m.get("team_id")}, role={m.get("role")}')

# Check specific team
res = sb.table("team_members").select("*").eq("team_id", "926f964d-14a0-4595-90eb-235143adf714").execute()
print(f"\nTeam members for team_id=926f964d-14a0-4595-90eb-235143adf714:")
for m in res.data:
    print(f'  {m["name"]}: role={m.get("role")}')