"""
Backend API Service for HR CV Filter Agent
FastAPI application that handles AI agent logic, LLM, and MongoDB operations
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import asyncio

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.HR_CVFilter_agent import HRCVFilterAgent
from src.services.rule_service import RuleService
from src.utils.cv_extractor import CVExtractor
from src.utils.logger import Logger
from backend.services.session_service import SessionService
from backend.services.request_queue import RequestQueue
from backend.services.socket_manager import SocketManager

logger = Logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HR CV Filter Agent API",
    description="Backend API for AI-powered CV filtering and evaluation",
    version="1.0.0"
)

# Initialize Socket.IO manager
socket_manager = SocketManager()

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
session_service = None
request_queue = None
socket_io = None

# Pydantic models
class EvaluateCVRequest(BaseModel):
    session_id: Optional[str] = None
    cv_content: str
    job_description: str
    custom_rules: Optional[str] = ""
    llm_model: Optional[str] = "gemini-2.0-flash"

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
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
    global rule_service, session_service, request_queue

    # Initialize RuleService
    try:
        rule_service = RuleService()
        logger.info("✅ RuleService initialized")
    except Exception as e:
        logger.error(f"⚠️ Failed to initialize RuleService: {str(e)}")
        logger.error("⚠️ MongoDB features will be unavailable. API will continue without rule management.")
        rule_service = None

    # Initialize SessionService
    try:
        session_service = SessionService(session_timeout_minutes=60)
        logger.info("✅ SessionService initialized")
    except Exception as e:
        logger.error(f"⚠️ Failed to initialize SessionService: {str(e)}")
        session_service = None

    # Initialize RequestQueue with socket manager
    try:
        request_queue = RequestQueue(max_concurrent=1, max_queue_size=100, socket_manager=socket_manager)
        await request_queue.start()
        logger.info("✅ RequestQueue initialized and started")
    except Exception as e:
        logger.error(f"⚠️ Failed to initialize RequestQueue: {str(e)}")
        request_queue = None

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global request_queue
    if request_queue:
        await request_queue.stop()
        logger.info("✅ RequestQueue stopped")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "HR CV Filter Agent API",
        "version": "1.0.0",
        "queue_size": request_queue.get_queue_size() if request_queue else 0,
        "active_requests": request_queue.get_active_count() if request_queue else 0,
        "active_sessions": session_service.get_session_count() if session_service else 0
    }

# Get or create session
@app.post("/api/session")
async def create_session():
    """Create a new session and return session_id"""
    try:
        session_id = session_service.create_session()
        return {
            "success": True,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get session info
@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    try:
        session = session_service.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found or expired")

        return {
            "success": True,
            "session": {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "chat_history_count": len(session.chat_history),
                "cv_evaluations_count": len(session.cv_evaluations)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Evaluate CV endpoint
@app.post("/api/evaluate-cv")
async def evaluate_cv(request: EvaluateCVRequest):
    try:
        # Get or create session
        session_id, session = session_service.get_or_create_session(request.session_id)

        # Update session with job description and rules
        session_service.update_session(
            session_id,
            job_description=request.job_description,
            custom_rules=request.custom_rules,
            llm_model=request.llm_model
        )

        # Define handler function
        def evaluate_handler():
            agent = HRCVFilterAgent(llm_model_name=request.llm_model)
            return agent.evaluate_cv(
                cv_content=request.cv_content,
                job_description=request.job_description,
                custom_rules=request.custom_rules
            )

        # Enqueue request
        request_id = await request_queue.enqueue(
            session_id=session_id,
            request_type="evaluate_cv",
            handler=evaluate_handler
        )

        # Wait for completion (with timeout)
        queued_request = await request_queue.wait_for_request(request_id, timeout=300)

        if queued_request.status.value == "failed":
            raise HTTPException(status_code=500, detail=queued_request.error)

        return {
            "success": True,
            "session_id": session_id,
            "evaluation": queued_request.result,
            "queue_position": request_queue.get_queue_size()
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except asyncio.QueueFull:
        raise HTTPException(status_code=503, detail="Server is busy, please try again later")
    except Exception as e:
        logger.error(f"Error evaluating CV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Get or create session
        session_id, session = session_service.get_or_create_session(request.session_id)

        # Update session
        session_service.update_session(
            session_id,
            job_description=request.job_description,
            custom_rules=request.custom_rules,
            llm_model=request.llm_model
        )

        # Add user message to session
        session_service.add_chat_message(session_id, "user", request.message)

        # Define handler function
        def chat_handler():
            agent = HRCVFilterAgent(llm_model_name=request.llm_model)

            # Add CV evaluations to agent's chat history if provided
            if request.cv_evaluations:
                agent.chat_history = request.cv_evaluations

            # Chat with agent
            return agent.chat(
                message=request.message,
                job_description=request.job_description,
                custom_rules=request.custom_rules
            )

        # Enqueue request
        request_id = await request_queue.enqueue(
            session_id=session_id,
            request_type="chat",
            handler=chat_handler
        )

        # Wait for completion (with timeout)
        queued_request = await request_queue.wait_for_request(request_id, timeout=300)

        if queued_request.status.value == "failed":
            raise HTTPException(status_code=500, detail=queued_request.error)

        # Add assistant response to session
        session_service.add_chat_message(session_id, "assistant", queued_request.result)

        return {
            "success": True,
            "session_id": session_id,
            "response": queued_request.result,
            "queue_position": request_queue.get_queue_size()
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except asyncio.QueueFull:
        raise HTTPException(status_code=503, detail="Server is busy, please try again later")
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

# Socket.IO event handlers
async def handle_evaluate_cv_socketio(sid: str, data: dict):
    """Handle CV evaluation via Socket.IO"""
    try:
        session_id = data.get('session_id')
        cv_content = data.get('cv_content')
        job_description = data.get('job_description', '')
        custom_rules = data.get('custom_rules', '')
        llm_model = data.get('llm_model', 'gemini-2.0-flash')

        if not session_id or not cv_content:
            await socket_manager.sio.emit('evaluate_cv_error', {
                'error': 'Missing session_id or cv_content'
            }, room=sid)
            return

        # Get or create session
        session_id, session = session_service.get_or_create_session(session_id)

        # Update session
        session_service.update_session(
            session_id,
            job_description=job_description,
            custom_rules=custom_rules,
            llm_model=llm_model
        )

        # Define handler function
        def evaluate_handler():
            agent = HRCVFilterAgent(llm_model_name=llm_model)
            return agent.evaluate_cv(
                cv_content=cv_content,
                job_description=job_description,
                custom_rules=custom_rules
            )

        # Enqueue request
        request_id = await request_queue.enqueue(
            session_id=session_id,
            request_type="evaluate_cv",
            handler=evaluate_handler
        )

        # Wait for completion
        queued_request = await request_queue.wait_for_request(request_id, timeout=300)

        if queued_request.status.value == "failed":
            await socket_manager.sio.emit('evaluate_cv_error', {
                'error': queued_request.error
            }, room=sid)
        else:
            await socket_manager.sio.emit('evaluate_cv_complete', {
                'session_id': session_id,
                'evaluation': queued_request.result
            }, room=sid)

    except asyncio.TimeoutError:
        await socket_manager.sio.emit('evaluate_cv_error', {
            'error': 'Request timed out'
        }, room=sid)
    except Exception as e:
        logger.error(f"Error in evaluate_cv_socketio: {str(e)}")
        await socket_manager.sio.emit('evaluate_cv_error', {
            'error': str(e)
        }, room=sid)

async def handle_chat_socketio(sid: str, data: dict):
    """Handle chat via Socket.IO"""
    try:
        session_id = data.get('session_id')
        message = data.get('message')
        job_description = data.get('job_description', '')
        custom_rules = data.get('custom_rules', '')
        cv_evaluations = data.get('cv_evaluations', [])
        chat_history = data.get('chat_history', [])
        llm_model = data.get('llm_model', 'gemini-2.0-flash')

        if not session_id or not message:
            await socket_manager.sio.emit('chat_error', {
                'error': 'Missing session_id or message'
            }, room=sid)
            return

        # Get or create session
        session_id, session = session_service.get_or_create_session(session_id)

        # Update session
        session_service.update_session(
            session_id,
            job_description=job_description,
            custom_rules=custom_rules,
            llm_model=llm_model
        )

        # Add user message to session
        session_service.add_chat_message(session_id, "user", message)

        # Define handler function
        def chat_handler():
            agent = HRCVFilterAgent(llm_model_name=llm_model)

            # Add CV evaluations to agent's chat history if provided
            if cv_evaluations:
                agent.chat_history = cv_evaluations

            # Chat with agent
            return agent.chat(
                message=message,
                job_description=job_description,
                custom_rules=custom_rules
            )

        # Enqueue request
        request_id = await request_queue.enqueue(
            session_id=session_id,
            request_type="chat",
            handler=chat_handler
        )

        # Wait for completion
        queued_request = await request_queue.wait_for_request(request_id, timeout=300)

        if queued_request.status.value == "failed":
            await socket_manager.sio.emit('chat_error', {
                'error': queued_request.error
            }, room=sid)
        else:
            # Add assistant message to session
            session_service.add_chat_message(session_id, "assistant", queued_request.result)

            await socket_manager.sio.emit('chat_complete', {
                'session_id': session_id,
                'response': queued_request.result
            }, room=sid)

    except asyncio.TimeoutError:
        await socket_manager.sio.emit('chat_error', {
            'error': 'Request timed out'
        }, room=sid)
    except Exception as e:
        logger.error(f"Error in chat_socketio: {str(e)}")
        await socket_manager.sio.emit('chat_error', {
            'error': str(e)
        }, room=sid)

# Mount Socket.IO app
socket_app = socket_manager.get_asgi_app()
app.mount("/socket.io", socket_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

