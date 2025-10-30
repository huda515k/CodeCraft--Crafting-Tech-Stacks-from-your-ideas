# backend_generator/PromptAnalysis/models.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class PermissionType(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    UPDATE = "update"
    CREATE = "create"
    ADMIN = "admin"
    MANAGE = "manage"

class AccessLevel(str, Enum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ROLE_BASED = "role_based"
    OWNER_ONLY = "owner_only"
    ADMIN_ONLY = "admin_only"

class BusinessRuleType(str, Enum):
    VALIDATION = "validation"
    AUTHORIZATION = "authorization"
    WORKFLOW = "workflow"
    DATA_INTEGRITY = "data_integrity"
    BUSINESS_LOGIC = "business_logic"
    AUDIT = "audit"

class Role(BaseModel):
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(default=None, description="Role description")
    permissions: List[PermissionType] = Field(..., description="List of permissions for this role")
    access_level: AccessLevel = Field(default=AccessLevel.ROLE_BASED, description="Access level for this role")
    entity_access: Dict[str, List[PermissionType]] = Field(default_factory=dict, description="Entity-specific permissions")

class BusinessRule(BaseModel):
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    rule_type: BusinessRuleType = Field(..., description="Type of business rule")
    entity: Optional[str] = Field(default=None, description="Entity this rule applies to")
    condition: str = Field(..., description="Rule condition or logic")
    action: str = Field(..., description="Action to take when rule is triggered")
    priority: int = Field(default=1, description="Rule priority (1=highest)")

class UserAccess(BaseModel):
    user_id: str = Field(..., description="User identifier")
    roles: List[str] = Field(..., description="List of role names assigned to user")
    custom_permissions: List[PermissionType] = Field(default_factory=list, description="Custom permissions beyond roles")
    restrictions: List[str] = Field(default_factory=list, description="Access restrictions")

class PromptAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="User prompt containing role-based access and business rules")
    erd_schema: Optional[Dict[str, Any]] = Field(default=None, description="ERD schema to apply rules to")
    existing_backend: Optional[Dict[str, Any]] = Field(default=None, description="Existing backend structure for modifications")
    context: Optional[str] = Field(default=None, description="Additional context for analysis")

class PromptAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether analysis was successful")
    roles: List[Role] = Field(default_factory=list, description="Extracted roles")
    business_rules: List[BusinessRule] = Field(default_factory=list, description="Extracted business rules")
    user_access: List[UserAccess] = Field(default_factory=list, description="User access definitions")
    generated_code: Optional[Dict[str, Any]] = Field(default=None, description="Generated authorization code")
    modifications: Optional[Dict[str, Any]] = Field(default=None, description="Backend modifications")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    analysis_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis metadata")

class BackendModificationRequest(BaseModel):
    backend_code: str = Field(..., description="Existing backend code")
    modification_prompt: str = Field(..., description="Prompt describing desired modifications")
    current_roles: Optional[List[Role]] = Field(default=None, description="Current role definitions")
    current_rules: Optional[List[BusinessRule]] = Field(default=None, description="Current business rules")

class BackendModificationResponse(BaseModel):
    success: bool = Field(..., description="Whether modification was successful")
    modified_code: Optional[str] = Field(default=None, description="Modified backend code")
    new_roles: List[Role] = Field(default_factory=list, description="New or updated roles")
    new_rules: List[BusinessRule] = Field(default_factory=list, description="New or updated business rules")
    changes_summary: List[str] = Field(default_factory=list, description="Summary of changes made")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
