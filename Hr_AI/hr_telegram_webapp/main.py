"""
FastAPI Main Application
Serves WebApp and handles API requests
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import asyncio
from contextlib import asynccontextmanager

from config import Config
from db import get_db, init_db
from models import ChatLog, User
from gemini_client import get_hr_response
import telegram_bot


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for FastAPI app
    Starts Telegram bot on startup, stops on shutdown
    """
    # Startup
    print("🚀 Starting HR Assistant WebApp Bot...")
    
    # Initialize database
    init_db()
    
    # Start Telegram bot in background
    bot_task = asyncio.create_task(telegram_bot.start_bot())
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await telegram_bot.stop_bot()
    bot_task.cancel()


# Initialize FastAPI app
app = FastAPI(
    title="HR Assistant WebApp Bot",
    description="Telegram WebApp for HR assistance with multilingual support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic models
class ChatRequest(BaseModel):
    telegram_id: int
    question: str
    language: str = "en"  # Optional language parameter


class ChatResponse(BaseModel):
    answer: str
    language: str
    success: bool


# ============================================================================
# MODULE 6: FastAPI Endpoints
# ============================================================================

@app.get("/webapp")
async def serve_webapp():
    """
    MODULE 6: Serves HTML UI
    Returns the WebApp interface
    """
    from fastapi.responses import FileResponse
    return FileResponse("static/webapp_new.html")


@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    MODULE 6: Chat endpoint
    Receives {message, lang, user_id}
    Calls hrbot_gemini API
    Saves to PostgreSQL
    Returns response
    """
    import requests
    from gemini_client import detect_language
    
    try:
        # Use provided language or detect it
        if request.language and request.language in ["uz", "ru", "en"]:
            language = request.language
        else:
            language = detect_language(request.question)
        
        # Call hrbot_gemini API
        api_url = "http://localhost:8000/chat"
        response = requests.post(
            api_url,
            json={"message": request.question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("reply", "No response received.")
        else:
            raise HTTPException(status_code=500, detail="hrbot_gemini API error")
        
        # Save to database using MODULE 2 schema
        chat_log = ChatLog(
            user_id=str(request.telegram_id),
            message=request.question,
            response=answer,
            language=language
        )
        
        db.add(chat_log)
        db.commit()
        
        return ChatResponse(
            answer=answer,
            language=language,
            success=True
        )
    
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="HR assistant API is temporarily unavailable"
        )
    except Exception as e:
        print(f"Error in api_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status():
    """
    MODULE 6: Simple health check
    """
    return {
        "status": "ok",
        "service": "HR Assistant WebApp Bot",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HR Assistant WebApp Bot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webapp": "GET /webapp - WebApp interface",
            "chat": "POST /api/chat - Send message to HR assistant",
            "status": "GET /status - Health check",
            "history": "GET /api/history/{telegram_id} - Get chat history"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/api/history/{telegram_id}")
async def get_history(
    telegram_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get chat history for a user
    
    Args:
        telegram_id: Telegram user ID
        limit: Maximum number of messages to return
        db: Database session
        
    Returns:
        List of chat messages
    """
    try:
        # Query using user_id field from MODULE 2 schema
        chat_logs = db.query(ChatLog).filter(
            ChatLog.user_id == str(telegram_id)
        ).order_by(
            ChatLog.created_at.desc()
        ).limit(limit).all()
        
        return {
            "telegram_id": telegram_id,
            "count": len(chat_logs),
            "messages": [log.to_dict() for log in reversed(chat_logs)]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: int, db: Session = Depends(get_db)):
    """
    Get user information
    
    Args:
        telegram_id: Telegram user ID
        db: Database session
        
    Returns:
        User information
    """
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language_code": user.language_code
    }


if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting FastAPI server on {Config.API_HOST}:{Config.API_PORT}")
    
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.DEBUG
    )
