"""
JWT Authentication for team members.
"""
import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.db.supabase_client import get_supabase_admin

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hackfest-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Simple password hashing (bcrypt has issues on Python 3.14)
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"pbkdf2_sha256${salt}${pwd_hash.hex()}"

def verify_password(plain: str, hashed: str) -> bool:
    try:
        if not hashed.startswith("pbkdf2_sha256$"):
            return False
        _, salt, pwd_hash = hashed.split("$")
        computed = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt.encode(), 100000)
        return secrets.compare_digest(computed.hex(), pwd_hash)
    except:
        return False

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_member_by_email(email: str) -> Optional[Dict]:
    sb = get_supabase_admin()
    res = sb.table("team_members").select("*").eq("email", email).single().execute()
    data = res.data
    if isinstance(data, list):
        return data[0] if data else None
    return data

def get_member_by_id(member_id: str) -> Optional[Dict]:
    sb = get_supabase_admin()
    res = sb.table("team_members").select("*").eq("id", member_id).single().execute()
    data = res.data
    if isinstance(data, list):
        return data[0] if data else None
    return data

def get_team_by_join_code(join_code: str) -> Optional[Dict]:
    sb = get_supabase_admin()
    res = sb.table("teams").select("*").eq("join_code", join_code).single().execute()
    return res.data

def get_team_by_manager(manager_id: str) -> Optional[Dict]:
    sb = get_supabase_admin()
    res = sb.table("teams").select("*").eq("manager_id", manager_id).single().execute()
    return res.data

def generate_join_code() -> str:
    return str(uuid.uuid4())[:8].upper()

def create_team(manager_id: str, team_name: str) -> Dict:
    sb = get_supabase_admin()
    join_code = generate_join_code()
    team_data = {
        "name": team_name,
        "manager_id": manager_id,
        "join_code": join_code
    }
    res = sb.table("teams").insert(team_data).execute()
    team = res.data[0]
    
    # Update manager with team_id and role
    sb.table("team_members").update({
        "team_id": team["id"],
        "role": "manager"
    }).eq("id", manager_id).execute()
    
    return team

def join_team(member_id: str, join_code: str) -> Dict:
    sb = get_supabase_admin()
    team = get_team_by_join_code(join_code)
    if not team:
        raise ValueError("Invalid join code")
    
    sb.table("team_members").update({
        "team_id": team["id"],
        "role": "member"
    }).eq("id", member_id).execute()
    
    return team

def create_member(member_data: Dict) -> Dict:
    sb = get_supabase_admin()
    member_data["password_hash"] = hash_password(member_data.pop("password"))
    member_data["email"] = member_data["email"].lower()
    member_data["role"] = member_data.get("role", "member")
    res = sb.table("team_members").insert(member_data).execute()
    return res.data[0]

def authenticate_member(email: str, password: str) -> Optional[Dict]:
    member = get_member_by_email(email)
    if not member:
        return None
    if not verify_password(password, member.get("password_hash", "")):
        return None
    return member

def create_manager(member_data: Dict) -> Dict:
    """Create a manager with a new team."""
    sb = get_supabase_admin()
    member_data["password_hash"] = hash_password(member_data.pop("password"))
    member_data["email"] = member_data["email"].lower()
    member_data["role"] = "manager"
    res = sb.table("team_members").insert(member_data).execute()
    member = res.data[0]
    
    # Create team for manager
    team_name = member_data.get("team_name", f"{member['name']}'s Team")
    create_team(member["id"], team_name)
    
    return member