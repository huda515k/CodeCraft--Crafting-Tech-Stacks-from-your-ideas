# main.py - FastAPI application entry point
from fastapi import FastAPI
from backend_generator.ERD.routes import router as erd_router
from backend_generator.NodeGen.routes import router as nodegen_router
from backend_generator.Agent.routes import router as agent_router

app = FastAPI(
    title="CodeCraft Backend Generator",
    description="AI-powered ERD processing and backend generation service with LangGraph AI Agent",
    version="2.0.0"
)

# Include all routes
app.include_router(erd_router)
app.include_router(nodegen_router)
app.include_router(agent_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CodeCraft Backend Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/erd/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)