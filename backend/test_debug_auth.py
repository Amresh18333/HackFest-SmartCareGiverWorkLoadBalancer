from app.db.supabase_client import get_supabase_admin
from app.auth import get_member_by_id, get_member_by_email

sb = get_supabase_admin()

# Test get_member_by_email
print("=== Test get_member_by_email ===")
email = "manager@example.com"
res = sb.table("team_members").select("*").eq("email", email).single().execute()
print(f"Result type: {type(res)}")
print(f"Result data: {res.data}")
print(f"Data type: {type(res.data)}")

# Test get_member_by_id
member_id = "224fca98-e34f-4fff-8b99-d075f7283638"
print(f"\n=== Test get_member_by_id ===")
res = sb.table("team_members").select("*").eq("id", member_id).single().execute()
print(f"Result type: {type(res)}")
print(f"Result data: {res.data}")
print(f"Data type: {type(res.data)}")

# Test function
print(f"\n=== Test get_member_by_id function ===")
member = get_member_by_id(member_id)
print(f"Result: {member}")
print(f"Type: {type(member)}")