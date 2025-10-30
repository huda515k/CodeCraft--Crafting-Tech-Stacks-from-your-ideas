# main.py - FastAPI application entry point
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import zipfile
from pathlib import Path
import json
from datetime import datetime
import tempfile
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from backend_generator.ERD.routes import router as erd_router
from backend_generator.NodeGen.routes import router as nodegen_router
from backend_generator.Agent.routes import router as agent_router
from backend_generator.PromptAnalysis.routes import router as prompt_analysis_router

# Import documentation agent
from documentation.documentation_agent import DocumentationAgent

app = FastAPI(
    title="CodeCraft Backend Generator",
    description="AI-powered ERD processing and backend generation service with LangGraph AI Agent",
    version="2.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories for documentation
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize the documentation agent
try:
    doc_agent = DocumentationAgent()
except Exception as e:
    logger.warning(f"Documentation agent not available: {e}")
    doc_agent = None

# Include all routes
app.include_router(erd_router)
app.include_router(nodegen_router)
app.include_router(agent_router)
app.include_router(prompt_analysis_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CodeCraft Backend Generator API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/erd/health",
        "services": {
            "erd": "/erd/health",
            "nodegen": "/nodegen/health", 
            "agent": "/agent/status",
            "prompt_analysis": "/prompt-analysis/health"
        },
        "generators": {
            "ai_advanced": "/nodegen/advanced-upload-erd"
        },
        "documentation": {
            "claude_documentation": "/claude-documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/claude-documentation")
async def claude_documentation(file: UploadFile = File(...)):
    """
    Analyze uploaded Node.js/Express backend and generate API documentation
    
    Args:
        file: Zip file containing the backend code
        
    Returns:
        Downloadable ZIP file with API documentation in JSON, Markdown, and OpenAPI formats
    """
    if not doc_agent:
        raise HTTPException(status_code=503, detail="Documentation agent not available")
    
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
    
    # Create unique directory for this upload
    upload_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_path = UPLOAD_DIR / upload_id
    upload_path.mkdir(exist_ok=True)
    
    zip_path = upload_path / file.filename
    extracted_path = upload_path / "extracted"
    
    try:
        # Save uploaded file
        logger.info(f"Saving uploaded file: {file.filename}")
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract zip file
        logger.info(f"Extracting zip file to: {extracted_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_path)
        
        # Analyze the backend
        logger.info("Starting backend analysis...")
        documentation = await doc_agent.analyze_backend(str(extracted_path))
        
        # Generate documentation files
        logger.info("Generating documentation files...")
        output_path = OUTPUT_DIR / f"api_docs_{upload_id}"
        output_path.mkdir(exist_ok=True)
        
        # Save as JSON
        json_path = output_path / "api_documentation.json"
        with open(json_path, "w") as f:
            json.dump(documentation, f, indent=2)
        
        # Generate Markdown documentation
        md_path = output_path / "API_DOCUMENTATION.md"
        markdown_content = doc_agent.generate_markdown(documentation)
        with open(md_path, "w") as f:
            f.write(markdown_content)
        
        # Generate OpenAPI/Swagger spec
        openapi_path = output_path / "openapi.yaml"
        openapi_content = doc_agent.generate_openapi(documentation)
        import yaml
        with open(openapi_path, "w") as f:
            yaml.dump(openapi_content, f, default_flow_style=False)
        
        # Create zip file with all documentation
        zip_output_path = OUTPUT_DIR / f"api_docs_{upload_id}.zip"
        with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in output_path.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(output_path))
        
        logger.info(f"Documentation generated successfully: {zip_output_path}")
        
        # Clean up uploaded files
        shutil.rmtree(upload_path)
        
        return FileResponse(
            path=zip_output_path,
            filename=f"api_documentation_{upload_id}.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing backend: {str(e)}")
        # Clean up on error
        if upload_path.exists():
            shutil.rmtree(upload_path)
        raise HTTPException(status_code=500, detail=f"Error analyzing backend: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
