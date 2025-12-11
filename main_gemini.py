# main_gemini.py - FastAPI application for Gemini-powered CodeCraft on port 9090
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Import Gemini routes
from gemini_routes import router as gemini_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeCraft AI Builder (Gemini)",
    description="AI-powered Full Stack Builder using Gemini",
    version="2.0.0-gemini"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Gemini router
app.include_router(gemini_router)

@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "CodeCraft - AI-Powered Full Stack Builder (Gemini)",
        "version": "2.0.0-gemini",
        "description": "AI-powered Full Stack Builder using Gemini models",
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "gemini_modules": {
                "prompt_to_backend_stream": "/gemini/prompt-to-backend-stream",
                "prompt_to_frontend_stream": "/gemini/prompt-to-frontend-stream",
                "frontend_to_backend_stream": "/gemini/frontend-to-backend-stream",
                "backend_to_frontend_stream": "/gemini/backend-to-frontend-stream",
                "ui_to_frontend_stream": "/gemini/ui-to-frontend-stream",
                "ui_to_frontend_multi_stream": "/gemini/ui-to-frontend-multi-stream",
            }
        },
        "quick_start": {
            "api_docs": "http://localhost:9090/docs",
            "health_check": "http://localhost:9090/health"
        }
    }

@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    gemini_key_configured = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "healthy",
        "service": "CodeCraft Gemini Backend",
        "port": 9090,
        "gemini_configured": gemini_key_configured
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)
