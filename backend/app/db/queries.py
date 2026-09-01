from typing import List, Optional, Dict, Any
from datetime import date, timedelta, datetime
from app.db.supabase_client import get_supabase, get_supabase_admin
from app.ml.model import predict_risk, get_top_drivers, format_driver

sb = get_supabase()
sb_admin = get_supabase_admin()

# --- Team Members ---
MEMBER_PUBLIC_FIELDS = "id,name,avatar_initials,timezone,role,team_id,email"

def get_all_members(team_id: Optional[str] = None) -> List[Dict]:
    query = sb.table("team_members").select(MEMBER_PUBLIC_FIELDS).order("name")
    if team_id:
        query = query.eq("team_id", team_id)
    res = query.execute()
    return res.data or []

def get_member(member_id: str) -> Optional[Dict]:
    try:
        res = sb.table("team_members").select(MEMBER_PUBLIC_FIELDS).eq("id", member_id).single().execute()
        return res.data
    except Exception:
        return None

# --- Tasks ---
def get_member_tasks(member_id: str, status: Optional[str] = None) -> List[Dict]:
    query = sb.table("tasks").select("*").eq("assignee_id", member_id)
    if status:
        query = query.eq("status", status)
    res = query.order("priority", desc=True).order("due_date").execute()
    return res.data

def get_all_active_tasks() -> List[Dict]:
    res = sb.table("tasks").select("*").in_("status", ["todo", "in_progress"]).execute()
    return res.data

def get_task(task_id: str) -> Optional[Dict]:
    res = sb.table("tasks").select("*").eq("id", task_id).single().execute()
    return res.data

def create_task(task: Dict) -> Dict:
    res = sb_admin.table("tasks").insert(task).execute()
    return res.data[0]

def update_task(task_id: str, updates: Dict) -> Dict:
    res = sb_admin.table("tasks").update(updates).eq("id", task_id).execute()
    return res.data[0]

# --- Risk Signals ---
def get_member_signals(member_id: str, days: int = 30) -> List[Dict]:
    cutoff = date.today() - timedelta(days=days)
    res = sb.table("risk_signals").select("*").eq("member_id", member_id).gte("date", cutoff.isoformat()).order("date").execute()
    return res.data

def get_latest_signals(member_id: str) -> Optional[Dict]:
    res = sb.table("risk_signals").select("*").eq("member_id", member_id).order("date", desc=True).limit(1).execute()
    return res.data[0] if res.data else None

def upsert_risk_signal(signal: Dict) -> Dict:
    res = sb_admin.table("risk_signals").upsert(signal, on_conflict="member_id,date").execute()
    return res.data[0]

# --- Risk Scores ---
def get_member_scores(member_id: str, days: int = 30) -> List[Dict]:
    cutoff = date.today() - timedelta(days=days)
    res = sb.table("risk_scores").select("*").eq("member_id", member_id).gte("date", cutoff.isoformat()).order("date").execute()
    return res.data

def get_latest_score(member_id: str) -> Optional[Dict]:
    res = sb.table("risk_scores").select("*").eq("member_id", member_id).order("date", desc=True).limit(1).execute()
    return res.data[0] if res.data else None

def upsert_risk_score(score: Dict) -> Dict:
    res = sb_admin.table("risk_scores").upsert(score, on_conflict="member_id,date").execute()
    return res.data[0]

def compute_and_store_risk_score(member_id: str, signals: Dict, target_date: date = None) -> Dict:
    """Compute risk score from signals and store it."""
    if target_date is None:
        target_date = date.today()
    
    score, importances = predict_risk(signals)
    top_drivers = get_top_drivers(importances)
    driver_texts = [format_driver(d) for d in top_drivers]
    
    risk_score = {
        "member_id": member_id,
        "date": target_date.isoformat(),
        "score": score,
        "top_drivers": driver_texts
    }
    
    return upsert_risk_score(risk_score)

# --- Proposed Reassignments ---
def get_pending_reassignments(member_id: str = None) -> List[Dict]:
    query = sb.table("proposed_reassignments").select("*").eq("status", "pending")
    if member_id:
        query = query.or_(f"from_member_id.eq.{member_id},to_member_id.eq.{member_id}")
    res = query.order("created_at", desc=True).execute()
    
    # Manually join with tasks and members
    proposals = res.data
    for p in proposals:
        task = get_task(p["task_id"])
        p["tasks"] = task
        from_member = get_member(p["from_member_id"])
        p["from_member"] = from_member
        to_member = get_member(p["to_member_id"])
        p["to_member"] = to_member
    return proposals

def create_proposed_reassignment(proposal: Dict) -> Dict:
    proposal["status"] = "pending"
    proposal["created_at"] = datetime.now().isoformat()
    res = sb_admin.table("proposed_reassignments").insert(proposal).execute()
    return res.data[0]

def resolve_proposal(proposal_id: str, status: str) -> Dict:
    """Accept or dismiss a proposal."""
    from datetime import datetime
    res = sb_admin.table("proposed_reassignments").update({
        "status": status,
        "resolved_at": datetime.now().isoformat()
    }).eq("id", proposal_id).execute()
    return res.data[0]

# --- Rebalancing Logic ---
def find_rebalance_candidate(overloaded_member_id: str) -> Optional[Dict]:
    """
    When a member's risk crosses 70, find their lowest-priority incomplete task
    and the teammate with the most spare capacity.
    """
    # Get overloaded member's incomplete tasks, lowest priority first
    tasks = get_member_tasks(overloaded_member_id)
    incomplete = [t for t in tasks if t["status"] != "done"]
    
    if not incomplete:
        return None
    
    # Priority order: low < medium < high
    priority_order = {"low": 0, "medium": 1, "high": 2}
    incomplete.sort(key=lambda t: priority_order.get(t["priority"], 1))
    task_to_reassign = incomplete[0]
    
    # Find teammate with lowest current estimated_hours on active tasks
    overloaded = get_member(overloaded_member_id)
    members = get_all_members(team_id=overloaded.get("team_id") if overloaded else None)
    other_members = [m for m in members if m["id"] != overloaded_member_id and m.get("role") != "manager"]
    
    best_member = None
    min_hours = float("inf")
    
    for member in other_members:
        active_tasks = get_member_tasks(member["id"])
        active_incomplete = [t for t in active_tasks if t["status"] != "done"]
        total_hours = sum(t["estimated_hours"] for t in active_incomplete)
        
        if total_hours < min_hours:
            min_hours = total_hours
            best_member = member
    
    if not best_member:
        return None
    
    return {
        "task_id": task_to_reassign["id"],
        "from_member_id": overloaded_member_id,
        "to_member_id": best_member["id"],
        "reason": f"Rebalance: {task_to_reassign['title']} moved to {best_member['name']} (they have {min_hours:.1f}h vs your {sum(t['estimated_hours'] for t in incomplete):.1f}h)"
    }