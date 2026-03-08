import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from utils.logger import logger

from database.connection import init_db, close_db
from auth.routes import router as auth_router
from agents.pipeline import analyze_claim_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="TruthLens API",
    description="Fact-checking and claim verification API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon, allow all
    allow_credentials=False, # Must be False if origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])


def _serialize_analysis_result(result):
    if isinstance(result, dict):
        return result
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return {"result": str(result)}

@app.get("/")
async def root():
    return {"message": "Welcome to TruthLens API. Systems nominal."}

@app.post("/analyze")
async def analyze_claim(request: Request):
    data = await request.json()
    claim = data.get("claim")
    user_id = data.get("user_id") # Optional
    ip_address = request.client.host if request.client else None
    
    if not claim:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Claim is required")
        
    # Standard analysis pipeline execution
    result = await analyze_claim_pipeline(claim, user_id, ip_address)
    result_dict = _serialize_analysis_result(result)
    
    # If authenticated, try to send an email report to the user asynchronously
    if user_id:
        try:
            from database.crud import get_db
            db = get_db()
            if db:
                user_res = db.table("users").select("email").eq("id", user_id).execute()
                if user_res.data:
                    from utils.email_service import send_report_email
                    
                    user_email = user_res.data[0]["email"]
                    
                    # Hack for sending it without background task properly initiated via FastAPI signature (for sake of speed here)
                    send_report_email(user_email, claim, result_dict)
        except Exception as e:
            logger.error(f"Error sending report email: {e}")
            
    return result_dict

@app.get("/history")
async def get_history(user_id: str):
    from database.crud import get_analyses_by_user
    analyses = await get_analyses_by_user(user_id)
    return list(analyses)

@app.get("/trending")
async def get_trending():
    from database.crud import get_trending_analyses
    analyses = await get_trending_analyses()
    return list(analyses)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
