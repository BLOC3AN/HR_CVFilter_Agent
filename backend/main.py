"""
Backend API Service for HR CV Filter Agent
FastAPI application that handles AI agent logic, LLM, and MongoDB operations
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.HR_CVFilter_agent import HRCVFilterAgent
from src.services.rule_service import RuleService
from src.utils.cv_extractor import CVExtractor
from src.utils.logger import Logger

logger = Logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HR CV Filter Agent API",
    description="Backend API for AI-powered CV filtering and evaluation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
agent_instance = None
rule_service = None

# Pydantic models
class EvaluateCVRequest(BaseModel):
    cv_content: str
    job_description: str
    custom_rules: Optional[str] = ""
    llm_model: Optional[str] = "gemini-2.0-flash"

class ChatRequest(BaseModel):
    message: str
    job_description: str
    custom_rules: Optional[str] = ""
    cv_evaluations: Optional[List[dict]] = []
    chat_history: Optional[List[dict]] = []
    llm_model: Optional[str] = "gemini-2.0-flash"

class CreateRuleRequest(BaseModel):
    name: str
    rules: str
    description: Optional[str] = ""

class UpdateRuleRequest(BaseModel):
    rules: str
    description: Optional[str] = ""

class RuleResponse(BaseModel):
    name: str
    rules: str
    description: str
    created_at: str
    updated_at: str

# Startup event
@app.on_event("startup")
async def startup_event():
    global rule_service
    try:
        rule_service = RuleService()
        logger.info("✅ RuleService initialized")
    except Exception as e:
        logger.error(f"⚠️ Failed to initialize RuleService: {str(e)}")
        logger.error("⚠️ MongoDB features will be unavailable. API will continue without rule management.")
        rule_service = None

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "HR CV Filter Agent API",
        "version": "1.0.0"
    }

# Evaluate CV endpoint
@app.post("/api/evaluate-cv")
async def evaluate_cv(request: EvaluateCVRequest):
    try:
        # Create agent instance with specified model
        agent = HRCVFilterAgent(llm_model_name=request.llm_model)
        
        # Evaluate CV
        result = agent.evaluate_cv(
            cv_content=request.cv_content,
            job_description=request.job_description,
            custom_rules=request.custom_rules
        )
        
        return {
            "success": True,
            "evaluation": result
        }
    except Exception as e:
        logger.error(f"Error evaluating CV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Create agent instance with specified model
        agent = HRCVFilterAgent(llm_model_name=request.llm_model)
        
        # Chat with agent
        result = agent.chat(
            message=request.message,
            job_description=request.job_description,
            custom_rules=request.custom_rules,
            cv_evaluations=request.cv_evaluations,
            chat_history=request.chat_history
        )
        
        return {
            "success": True,
            "response": result
        }
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Rules CRUD endpoints
@app.get("/api/rules")
async def get_all_rules():
    try:
        if rule_service is None:
            raise HTTPException(status_code=503, detail="RuleService not available")
        
        rules = rule_service.get_all_rules()
        return {
            "success": True,
            "rules": [
                {
                    "name": rule.name,
                    "rules": rule.rules,
                    "description": rule.description,
                    "created_at": rule.created_at.isoformat(),
                    "updated_at": rule.updated_at.isoformat()
                }
                for rule in rules
            ]
        }
    except Exception as e:
        logger.error(f"Error getting rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rules/names")
async def get_rule_names():
    try:
        if rule_service is None:
            raise HTTPException(status_code=503, detail="RuleService not available")
        
        names = rule_service.get_all_rule_names()
        return {
            "success": True,
            "names": names
        }
    except Exception as e:
        logger.error(f"Error getting rule names: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rules/{name}")
async def get_rule(name: str):
    try:
        if rule_service is None:
            raise HTTPException(status_code=503, detail="RuleService not available")
        
        rule = rule_service.get_rule_by_name(name)
        if rule is None:
            raise HTTPException(status_code=404, detail=f"Rule '{name}' not found")
        
        return {
            "success": True,
            "rule": {
                "name": rule.name,
                "rules": rule.rules,
                "description": rule.description,
                "created_at": rule.created_at.isoformat(),
                "updated_at": rule.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rules")
async def create_rule(request: CreateRuleRequest):
    try:
        if rule_service is None:
            raise HTTPException(status_code=503, detail="RuleService not available")
        
        rule = rule_service.create_rule(
            name=request.name,
            rules=request.rules,
            description=request.description
        )
        
        if rule is None:
            raise HTTPException(status_code=400, detail=f"Rule '{request.name}' already exists")
        
        return {
            "success": True,
            "rule": {
                "name": rule.name,
                "rules": rule.rules,
                "description": rule.description,
                "created_at": rule.created_at.isoformat(),
                "updated_at": rule.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/rules/{name}")
async def update_rule(name: str, request: UpdateRuleRequest):
    try:
        if rule_service is None:
            raise HTTPException(status_code=503, detail="RuleService not available")
        
        success = rule_service.update_rule(
            name=name,
            rules=request.rules,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Rule '{name}' not found")
        
        return {
            "success": True,
            "message": f"Rule '{name}' updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/rules/{name}")
async def delete_rule(name: str):
    try:
        if rule_service is None:
            raise HTTPException(status_code=503, detail="RuleService not available")
        
        success = rule_service.delete_rule(name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Rule '{name}' not found")
        
        return {
            "success": True,
            "message": f"Rule '{name}' deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

