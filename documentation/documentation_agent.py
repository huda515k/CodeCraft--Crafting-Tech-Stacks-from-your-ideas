from typing import Dict, List, Any, Optional, TypedDict
from pathlib import Path
import os
import json
import re
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)


class BackendState(TypedDict):
    """State definition for the workflow"""
    backend_path: str
    files_content: Dict[str, str]
    routes: List[Dict]
    models: List[Dict]
    controllers: List[Dict]
    middlewares: List[Dict]
    documentation: Dict
    errors: List[str]


class DocumentationAgent:
    """Agent for analyzing Node.js/Express backends and generating API documentation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the documentation agent"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        
        # Initialize LLM with correct model name
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for backend analysis"""
        workflow = StateGraph(BackendState)
        
        # Define nodes
        workflow.add_node("scan_files", self._scan_files_node)
        workflow.add_node("extract_routes", self._extract_routes_node)
        workflow.add_node("analyze_models", self._analyze_models_node)
        workflow.add_node("analyze_controllers", self._analyze_controllers_node)
        workflow.add_node("analyze_middlewares", self._analyze_middlewares_node)
        workflow.add_node("generate_documentation", self._generate_documentation_node)
        
        # Define edges
        workflow.set_entry_point("scan_files")
        workflow.add_edge("scan_files", "extract_routes")
        workflow.add_edge("extract_routes", "analyze_models")
        workflow.add_edge("analyze_models", "analyze_controllers")
        workflow.add_edge("analyze_controllers", "analyze_middlewares")
        workflow.add_edge("analyze_middlewares", "generate_documentation")
        workflow.add_edge("generate_documentation", END)
        
        return workflow.compile()
    
    async def analyze_backend(self, backend_path: str) -> Dict:
        """Main entry point for analyzing a backend"""
        initial_state = {
            "backend_path": backend_path,
            "files_content": {},
            "routes": [],
            "models": [],
            "controllers": [],
            "middlewares": [],
            "documentation": {},
            "errors": []
        }
        
        # Run the workflow
        logger.info("Starting backend analysis workflow...")
        result = await self.workflow.ainvoke(initial_state)
        
        logger.info(f"Workflow completed. Documentation keys: {result.get('documentation', {}).keys()}")
        
        return result.get('documentation', {})
    
    def _scan_files_node(self, state: Dict) -> Dict:
        """Scan and read all relevant files in the backend"""
        logger.info("=== SCANNING FILES ===")
        
        backend_path = Path(state["backend_path"])
        relevant_extensions = ['.js', '.ts', '.json']
        exclude_dirs = ['node_modules', 'dist', 'build', 'coverage', '.git', 'test', 'tests']
        
        files_content = {}
        errors = state.get("errors", [])
        
        logger.info(f"Scanning directory: {backend_path}")
        
        for file_path in backend_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in relevant_extensions:
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue
                
                try:
                    relative_path = file_path.relative_to(backend_path)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if content.strip():  # Only add non-empty files
                            files_content[str(relative_path)] = content
                            logger.info(f"  ✓ Read: {relative_path} ({len(content)} chars)")
                except Exception as e:
                    logger.warning(f"  ✗ Could not read {file_path}: {e}")
                    errors.append(f"Error reading {file_path}: {str(e)}")
        
        logger.info(f"Total files scanned: {len(files_content)}")
        
        # Log file categories
        route_files = [f for f in files_content.keys() if 'route' in f.lower() or 'app.js' in f.lower()]
        model_files = [f for f in files_content.keys() if 'model' in f.lower() or 'schema' in f.lower()]
        controller_files = [f for f in files_content.keys() if 'controller' in f.lower()]
        
        logger.info(f"  Route files: {len(route_files)}")
        logger.info(f"  Model files: {len(model_files)}")
        logger.info(f"  Controller files: {len(controller_files)}")
        
        return {
            **state,
            "files_content": files_content,
            "errors": errors
        }
    
    def _extract_routes_node(self, state: Dict) -> Dict:
        """Extract API routes from the backend files"""
        logger.info("=== EXTRACTING ROUTES ===")
        
        files_content = state.get("files_content", {})
        routes_files = {
            path: content for path, content in files_content.items()
            if 'route' in path.lower() or 'router' in path.lower() or 'app.js' in path.lower() or 'index.js' in path.lower()
        }
        
        logger.info(f"Found {len(routes_files)} potential route files")
        for path in routes_files.keys():
            logger.info(f"  - {path}")
        
        routes = []
        errors = state.get("errors", [])
        
        for file_path, content in routes_files.items():
            logger.info(f"\nAnalyzing routes in: {file_path}")
            
            # First try regex-based extraction (faster and more reliable)
            extracted_routes = self._extract_routes_with_regex(file_path, content)
            if extracted_routes:
                routes.extend(extracted_routes)
                logger.info(f"  ✓ Extracted {len(extracted_routes)} routes with regex")
                continue
            
            # Fallback to LLM if regex doesn't work
            try:
                logger.info(f"  Trying LLM extraction...")
                
                # Truncate content if too long
                max_content_length = 8000
                truncated_content = content[:max_content_length] if len(content) > max_content_length else content
                
                prompt = f"""Analyze this Express.js/Node.js route file and extract ALL API routes.

File: {file_path}

Code:
{truncated_content}

For EACH route found, return a JSON array with objects containing:
- method: HTTP method (GET, POST, PUT, DELETE, PATCH)
- path: the route path/endpoint (e.g., "/api/users", "/users/:id")
- description: brief description of what the route does
- handler: function name handling the route

Return ONLY a valid JSON array, nothing else. Example:
[
  {{"method": "GET", "path": "/api/users", "description": "Get all users", "handler": "getUsers"}},
  {{"method": "POST", "path": "/api/users", "description": "Create user", "handler": "createUser"}}
]"""

                response = self.llm.invoke(prompt)
                route_data = self._extract_json_from_response(response.content)
                
                if route_data and isinstance(route_data, list):
                    for route in route_data:
                        route['file'] = file_path
                        routes.append(route)
                    logger.info(f"  ✓ LLM extracted {len(route_data)} routes")
                else:
                    logger.warning(f"  ✗ LLM did not return valid JSON")
                    # Create a basic entry so we know this file was analyzed
                    routes.append({
                        'method': 'UNKNOWN',
                        'path': '/api',
                        'description': f'Routes defined in {file_path}',
                        'file': file_path,
                        'handler': 'See file for details'
                    })
                
            except Exception as e:
                logger.error(f"  ✗ Error extracting routes: {e}")
                errors.append(f"Error extracting routes from {file_path}: {str(e)}")
        
        logger.info(f"\nTotal routes extracted: {len(routes)}")
        
        return {
            **state,
            "routes": routes,
            "errors": errors
        }
    
    def _extract_routes_with_regex(self, file_path: str, content: str) -> List[Dict]:
        """Extract routes using regex patterns"""
        routes = []
        
        # Common Express.js route patterns
        patterns = [
            # router.get('/path', handler)
            r'router\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,',
            # app.get('/path', handler)
            r'app\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,',
            # router.route('/path').get(handler)
            r'router\.route\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\.\s*(get|post|put|delete|patch)',
            # app.route('/path').get(handler)
            r'app\.route\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\.\s*(get|post|put|delete|patch)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    # Determine which group is method and which is path
                    if groups[0].lower() in ['get', 'post', 'put', 'delete', 'patch']:
                        method = groups[0].upper()
                        path = groups[1]
                    else:
                        method = groups[1].upper()
                        path = groups[0]
                    
                    routes.append({
                        'method': method,
                        'path': path,
                        'description': f'{method} {path}',
                        'file': file_path,
                        'handler': 'Function in file'
                    })
        
        # Remove duplicates
        seen = set()
        unique_routes = []
        for route in routes:
            key = (route['method'], route['path'])
            if key not in seen:
                seen.add(key)
                unique_routes.append(route)
        
        return unique_routes
    
    def _analyze_models_node(self, state: Dict) -> Dict:
        """Analyze data models in the backend"""
        logger.info("Analyzing models...")
        models = []
        errors = state.get("errors", [])
        
        # Simple model extraction - look for model definitions
        for file_path, content in state.get("files_content", {}).items():
            if any(keyword in file_path.lower() for keyword in ['model', 'schema', 'entity']):
                try:
                    # Extract model information
                    models.append({
                        "name": Path(file_path).stem,
                        "file": file_path,
                        "type": "Data Model"
                    })
                except Exception as e:
                    errors.append(f"Error analyzing model in {file_path}: {str(e)}")
        
        logger.info(f"Analyzed {len(models)} models")
        return {
            "models": models,
            "errors": errors
        }
    
    def _analyze_controllers_node(self, state: Dict) -> Dict:
        """Analyze controllers in the backend"""
        logger.info("Analyzing controllers...")
        controllers = []
        errors = state.get("errors", [])
        
        # Simple controller extraction
        for file_path, content in state.get("files_content", {}).items():
            if any(keyword in file_path.lower() for keyword in ['controller', 'handler']):
                try:
                    controllers.append({
                        "name": Path(file_path).stem,
                        "file": file_path,
                        "type": "Controller"
                    })
                except Exception as e:
                    errors.append(f"Error analyzing controller in {file_path}: {str(e)}")
        
        logger.info(f"Analyzed {len(controllers)} controllers")
        return {
            "controllers": controllers,
            "errors": errors
        }
    
    def _analyze_middlewares_node(self, state: Dict) -> Dict:
        """Analyze middlewares in the backend"""
        logger.info("Analyzing middlewares...")
        middlewares = []
        errors = state.get("errors", [])
        
        # Simple middleware extraction
        for file_path, content in state.get("files_content", {}).items():
            if any(keyword in file_path.lower() for keyword in ['middleware', 'auth', 'cors']):
                try:
                    middlewares.append({
                        "name": Path(file_path).stem,
                        "file": file_path,
                        "type": "Middleware"
                    })
                except Exception as e:
                    errors.append(f"Error analyzing middleware in {file_path}: {str(e)}")
        
        logger.info(f"Analyzed {len(middlewares)} middlewares")
        return {
            "middlewares": middlewares,
            "errors": errors
        }
    
    def _generate_documentation_node(self, state: Dict) -> Dict:
        """Generate comprehensive API documentation"""
        logger.info("Generating documentation...")
        errors = state.get("errors", [])
        
        try:
            # Create comprehensive documentation
            documentation = {
                "api_documentation": {
                    "api_overview": {
                        "title": "Backend API Documentation",
                        "description": "Comprehensive API documentation generated from backend analysis",
                        "base_url": "http://localhost:3000",
                        "authentication_methods": ["JWT Bearer Token"],
                        "general_information": {
                            "rate_limiting": "Standard rate limits apply",
                            "data_format": "All requests and responses use JSON"
                        }
                    },
                    "authentication_authorization": {
                        "authentication_method": "JSON Web Token (JWT)",
                        "how_to_authenticate": "Include JWT token in Authorization header",
                        "token_format": "Bearer <token>",
                        "required_headers": [
                            {
                                "header": "Authorization",
                                "format": "Bearer <YOUR_JWT_TOKEN>",
                                "description": "JWT token for authentication"
                            }
                        ]
                    },
                    "endpoints": self._generate_endpoints_documentation(state.get("routes", [])),
                    "data_models": self._generate_models_documentation(state.get("models", [])),
                    "error_handling": {
                        "standard_errors": {
                            "400": "Bad Request - Invalid input data",
                            "401": "Unauthorized - Authentication required",
                            "403": "Forbidden - Insufficient permissions",
                            "404": "Not Found - Resource not found",
                            "500": "Internal Server Error - Server error"
                        }
                    }
                },
                "metadata": {
                    "total_routes": len(state.get("routes", [])),
                    "total_models": len(state.get("models", [])),
                    "total_controllers": len(state.get("controllers", [])),
                    "total_middlewares": len(state.get("middlewares", [])),
                    "analysis_errors": state.get("errors", [])
                }
            }
            
            logger.info("Documentation generated successfully")
            return {
                "documentation": documentation,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            return {
                "documentation": {},
                "errors": [f"Error generating documentation: {str(e)}"]
            }
    
    def _generate_endpoints_documentation(self, routes: List[Dict]) -> Dict:
        """Generate endpoints documentation from routes"""
        endpoints = {}
        
        for route in routes:
            method = route.get("method", "GET")
            path = route.get("path", route.get("route_path", "/"))
            
            endpoint_key = f"{method.upper()} {path}"
            endpoints[endpoint_key] = {
                "method": method.upper(),
                "path": path,
                "description": route.get("description", f"{method.upper()} {path}"),
                "parameters": route.get("parameters", {}),
                "handler": route.get("handler", route.get("route_handler", "Unknown")),
                "middleware": route.get("middleware", [])
            }
        
        return endpoints
    
    def _generate_models_documentation(self, models: List[Dict]) -> Dict:
        """Generate models documentation"""
        models_doc = {}
        
        for model in models:
            name = model.get("name", "Unknown")
            models_doc[name] = {
                "description": f"Data model: {name}",
                "type": model.get("type", "Data Model"),
                "file": model.get("file", "Unknown")
            }
        
        return models_doc
    
    def generate_markdown(self, documentation: Dict) -> str:
        """Generate markdown documentation from the analysis results"""
        try:
            if not documentation or not documentation.get("api_documentation"):
                return "# API Documentation\n\nNo documentation available."
            
            api_doc = documentation["api_documentation"]
            markdown = []
            
            # Title and overview
            overview = api_doc.get("api_overview", {})
            markdown.append(f"# {overview.get('title', 'API Documentation')}")
            markdown.append(f"\n{overview.get('description', '')}")
            markdown.append(f"\n**Base URL:** {overview.get('base_url', 'http://localhost:3000')}")
            
            # Authentication
            auth = api_doc.get("authentication_authorization", {})
            if auth:
                markdown.append(f"\n## Authentication")
                markdown.append(f"\n**Method:** {auth.get('authentication_method', 'JWT')}")
                markdown.append(f"\n**How to authenticate:** {auth.get('how_to_authenticate', '')}")
            
            # Endpoints
            endpoints = api_doc.get("endpoints", {})
            if endpoints:
                markdown.append(f"\n## API Endpoints")
                for endpoint_key, endpoint_info in endpoints.items():
                    markdown.append(f"\n### {endpoint_key}")
                    markdown.append(f"- **Method:** {endpoint_info.get('method', 'GET')}")
                    markdown.append(f"- **Path:** {endpoint_info.get('path', '/')}")
                    markdown.append(f"- **Description:** {endpoint_info.get('description', '')}")
                    markdown.append(f"- **Handler:** {endpoint_info.get('handler', 'Unknown')}")
            
            # Data Models
            models = api_doc.get("data_models", {})
            if models:
                markdown.append(f"\n## Data Models")
                for model_name, model_info in models.items():
                    markdown.append(f"\n### {model_name}")
                    markdown.append(f"- **Type:** {model_info.get('type', 'Data Model')}")
                    markdown.append(f"- **Description:** {model_info.get('description', '')}")
            
            # Error Handling
            error_handling = api_doc.get("error_handling", {})
            if error_handling:
                markdown.append(f"\n## Error Handling")
                standard_errors = error_handling.get("standard_errors", {})
                for code, description in standard_errors.items():
                    markdown.append(f"- **{code}:** {description}")
            
            return "\n".join(markdown)
            
        except Exception as e:
            logger.error(f"Error generating markdown: {str(e)}")
            return f"# API Documentation\n\nError generating documentation: {str(e)}"
    
    def generate_openapi(self, documentation: Dict) -> Dict:
        """Generate OpenAPI specification from the analysis results"""
        try:
            if not documentation or not documentation.get("api_documentation"):
                return {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "API Documentation",
                        "version": "1.0.0",
                        "description": "No documentation available"
                    },
                    "paths": {}
                }
            
            api_doc = documentation["api_documentation"]
            overview = api_doc.get("api_overview", {})
            endpoints = api_doc.get("endpoints", {})
            
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": overview.get("title", "API Documentation"),
                    "version": "1.0.0",
                    "description": overview.get("description", "API Documentation"),
                    "servers": [
                        {
                            "url": overview.get("base_url", "http://localhost:3000"),
                            "description": "API Server"
                        }
                    ]
                },
                "paths": {},
                "components": {
                    "securitySchemes": {
                        "bearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT"
                        }
                    }
                }
            }
            
            # Add paths from endpoints
            for endpoint_key, endpoint_info in endpoints.items():
                method = endpoint_info.get("method", "GET").lower()
                path = endpoint_info.get("path", "/")
                
                if path not in openapi_spec["paths"]:
                    openapi_spec["paths"][path] = {}
                
                openapi_spec["paths"][path][method] = {
                    "summary": endpoint_info.get("description", f"{method.upper()} {path}"),
                    "description": endpoint_info.get("description", f"{method.upper()} {path}"),
                    "responses": {
                        "200": {
                            "description": "Successful response"
                        },
                        "400": {
                            "description": "Bad Request"
                        },
                        "401": {
                            "description": "Unauthorized"
                        },
                        "404": {
                            "description": "Not Found"
                        },
                        "500": {
                            "description": "Internal Server Error"
                        }
                    }
                }
                
                # Add security if authentication is required
                if api_doc.get("authentication_authorization"):
                    openapi_spec["paths"][path][method]["security"] = [{"bearerAuth": []}]
            
            return openapi_spec
            
        except Exception as e:
            logger.error(f"Error generating OpenAPI spec: {str(e)}")
            return {
                "openapi": "3.0.0",
                "info": {
                    "title": "API Documentation",
                    "version": "1.0.0",
                    "description": f"Error generating documentation: {str(e)}"
                },
                "paths": {}
            }