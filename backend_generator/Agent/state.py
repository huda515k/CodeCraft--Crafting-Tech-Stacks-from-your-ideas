from typing import Dict, List, Optional, Any, TypedDict
from pydantic import BaseModel

class ProcessingResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class AgentState(TypedDict):
    # User input
    user_request: str
    uploaded_file: Optional[bytes]
    
    # Processing state
    current_step: str
    erd_schema: Optional[Dict[str, Any]]
    processing_results: List[ProcessingResult]
    
    # Agent memory
    conversation_history: List[Dict[str, str]]
    user_preferences: Dict[str, Any]
    
    # Output
    generated_backend: Optional[Dict[str, Any]]
    final_response: Optional[str]
    
    # Error handling
    retry_count: int
    last_error: Optional[str]
