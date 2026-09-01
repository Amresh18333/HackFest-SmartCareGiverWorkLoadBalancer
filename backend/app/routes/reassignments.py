from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from app.db.queries import get_pending_reassignments, resolve_proposal, get_task, update_task

router = APIRouter()

@router.get("/reassignments")
async def list_reassignments(member_id: Optional[str] = None):
    return get_pending_reassignments(member_id)

@router.post("/reassignments/{proposal_id}/resolve")
async def resolve_reassignment(proposal_id: str, request: Request):
    try:
        body = await request.json()
    except:
        raise HTTPException(400, "Invalid JSON")
    
    status = body.get("status")
    if status not in ["accepted", "dismissed"]:
        raise HTTPException(400, "Status must be 'accepted' or 'dismissed'")
    
    # Get proposal details
    from app.db.supabase_client import get_supabase_admin
    sb = get_supabase_admin()
    res = sb.table("proposed_reassignments").select("*").eq("id", proposal_id).single().execute()
    proposal = res.data
    
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    
    if proposal["status"] != "pending":
        raise HTTPException(400, "Proposal already resolved")
    
    # If accepted, actually reassign the task
    if status == "accepted":
        update_task(proposal["task_id"], {"assignee_id": proposal["to_member_id"]})
    
    resolved = resolve_proposal(proposal_id, status)
    return resolved