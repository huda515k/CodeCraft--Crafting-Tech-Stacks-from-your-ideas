# backend_generator/PromptAnalysis/prompt_parser.py

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from .models import Role, BusinessRule, UserAccess, PermissionType, BusinessRuleType, AccessLevel

class PromptParser:
    """
    AI-powered prompt parser for extracting role-based access and business rules
    """
    
    def __init__(self):
        self.role_keywords = [
            'role', 'roles', 'user role', 'user roles', 'permission', 'permissions',
            'access', 'authorization', 'privilege', 'privileges', 'admin', 'user',
            'manager', 'employee', 'customer', 'guest', 'member'
        ]
        
        self.business_rule_keywords = [
            'rule', 'rules', 'business rule', 'business rules', 'policy', 'policies',
            'constraint', 'constraints', 'validation', 'workflow', 'process',
            'requirement', 'requirements', 'logic', 'condition', 'condition'
        ]
        
        self.permission_keywords = {
            'read': ['read', 'view', 'see', 'access', 'retrieve', 'get'],
            'write': ['write', 'create', 'add', 'insert', 'post'],
            'update': ['update', 'edit', 'modify', 'change', 'put', 'patch'],
            'delete': ['delete', 'remove', 'destroy', 'eliminate'],
            'admin': ['admin', 'administrator', 'manage', 'control', 'superuser'],
            'manage': ['manage', 'control', 'oversee', 'supervise']
        }

    def parse_prompt(self, prompt: str) -> 'PromptAnalysisResponse':
        """
        Parse user prompt to extract roles, business rules, and user access patterns
        """
        from .models import PromptAnalysisResponse
        
        roles = self._extract_roles(prompt)
        business_rules = self._extract_business_rules(prompt)
        user_access = self._extract_user_access(prompt)
        
        return PromptAnalysisResponse(
            success=True,
            roles=roles,
            business_rules=business_rules,
            user_access=user_access,
            analysis_method="basic_parser"
        )
    
    def _extract_roles(self, prompt: str) -> List[Role]:
        """Extract roles and permissions from prompt"""
        roles = []
        
        # Look for role definitions
        role_patterns = [
            r'(?:role|user)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:can|has|should|must)\s+(.*?)(?:\n|\.|$)',
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:role|user)\s+(?:can|has|should|must)\s+(.*?)(?:\n|\.|$)',
            r'(?:admin|manager|employee|customer|guest|member)\s+(?:can|has|should|must)\s+(.*?)(?:\n|\.|$)'
        ]
        
        for pattern in role_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                role_name = match.group(1).strip()
                permissions_text = match.group(2).strip()
                
                # Extract permissions from the text
                permissions = self._extract_permissions(permissions_text)
                
                if permissions:
                    role = Role(
                        name=role_name,
                        description=f"Role extracted from prompt: {permissions_text[:100]}...",
                        permissions=permissions,
                        access_level=AccessLevel.ROLE_BASED
                    )
                    roles.append(role)
        
        # Look for explicit role definitions
        explicit_roles = self._find_explicit_roles(prompt)
        roles.extend(explicit_roles)
        
        return roles
    
    def _extract_business_rules(self, prompt: str) -> List[BusinessRule]:
        """Extract business rules from prompt"""
        rules = []
        
        # Look for rule patterns
        rule_patterns = [
            r'(?:rule|policy|constraint):\s*(.*?)(?:\n|$)',
            r'(?:if|when|whenever)\s+(.*?)\s+(?:then|do|should|must)\s+(.*?)(?:\n|\.|$)',
            r'(?:validate|check|ensure)\s+(.*?)(?:\n|\.|$)',
            r'(?:only|restrict|limit)\s+(.*?)(?:\n|\.|$)'
        ]
        
        for pattern in rule_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) >= 2:
                    condition = match.group(1).strip()
                    action = match.group(2).strip()
                else:
                    condition = match.group(1).strip()
                    action = "Apply rule"
                
                rule_type = self._classify_rule_type(condition)
                
                rule = BusinessRule(
                    name=f"Rule_{len(rules) + 1}",
                    description=f"Business rule: {condition}",
                    rule_type=rule_type,
                    condition=condition,
                    action=action,
                    priority=1
                )
                rules.append(rule)
        
        return rules
    
    def _extract_user_access(self, prompt: str) -> List[UserAccess]:
        """Extract user access patterns from prompt"""
        user_access = []
        
        # Look for user-specific access patterns
        user_patterns = [
            r'user\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:has|can|should)\s+(.*?)(?:\n|\.|$)',
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:user|person)\s+(?:has|can|should)\s+(.*?)(?:\n|\.|$)'
        ]
        
        for pattern in user_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                user_id = match.group(1).strip()
                access_text = match.group(2).strip()
                
                # Extract roles and permissions
                roles = self._extract_role_names(access_text)
                permissions = self._extract_permissions(access_text)
                
                access = UserAccess(
                    user_id=user_id,
                    roles=roles,
                    custom_permissions=permissions
                )
                user_access.append(access)
        
        return user_access
    
    def _extract_permissions(self, text: str) -> List[PermissionType]:
        """Extract permissions from text"""
        permissions = []
        text_lower = text.lower()
        
        for perm_type, keywords in self.permission_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    try:
                        permission = PermissionType(perm_type)
                        if permission not in permissions:
                            permissions.append(permission)
                    except ValueError:
                        continue
        
        return permissions
    
    def _extract_role_names(self, text: str) -> List[str]:
        """Extract role names from text"""
        roles = []
        
        # Look for role names
        role_pattern = r'\b(admin|manager|employee|customer|guest|member|user|admin|superuser)\b'
        matches = re.finditer(role_pattern, text, re.IGNORECASE)
        
        for match in matches:
            role_name = match.group(1).lower()
            if role_name not in roles:
                roles.append(role_name)
        
        return roles
    
    def _find_explicit_roles(self, prompt: str) -> List[Role]:
        """Find explicitly defined roles"""
        roles = []
        
        # Look for structured role definitions
        role_def_pattern = r'(?:role|user)\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\{([^}]*)\}'
        matches = re.finditer(role_def_pattern, prompt, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            role_name = match.group(1).strip()
            role_content = match.group(2).strip()
            
            permissions = self._extract_permissions(role_content)
            
            if permissions:
                role = Role(
                    name=role_name,
                    description=f"Explicitly defined role: {role_content[:100]}...",
                    permissions=permissions,
                    access_level=AccessLevel.ROLE_BASED
                )
                roles.append(role)
        
        return roles
    
    def _classify_rule_type(self, condition: str) -> BusinessRuleType:
        """Classify business rule type based on condition"""
        condition_lower = condition.lower()
        
        if any(word in condition_lower for word in ['validate', 'check', 'verify', 'ensure']):
            return BusinessRuleType.VALIDATION
        elif any(word in condition_lower for word in ['authorize', 'permit', 'allow', 'deny', 'access']):
            return BusinessRuleType.AUTHORIZATION
        elif any(word in condition_lower for word in ['workflow', 'process', 'step', 'stage']):
            return BusinessRuleType.WORKFLOW
        elif any(word in condition_lower for word in ['integrity', 'consistency', 'constraint']):
            return BusinessRuleType.DATA_INTEGRITY
        elif any(word in condition_lower for word in ['audit', 'log', 'track', 'monitor']):
            return BusinessRuleType.AUDIT
        else:
            return BusinessRuleType.BUSINESS_LOGIC
    
    def parse_modification_prompt(self, prompt: str, existing_roles: List[Role], existing_rules: List[BusinessRule]) -> Tuple[List[Role], List[BusinessRule], List[str]]:
        """
        Parse modification prompt to update existing roles and rules
        """
        # Extract new roles and rules
        parser_result = self.parse_prompt(prompt)
        new_roles = parser_result.roles
        new_rules = parser_result.business_rules
        
        # Look for modification keywords
        modification_keywords = [
            'add', 'create', 'new', 'include', 'add role', 'add rule',
            'update', 'modify', 'change', 'edit', 'alter',
            'remove', 'delete', 'exclude', 'disable',
            'enable', 'activate', 'deactivate'
        ]
        
        changes = []
        
        # Check for additions
        if 'add' in prompt.lower() or 'create' in prompt.lower() or 'new' in prompt.lower():
            changes.append("Added new roles and business rules")
        
        # Check for modifications
        if 'update' in prompt.lower() or 'modify' in prompt.lower() or 'change' in prompt.lower():
            changes.append("Updated existing roles and business rules")
        
        # Check for removals
        if 'remove' in prompt.lower() or 'delete' in prompt.lower():
            changes.append("Removed specified roles and business rules")
        
        return new_roles, new_rules, changes
