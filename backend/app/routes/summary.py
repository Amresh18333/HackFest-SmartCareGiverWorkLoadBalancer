from fastapi import APIRouter, HTTPException, Request
from typing import List
from app.config import settings

router = APIRouter()

@router.post("/summary")
async def generate_summary(request: Request):
    try:
        body = await request.json()
    except:
        raise HTTPException(400, "Invalid JSON")
    
    team_risk_summary = body.get("team_risk_summary", "")
    top_concerns = body.get("top_concerns", [])
    
    if not settings.groq_api_key:
        # Fallback deterministic summary
        return {
            "summary": f"Team status: {team_risk_summary}. Key concerns: {', '.join(top_concerns)}."
        }
    
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
        return {"summary": summary}
        
    except Exception as e:
        # Fallback on any error
        return {
            "summary": f"Team status: {team_risk_summary}. Key concerns: {', '.join(top_concerns)}."
        }