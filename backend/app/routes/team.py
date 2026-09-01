from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date, timedelta
from pydantic import BaseModel
from app.db.queries import (
    get_all_members, get_member, get_member_tasks, get_latest_signals,
    get_latest_score, get_member_scores, compute_and_store_risk_score,
    get_pending_reassignments, find_rebalance_candidate
)

router = APIRouter()

class MemberCard(BaseModel):
    id: str
    name: str
    avatar_initials: str
    current_score: int
    score_trend: List[dict]  # [{"date": "...", "score": 75}, ...]
    risk_level: str  # low, medium, high

class MemberDetail(BaseModel):
    id: str
    name: str
    avatar_initials: str
    timezone: str
    current_score: int
    top_drivers: List[str]
    score_history: List[dict]
    tasks: List[dict]
    pending_reassignments: List[dict]

@router.get("/members", response_model=List[MemberCard])
async def list_members():
    members = get_all_members()
    cards = []
    
    for m in members:
        # Get last 7 days of scores for sparkline
        scores = get_member_scores(m["id"], days=7)
        trend = [{"date": s["date"], "score": s["score"]} for s in scores]
        
        latest = get_latest_score(m["id"])
        current_score = latest["score"] if latest else 0
        
        if current_score < 40:
            risk_level = "low"
        elif current_score < 70:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        cards.append(MemberCard(
            id=m["id"],
            name=m["name"],
            avatar_initials=m["avatar_initials"],
            current_score=current_score,
            score_trend=trend,
            risk_level=risk_level
        ))
    
    return cards

@router.get("/members/{member_id}", response_model=MemberDetail)
async def get_member_detail(member_id: str):
    member = get_member(member_id)
    if not member:
        raise HTTPException(404, "Member not found")
    
    latest_score = get_latest_score(member_id)
    current_score = latest_score["score"] if latest_score else 0
    top_drivers = latest_score["top_drivers"] if latest_score else []
    
    scores = get_member_scores(member_id, days=30)
    score_history = [{"date": s["date"], "score": s["score"]} for s in scores]
    
    tasks = get_member_tasks(member_id)
    pending_reassignments = get_pending_reassignments(member_id)
    
    return MemberDetail(
        id=member["id"],
        name=member["name"],
        avatar_initials=member["avatar_initials"],
        timezone=member["timezone"],
        current_score=current_score,
        top_drivers=top_drivers,
        score_history=score_history,
        tasks=tasks,
        pending_reassignments=pending_reassignments
    )

@router.post("/members/{member_id}/recompute-risk")
async def recompute_risk(member_id: str):
    member = get_member(member_id)
    if not member:
        raise HTTPException(404, "Member not found")
    
    signals = get_latest_signals(member_id)
    if not signals:
        raise HTTPException(404, "No risk signals found for member")
    
    # Remove metadata fields
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
    
    return result