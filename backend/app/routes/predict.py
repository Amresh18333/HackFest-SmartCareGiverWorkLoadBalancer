from fastapi import APIRouter, HTTPException, Request
from typing import Dict, List
from app.ml.model import predict_risk, get_top_drivers, format_driver

router = APIRouter()

@router.post("/predict")
async def predict(request: Request):
    try:
        body = await request.json()
    except:
        raise HTTPException(400, "Invalid JSON")
    
    # Validate required fields
    required = ["tasks_today", "overdue_tasks", "late_night_activity_flag", 
                "avg_response_latency_mins", "consecutive_overloaded_days", "self_checkin_score"]
    
    for field in required:
        if field not in body:
            raise HTTPException(400, f"Missing field: {field}")
    
    signals = body
    score, importances = predict_risk(signals)
    top_driver_keys = get_top_drivers(importances)
    top_drivers = [format_driver(d) for d in top_driver_keys]
    
    return {
        "score": score,
        "feature_importances": importances,
        "top_drivers": top_drivers
    }