# main.py - FastAPI application entry point
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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
from frontend_generator.routes import router as frontend_router

# Import documentation agent
from documentation.documentation_agent import DocumentationAgent

app = FastAPI(
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

# Register routers
app.include_router(erd_router)
app.include_router(nodegen_router)
app.include_router(agent_router)
app.include_router(prompt_analysis_router)
app.include_router(frontend_router)

# Create necessary directories for documentation
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize documentation agent
doc_agent = DocumentationAgent()

@app.get("/", tags=["Default"])
async def root():
    """
    Root endpoint - API information and available endpoints
    """
    return {
        "name": "CodeCraft - AI-Powered Backend Generator",
        "version": "2.0.0",
        "description": "AI-powered ERD processing and backend generation service with LangGraph AI Agent",
        "endpoints": {
            "documentation": "/docs",
            "preview": "/preview",
            "health": "/health",
            "erd": "/erd/health",
            "ollama_backend_generation": {
                "prompt_to_backend_stream": "/nodegen/prompt-to-backend-stream",
                "prompt_to_backend": "/nodegen/prompt-to-backend",
                "frontend_to_backend_stream": "/nodegen/frontend-to-backend-stream",
                "frontend_to_backend": "/nodegen/frontend-to-backend"
            },
            "nodegen": {
                "streaming": "/nodegen/prompt-to-backend-stream",
                "legacy": "/nodegen/prompt-to-backend",
                "advanced_erd": "/nodegen/advanced-upload-erd"
            },
            "agent": "/agent/status",
            "prompt_analysis": "/prompt-analysis/health",
            "claude_documentation": "/claude-documentation",
            "documentation_analyze": "/documentation/analyze-backend"
        },
        "quick_start": {
            "live_preview": "http://localhost:8000/preview",
            "api_docs": "http://localhost:8000/docs",
            "health_check": "http://localhost:8000/health"
        }
    }

@app.get("/health", tags=["Default"])
async def health():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "CodeCraft API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints_available": {
            "erd": "/erd/health",
            "agent": "/agent/status",
            "prompt_analysis": "/prompt-analysis/health"
        }
    }

