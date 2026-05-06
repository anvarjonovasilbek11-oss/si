"""
MODULE 7 & 9: FastAPI Chat & Feedback Endpoints
Multilingual HR chatbot with RAG (Retrieval-Augmented Generation)
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Import our modules
from ai_engine import get_gemini_response
from rag_search_module6 import search_hr_docs_json, get_context_for_query
from language_utils import detect_language_simple
from database import SessionLocal
from models import HRFeedback

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="HR Bot with Gemini AI",
    description="Multilingual AI-powered HR chatbot using Google Gemini and RAG",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    language: str = None  # Optional: 'uz', 'ru', 'en'


class ChatResponse(BaseModel):
    reply: str
    language: str
    sources: list = []


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    language: str
    rating: float = 0.0  # Rating from 0-5


# ============================================================================
# MODULE 7: Chat Endpoint
# ============================================================================

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request):
    """
    Chat endpoint with RAG (Module 7 specification)
    
    Accepts JSON: {"message": "user question"}
    Returns: {"reply": "AI answer", "language": "detected language"}
    """
    try:
        # Get request data
        data = await request.json()
        user_input = data.get("message", "")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Detect language
        lang = detect_language_simple(user_input)
        
        # Search for relevant documents
        docs = search_hr_docs_json(user_input, limit=3)
        
        # Build context from documents
        context = "\n\n".join([d['content'] for d in docs])
        
        # Create prompt with context
        prompt = f"""{context}

User question ({lang}): {user_input}"""
        
        # Get AI response
        reply = get_gemini_response(prompt)
        
        # Extract sources
        sources = [d['title'] for d in docs]
        
        return {
            "reply": reply,
            "language": lang,
            "sources": sources
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MODULE 9: Feedback Endpoint
# ============================================================================

@app.post("/feedback")
async def feedback(request: Request):
    """
    Feedback endpoint (Module 9 specification)
    
    Accepts JSON: {
        "question": "user question",
        "answer": "AI answer",
        "language": "language code",
        "rating": 0-5
    }
    Returns: {"status": "feedback_saved"}
    """
    try:
        data = await request.json()
        
        # Validate required fields
        if not data.get("question") or not data.get("answer"):
            raise HTTPException(
                status_code=400,
                detail="Question and answer are required"
            )
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Create feedback record
            fb = HRFeedback(
                question=data.get("question"),
                answer=data.get("answer"),
                language=data.get("language", "en"),
                rating=data.get("rating", 0.0)
            )
            
            db.add(fb)
            db.commit()
            db.refresh(fb)
            
            return {
                "status": "feedback_saved",
                "id": fb.id,
                "rating": fb.rating
            }
        
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Additional Endpoints
# ============================================================================

@app.get("/ping")
async def ping():
    """Test endpoint to verify the server is running"""
    return {"message": "pong"}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Multilingual HR Bot API",
        "version": "2.0.0",
        "status": "running",
        "features": {
            "multilingual": "Uzbek, Russian, English",
            "rag": "Retrieval-Augmented Generation",
            "ai_model": "Google Gemini"
        },
        "endpoints": {
            "chat": "POST /chat - Ask HR questions",
            "feedback": "POST /feedback - Submit feedback",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        },
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
        "database_configured": bool(os.getenv("DATABASE_URL"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
