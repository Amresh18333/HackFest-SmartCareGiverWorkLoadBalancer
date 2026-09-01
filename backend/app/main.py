"""
Minimal API using Starlette directly (no FastAPI/pydantic internals).
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.config import settings
from app.ml.model import predict_risk, get_top_drivers, format_driver, manager_visible_drivers
from app.db.queries import (
    get_all_members, get_member, get_member_tasks, get_latest_signals,
    get_latest_score, get_member_scores, compute_and_store_risk_score,
    get_pending_reassignments, find_rebalance_candidate, resolve_proposal, update_task,
    get_task, upsert_risk_signal
)
from app.db.supabase_client import get_supabase_admin
from app.auth import (
    create_access_token, decode_token, authenticate_member,
    create_member, get_member_by_id, get_member_by_email,
    create_team, join_team, create_manager, public_member
)


def require_user(request: Request) -> Tuple[Optional[Dict], Optional[JSONResponse]]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, JSONResponse({"detail": "Not authenticated"}, status_code=401)
    payload = decode_token(auth_header.split(" ", 1)[1])
    if not payload:
        return None, JSONResponse({"detail": "Invalid token"}, status_code=401)
    member = get_member_by_id(payload.get("sub"))
    if not member:
        return None, JSONResponse({"detail": "Member not found"}, status_code=404)
    return member, None


def require_manager(request: Request) -> Tuple[Optional[Dict], Optional[JSONResponse]]:
    member, err = require_user(request)
    if err:
        return None, err
    if member.get("role") != "manager":
        return None, JSONResponse({"detail": "Manager access required"}, status_code=403)
    return member, None

# --- Health ---
async def health(request: Request):
    return JSONResponse({"status": "ok"})

# --- Auth ---
async def login(request: Request):
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    email = body.get("email", "").lower()
    password = body.get("password", "")
    
    if not email or not password:
        return JSONResponse({"detail": "Email and password required"}, status_code=400)
    
    member = authenticate_member(email, password)
    if not member:
        return JSONResponse({"detail": "Invalid credentials"}, status_code=401)
    
    role = member.get("role", "member")
    token = create_access_token({"sub": member["id"], "email": member.get("email"), "role": role})
    pub = public_member(member)
    return JSONResponse({
        "access_token": token,
        "token_type": "bearer",
        "member": pub,
        "redirect": "/manager" if role == "manager" else "/me"
    })

async def register(request: Request):
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    required = ["email", "password", "name", "avatar_initials"]
    for field in required:
        if not body.get(field):
            return JSONResponse({"detail": f"Missing field: {field}"}, status_code=400)
    
    # Check if email exists
    existing = get_member_by_email(body["email"].lower())
    if existing:
        return JSONResponse({"detail": "Email already registered"}, status_code=400)
    
    is_manager = body.get("is_manager", False)
    team_name = body.get("team_name")
    
    if is_manager:
        member_data = {
            "email": body["email"].lower(),
            "password": body["password"],
            "name": body["name"],
            "avatar_initials": body["avatar_initials"],
            "timezone": body.get("timezone", "UTC"),
            "team_name": team_name or f"{body['name']}'s Team"
        }
        member = create_manager(member_data)
        role = "manager"
    else:
        member_data = {
            "email": body["email"].lower(),
            "password": body["password"],
            "name": body["name"],
            "avatar_initials": body["avatar_initials"],
            "timezone": body.get("timezone", "UTC")
        }
        member = create_member(member_data)
        role = "member"
        join_code = body.get("join_code")
        if join_code:
            try:
                join_team(member["id"], str(join_code).upper())
                member = get_member_by_id(member["id"]) or member
            except ValueError as e:
                return JSONResponse({"detail": str(e)}, status_code=400)

    token = create_access_token({"sub": member["id"], "email": member["email"], "role": role})
    pub = public_member(member)
    pub["role"] = role
    return JSONResponse({
        "access_token": token,
        "token_type": "bearer",
        "member": pub,
        "redirect": "/manager" if role == "manager" else "/me"
    }, status_code=201)

async def get_current_member(request: Request):
    member, err = require_user(request)
    if err:
        return err
    return JSONResponse(public_member(member))

# --- Team Management ---
async def create_my_team(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    
    member_id = payload["sub"]
    member = get_member_by_id(member_id)
    if not member:
        return JSONResponse({"detail": "Member not found"}, status_code=404)
    
    if member.get("role") != "manager":
        return JSONResponse({"detail": "Only managers can create teams"}, status_code=403)
    
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    team_name = body.get("team_name", f"{member['name']}'s Team")
    team = create_team(member_id, team_name)
    
    return JSONResponse({"team": team, "join_code": team["join_code"]})

async def join_team_endpoint(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    
    member_id = payload["sub"]
    
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    join_code = body.get("join_code", "").upper()
    if not join_code:
        return JSONResponse({"detail": "Join code required"}, status_code=400)
    
    try:
        team = join_team(member_id, join_code)
        return JSONResponse({"team": team, "message": f"Joined {team['name']}"})
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=400)

async def get_my_team(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    
    member_id = payload["sub"]
    member = get_member_by_id(member_id)
    if not member:
        return JSONResponse({"detail": "Member not found"}, status_code=404)
    
    team_id = member.get("team_id")
    if not team_id:
        return JSONResponse({"team": None, "message": "Not part of a team"})
    
    sb = get_supabase_admin()
    team = sb.table("teams").select("*").eq("id", team_id).single().execute()
    
    # Get team members (for manager view)
    members = sb.table("team_members").select("id,name,avatar_initials,role").eq("team_id", team_id).execute()
    
    return JSONResponse({
        "team": team.data,
        "members": members.data,
        "is_manager": member.get("role") == "manager"
    })

# --- Predict ---
async def predict(request: Request):
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    required = ["tasks_today", "overdue_tasks", "late_night_activity_flag", 
                "avg_response_latency_mins", "consecutive_overloaded_days", "self_checkin_score"]
    
    for field in required:
        if field not in body:
            return JSONResponse({"detail": f"Missing field: {field}"}, status_code=400)
    
    signals = body
    score, importances = predict_risk(signals)
    top_driver_keys = get_top_drivers(importances)
    top_drivers = [format_driver(d) for d in top_driver_keys]
    
    return JSONResponse({
        "score": score,
        "feature_importances": importances,
        "top_drivers": top_drivers
    })

# --- Team ---
async def list_members(request: Request):
    manager, err = require_manager(request)
    if err:
        return err

    team_id = manager.get("team_id")
    members = [m for m in get_all_members(team_id=team_id) if m.get("role") != "manager"]
    cards = []

    for m in members:
        scores = get_member_scores(m["id"], days=7)
        trend = [{"date": s["date"], "score": s["score"]} for s in scores]

        latest = get_latest_score(m["id"])
        current_score = latest["score"] if latest else 0
        drivers = manager_visible_drivers(latest.get("top_drivers") if latest else [])

        if current_score < 40:
            risk_level = "low"
        elif current_score < 70:
            risk_level = "medium"
        else:
            risk_level = "high"

        cards.append({
            "id": m["id"],
            "name": m["name"],
            "avatar_initials": m["avatar_initials"],
            "current_score": current_score,
            "score_trend": trend,
            "risk_level": risk_level,
            "top_drivers": drivers,
        })

    return JSONResponse(cards)

async def get_member_detail(request: Request):
    manager, err = require_manager(request)
    if err:
        return err

    member_id = request.path_params["member_id"]
    member = get_member(member_id)
    if not member:
        return JSONResponse({"detail": "Member not found"}, status_code=404)
    if manager.get("team_id") and member.get("team_id") != manager.get("team_id"):
        return JSONResponse({"detail": "Member not found"}, status_code=404)

    latest_score = get_latest_score(member_id)
    current_score = latest_score["score"] if latest_score else 0
    top_drivers = manager_visible_drivers(latest_score["top_drivers"] if latest_score else [])

    scores = get_member_scores(member_id, days=30)
    score_history = [{"date": s["date"], "score": s["score"]} for s in scores]

    tasks = get_member_tasks(member_id)
    pending_reassignments = get_pending_reassignments(member_id)

    return JSONResponse({
        "id": member["id"],
        "name": member["name"],
        "avatar_initials": member["avatar_initials"],
        "timezone": member["timezone"],
        "current_score": current_score,
        "top_drivers": top_drivers,
        "score_history": score_history,
        "tasks": tasks,
        "pending_reassignments": pending_reassignments,
        "personal_signals_hidden": True,
    })

# --- Member Dashboard Endpoints ---
async def get_my_tasks(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    
    member_id = payload["sub"]
    tasks = get_member_tasks(member_id)
    return JSONResponse(tasks)

async def update_task_status(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    
    member_id = payload["sub"]
    task_id = request.path_params["task_id"]
    
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    status = body.get("status")
    if status not in ["todo", "in_progress", "done"]:
        return JSONResponse({"detail": "Invalid status"}, status_code=400)
    
    # Verify task belongs to member
    task = get_task(task_id)
    if not task or task["assignee_id"] != member_id:
        return JSONResponse({"detail": "Task not found"}, status_code=404)
    
    updated = update_task(task_id, {"status": status})
    return JSONResponse(updated)

async def submit_daily_signals(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    
    member_id = payload["sub"]
    
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    # Required signals from member
    required = ["self_checkin_score", "tasks_today", "late_night_activity_flag", 
                "avg_response_latency_mins"]
    for field in required:
        if field not in body:
            return JSONResponse({"detail": f"Missing field: {field}"}, status_code=400)
    
    today = datetime.now().date().isoformat()
    
    signal_data = {
        "member_id": member_id,
        "date": today,
        "tasks_today": body["tasks_today"],
        "overdue_tasks": body.get("overdue_tasks", 0),
        "late_night_activity_flag": body["late_night_activity_flag"],
        "avg_response_latency_mins": body["avg_response_latency_mins"],
        "consecutive_overloaded_days": body.get("consecutive_overloaded_days", 0),
        "self_checkin_score": body["self_checkin_score"]
    }
    
    # Upsert signal
    upsert_risk_signal(signal_data)
    
    # Recompute risk score
    result = compute_and_store_risk_score(member_id, signal_data)
    
    return JSONResponse({
        "signal": signal_data,
        "risk_score": result
    })

async def get_my_risk(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    
    member_id = payload["sub"]
    
    latest_score = get_latest_score(member_id)
    current_score = latest_score["score"] if latest_score else 0
    top_drivers = latest_score["top_drivers"] if latest_score else []
    
    scores = get_member_scores(member_id, days=30)
    score_history = [{"date": s["date"], "score": s["score"]} for s in scores]
    
    return JSONResponse({
        "current_score": current_score,
        "top_drivers": top_drivers,
        "score_history": score_history
    })

async def recompute_risk(request: Request):
    manager, err = require_manager(request)
    if err:
        return err

    member_id = request.path_params["member_id"]
    member = get_member(member_id)
    if not member:
        return JSONResponse({"detail": "Member not found"}, status_code=404)
    if manager.get("team_id") and member.get("team_id") != manager.get("team_id"):
        return JSONResponse({"detail": "Member not found"}, status_code=404)
    
    signals = get_latest_signals(member_id)
    if not signals:
        return JSONResponse({"detail": "No risk signals found for member"}, status_code=404)
    
    signal_data = {k: v for k, v in signals.items() 
                   if k not in ["id", "member_id", "date", "created_at"]}
    
    result = compute_and_store_risk_score(member_id, signal_data)
    
    # Check if rebalancing needed
    if result["score"] >= 70:
        proposal = find_rebalance_candidate(member_id)
        if proposal:
            from app.db.queries import create_proposed_reassignment
            created = create_proposed_reassignment(proposal)
            result["rebalance_proposal"] = created
    
    return JSONResponse(result)

# --- Reassignments ---
async def list_reassignments(request: Request):
    manager, err = require_manager(request)
    if err:
        return err
    member_id = request.query_params.get("member_id")
    return JSONResponse(get_pending_reassignments(member_id))

async def resolve_reassignment(request: Request):
    manager, err = require_manager(request)
    if err:
        return err
    proposal_id = request.path_params["proposal_id"]
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    status = body.get("status")
    if status not in ["accepted", "dismissed"]:
        return JSONResponse({"detail": "Status must be 'accepted' or 'dismissed'"}, status_code=400)
    
    sb = get_supabase_admin()
    res = sb.table("proposed_reassignments").select("*").eq("id", proposal_id).single().execute()
    proposal = res.data
    
    if not proposal:
        return JSONResponse({"detail": "Proposal not found"}, status_code=404)
    
    if proposal["status"] != "pending":
        return JSONResponse({"detail": "Proposal already resolved"}, status_code=400)
    
    if status == "accepted":
        update_task(proposal["task_id"], {"assignee_id": proposal["to_member_id"]})
    
    resolved = resolve_proposal(proposal_id, status)
    return JSONResponse(resolved)

# --- Summary ---
async def generate_summary(request: Request):
    try:
        body = await request.json()
    except:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
    
    team_risk_summary = body.get("team_risk_summary", "")
    top_concerns = body.get("top_concerns", [])
    
    if not settings.groq_api_key:
        return JSONResponse({
            "summary": f"Team status: {team_risk_summary}. Key concerns: {', '.join(top_concerns)}."
        })
    
    try:
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        
        prompt = f"""You are a supportive manager's assistant. Write ONE concise, plain-language sentence summarizing the team's burnout risk status for a dashboard.