@app.get("/preview", response_class=HTMLResponse)
async def preview_page():
    """Serve the code preview interface."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeCraft - Live Code Preview</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            min-height: 600px;
        }
        @media (max-width: 968px) {
            .content { grid-template-columns: 1fr; }
        }
        .form-panel {
            padding: 30px;
            border-right: 1px solid #eee;
        }
        .preview-panel {
            padding: 30px;
            background: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            overflow-y: auto;
            max-height: 600px;
            min-height: 600px;
            position: relative;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
            font-family: 'Courier New', monospace;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 30px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-right: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .download-btn {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .status {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-weight: 500;
            animation: slideIn 0.3s;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .status.info {
            background: #e3f2fd;
            color: #1976d2;
            border-left: 4px solid #1976d2;
        }
        .status.success {
            background: #e8f5e9;
            color: #388e3c;
            border-left: 4px solid #388e3c;
        }
        .status.error {
            background: #ffebee;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }
        .file-list {
            margin-top: 20px;
        }
        .file-item {
            background: #2d2d2d;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .file-item h3 {
            margin: 0 0 10px 0;
            color: #4fc3f7;
            font-size: 16px;
        }
        .file-item pre {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        .code-output {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 13px;
            line-height: 1.6;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 4px;
            min-height: 400px;
            overflow-y: auto;
            border: 1px solid #444;
        }
        .code-output::selection {
            background: #264f78;
        }
        .code-output:empty::before {
            content: 'Code will appear here as it generates...';
            color: #666;
            font-style: italic;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #444;
        }
        .preview-header h2 {
            color: #4fc3f7;
            font-size: 1.3em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CodeCraft - Live Code Preview</h1>
            <p>Watch your backend code generate in real-time</p>
        </div>
        
        <div class="content">
            <div class="form-panel">
                <form id="generateForm">
                    <div class="form-group">
                        <label for="prompt">Describe your backend requirements:</label>
                        <textarea id="prompt" name="prompt" placeholder="e.g., Create a REST API for a blog with users, posts, and comments. Users can create posts and comment on posts." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="arch_type">Architecture Type:</label>
                        <select id="arch_type" name="arch_type">
                            <option value="Monolith">Monolith</option>
                            <option value="Microservices">Microservices</option>
                        </select>
                    </div>
                    
                    <button type="submit" id="generateBtn">▶️ Generate Backend</button>
                    <button type="button" id="downloadBtn" class="download-btn" style="display:none;">📦 Download ZIP</button>
                </form>
                
                <div id="status" class="status info" style="display:none;"></div>
                
                <div id="fileList" class="file-list"></div>
            </div>
            
            <div class="preview-panel">
                <div class="preview-header">
                    <h2>📝 Live Code Preview</h2>
                    <span id="loadingIndicator" style="display:none;"><div class="loading"></div></span>
                </div>
                <div id="codeOutput" class="code-output">
                    <div style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                        ⬅️ Enter a prompt and click "Generate Backend" to see code appear here in real-time!
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('generateForm');
        const statusDiv = document.getElementById('status');
        const codeOutput = document.getElementById('codeOutput');
        const fileList = document.getElementById('fileList');
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const loadingIndicator = document.getElementById('loadingIndicator');
        let currentProjectId = null;
        let fullCode = '';
        let eventSource = null;

        function showStatus(message, type = 'info') {
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
        }

        function hideStatus() {
            statusDiv.style.display = 'none';
        }

        function resetUI() {
            codeOutput.textContent = 'Code will appear here as it generates...';
            fileList.innerHTML = '';
            fullCode = '';
            currentProjectId = null;
            downloadBtn.style.display = 'none';
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Close previous connection if any
            if (eventSource) {
                eventSource.close();
            }
            
            const prompt = document.getElementById('prompt').value;
            const arch_type = document.getElementById('arch_type').value;
            
            generateBtn.disabled = true;
            loadingIndicator.style.display = 'block';
            resetUI();
            
            showStatus('🔗 Connecting to server...', 'info');
            codeOutput.textContent = 'Connecting and starting generation...\n';
            codeOutput.style.color = '#4fc3f7';

            try {
                const formData = new FormData();
                formData.append('prompt', prompt);
                formData.append('arch_type', arch_type);

                // Use Fetch API with streaming
                const response = await fetch('/nodegen/prompt-to-backend-stream', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('HTTP error response:', errorText);
                    throw new Error(`HTTP error! status: ${response.status} - ${errorText.substring(0, 200)}`);
                }
                
                console.log('✅ Connected to streaming endpoint, starting to receive data...');

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        loadingIndicator.style.display = 'none';
                        break;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    
                    // Keep the last incomplete line in buffer
                    buffer = lines.pop() || '';

                    for (const line of lines) {
                        if (line.trim() === '') continue; // Skip empty lines
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                
                                if (data.type === 'start') {
                                    currentProjectId = data.project_id;
                                    showStatus('🚀 Starting code generation...', 'info');
                                    codeOutput.textContent = '🚀 Code generation started...\n\n';
                                    codeOutput.style.color = '#d4d4d4';
                                    fullCode = '🚀 Code generation started...\n\n';
                                } else if (data.type === 'stream') {
                                    // Append content immediately for real-time preview (like Streamlit)
                                    const content = data.content || '';
                                    if (content) {
                                        fullCode += content;
                                        
                                        // Update code display with proper formatting
                                        codeOutput.textContent = fullCode;
                                        codeOutput.style.color = '#d4d4d4';
                                        
                                        // Auto-scroll to bottom to see latest code
                                        requestAnimationFrame(() => {
                                            codeOutput.scrollTop = codeOutput.scrollHeight;
                                        });
                                        
                                        // Also show in console for debugging
                                        console.log('Streaming content:', content.substring(0, 50));
                                    }
                                } else if (data.type === 'file') {
                                    showStatus(`✅ Generated file: ${data.filename}`, 'success');
                                    const fileDiv = document.createElement('div');
                                    fileDiv.className = 'file-item';
                                    fileDiv.innerHTML = `
                                        <h3>📄 ${data.filename} <small>(${data.size} bytes)</small></h3>
                                        <pre>${data.preview || 'Preview not available'}</pre>
                                    `;
                                    fileList.appendChild(fileDiv);
                                } else if (data.type === 'complete') {
                                    showStatus(`🎉 ${data.message || 'Generation complete!'} ${data.files_count} files generated.`, 'success');
                                    downloadBtn.style.display = 'inline-block';
                                    downloadBtn.onclick = () => {
                                        window.location.href = `/nodegen/download/${currentProjectId}`;
                                    };
                                    loadingIndicator.style.display = 'none';
                                    generateBtn.disabled = false;
                                } else if (data.type === 'error') {
                                    showStatus(`❌ Error: ${data.message}`, 'error');
                                    loadingIndicator.style.display = 'none';
                                    generateBtn.disabled = false;
                                } else if (data.type === 'info') {
                                    showStatus(data.message, 'info');
                                }
                            } catch (e) {
                                console.error('Error parsing SSE data:', e);
                                console.error('Problematic line:', line.substring(0, 100));
                                // Try to show raw content if JSON parsing fails
                                if (line.includes('data:')) {
                                    console.log('Raw data line:', line);
                                }
                            }
                        }
                    }
                }
                
                // Process any remaining buffer
                if (buffer.trim()) {
                    const lines = buffer.split('\n');
                    for (const line of lines) {
                        if (line.trim() && line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.type === 'stream') {
                                    const content = data.content || '';
                                    if (content) {
                                        fullCode += content;
                                        codeOutput.textContent = fullCode;
                                        codeOutput.style.color = '#d4d4d4';
                                    }
                                }
                            } catch (e) {
                                console.error('Error parsing final buffer:', e, 'Line:', line);
                            }
                        }
                    }
                }
                
                // Final update
                if (fullCode) {
                    codeOutput.textContent = fullCode;
                    codeOutput.style.color = '#d4d4d4';
                }
            } catch (error) {
                console.error('Full error:', error);
                showStatus(`❌ Error: ${error.message}`, 'error');
                codeOutput.textContent = `❌ Error: ${error.message}\n\nCheck browser console (F12) for details.`;
                codeOutput.style.color = '#ff6b6b';
                loadingIndicator.style.display = 'none';
                generateBtn.disabled = false;
            }
        });
        
        // Auto-submit if query parameters are provided
        window.addEventListener('DOMContentLoaded', () => {
            const urlParams = new URLSearchParams(window.location.search);
            const promptParam = urlParams.get('prompt');
            const archParam = urlParams.get('arch_type');
            
            if (promptParam) {
                // Set form values
                document.getElementById('prompt').value = decodeURIComponent(promptParam);
                if (archParam) {
                    document.getElementById('arch_type').value = decodeURIComponent(archParam);
                }
                
                // Auto-submit after a short delay to ensure everything is loaded
                setTimeout(() => {
                    form.dispatchEvent(new Event('submit'));
                }, 500);
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/documentation/analyze-backend")
async def analyze_backend(file: UploadFile = File(...)):
    """
    Analyze a backend ZIP file and generate comprehensive API documentation.
    """
    # Validate file type
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


@app.post("/claude-documentation", tags=["Default"])
async def claude_documentation(file: UploadFile = File(...)):
    """
    Claude Documentation endpoint - Alias for /documentation/analyze-backend
    
    Analyzes a backend ZIP file and generates comprehensive API documentation.
    This endpoint is named after Claude AI's documentation feature for compatibility.
    """
    # Reuse the same logic as analyze_backend
    return await analyze_backend(file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