Team status: {team_risk_summary}
Key concerns: {', '.join(top_concerns)}

Requirements:
- One sentence only
- Warm, professional tone
- No jargon, no bullet points
- Actionable if possible
- Max 25 words

Example: "Three teammates are approaching burnout threshold — consider redistributing Alex's lowest-priority task to Jordan who has capacity."
"""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=60
        )
        
        summary = response.choices[0].message.content.strip()
        return JSONResponse({"summary": summary})
        
    except Exception as e:
        return JSONResponse({
            "summary": f"Team status: {team_risk_summary}. Key concerns: {', '.join(top_concerns)}."
        })

# --- Routes ---
routes = [
    Route("/health", health, methods=["GET"]),
    Route("/api/health", health, methods=["GET"]),
    Route("/api/auth/login", login, methods=["POST"]),
    Route("/api/auth/register", register, methods=["POST"]),
    Route("/api/auth/me", get_current_member, methods=["GET"]),
    Route("/api/team/create", create_my_team, methods=["POST"]),
    Route("/api/team/join", join_team_endpoint, methods=["POST"]),
    Route("/api/team/me", get_my_team, methods=["GET"]),
    Route("/api/member/tasks", get_my_tasks, methods=["GET"]),
    Route("/api/member/tasks/{task_id}", update_task_status, methods=["PATCH"]),
    Route("/api/member/signals", submit_daily_signals, methods=["POST"]),
    Route("/api/member/risk", get_my_risk, methods=["GET"]),
    Route("/api/predict", predict, methods=["POST"]),
    Route("/api/members", list_members, methods=["GET"]),
    Route("/api/members/{member_id}", get_member_detail, methods=["GET"]),
    Route("/api/members/{member_id}/recompute-risk", recompute_risk, methods=["POST"]),
    Route("/api/reassignments", list_reassignments, methods=["GET"]),
    Route("/api/reassignments/{proposal_id}/resolve", resolve_reassignment, methods=["POST"]),
    Route("/api/summary", generate_summary, methods=["POST"]),
]

is_prod = settings.environment == "production"
app = Starlette(debug=not is_prod, routes=routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)