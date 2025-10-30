# backend_generator/PromptAnalysis/enhanced_parser.py

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from .models import Role, BusinessRule, UserAccess, PermissionType, BusinessRuleType, AccessLevel

class EnhancedPromptParser:
    """
    Enhanced prompt parser with improved pattern recognition and analysis
    """
    
    def __init__(self):
        self.role_patterns = [
            # Direct role definitions
            r'(?:role|user)\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\{([^}]*)\}',
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:role|user)\s+(?:can|has|should|must)\s+(.*?)(?:\n|\.|$)',
            r'(?:admin|manager|employee|customer|guest|member|user|superuser)\s+(?:can|has|should|must)\s+(.*?)(?:\n|\.|$)',
            # Role with permissions
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*?)(?:\n|$)',
            # Implicit roles
            r'(?:only|restrict)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:can|should|must)\s+(.*?)(?:\n|\.|$)',
            # Multiple roles in one sentence
            r'([A-Z][a-zA-Z_]*)\s+(?:can|has|should|must)\s+(.*?)(?:\.|,|$)',
            # Role patterns with specific actions
            r'([A-Z][a-zA-Z_]*)\s+(?:can|may|should|must)\s+(?:manage|access|view|create|update|delete|read|write)\s+(.*?)(?:\.|,|$)',
            # Simple role patterns
            r'([A-Z][a-zA-Z_]*)\s+(?:role|user|account)\s+(?:can|has|should|must)\s+(.*?)(?:\.|,|$)'
        ]
        
        self.business_rule_patterns = [
            r'(?:rule|policy|constraint|requirement)\s*:\s*(.*?)(?:\n|$)',
            r'(?:if|when|whenever)\s+(.*?)\s+(?:then|do|should|must)\s+(.*?)(?:\n|\.|$)',
            r'(?:validate|check|ensure|require)\s+(.*?)(?:\n|\.|$)',
            r'(?:only|restrict|limit)\s+(.*?)(?:\n|\.|$)',
            r'(?:must|should|cannot|can\'t)\s+(.*?)(?:\n|\.|$)',
            r'(?:business\s+rule|constraint)\s*:\s*(.*?)(?:\n|$)'
        ]
        
        self.permission_mapping = {
            'read': ['read', 'view', 'see', 'access', 'retrieve', 'get', 'fetch'],
            'write': ['write', 'create', 'add', 'insert', 'post', 'new'],
            'update': ['update', 'edit', 'modify', 'change', 'put', 'patch', 'alter'],
            'delete': ['delete', 'remove', 'destroy', 'eliminate', 'drop'],
            'admin': ['admin', 'administrator', 'superuser', 'root'],
            'manage': ['manage', 'control', 'oversee', 'supervise', 'handle']
        }
        
        self.rule_type_keywords = {
            'validation': ['validate', 'check', 'verify', 'ensure', 'must have', 'should have'],
            'authorization': ['authorize', 'permit', 'allow', 'deny', 'access', 'permission'],
            'workflow': ['workflow', 'process', 'step', 'stage', 'approve', 'reject'],
            'data_integrity': ['integrity', 'consistency', 'constraint', 'unique', 'primary'],
            'business_logic': ['logic', 'rule', 'policy', 'business', 'requirement'],
            'audit': ['audit', 'log', 'track', 'monitor', 'record', 'history']
        }

    def parse_prompt(self, prompt: str) -> 'PromptAnalysisResponse':
        """
        Enhanced prompt parsing with better pattern recognition
        """
        from .models import PromptAnalysisResponse
        
        roles = self._extract_roles_enhanced(prompt)
        business_rules = self._extract_business_rules_enhanced(prompt)
        user_access = self._extract_user_access_enhanced(prompt)
        
        return PromptAnalysisResponse(
            success=True,
            roles=roles,
            business_rules=business_rules,
            user_access=user_access,
            analysis_method="enhanced_parser"
        )
    
    def _extract_roles_enhanced(self, prompt: str) -> List[Role]:
        """Enhanced role extraction with better pattern matching"""
        roles = []
        
        # First, try to extract multiple roles from comma-separated lists
        multi_role_patterns = [
            r'([A-Z][a-zA-Z_]*)\s+(?:can|may|should|must)\s+(.*?)(?:,\s*([A-Z][a-zA-Z_]*)\s+(?:can|may|should|must)\s+(.*?))*(?:\.|$)',
            r'([A-Z][a-zA-Z_]*)\s+(?:role|user|account)\s+(?:can|has|should|must)\s+(.*?)(?:,\s*([A-Z][a-zA-Z_]*)\s+(?:role|user|account)\s+(?:can|has|should|must)\s+(.*?))*(?:\.|$)',
        ]
        
        for pattern in multi_role_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    # Extract all role groups
                    groups = match.groups()
                    for i in range(0, len(groups), 2):
                        if i + 1 < len(groups) and groups[i] and groups[i + 1]:
                            role_name = groups[i].strip()
                            role_content = groups[i + 1].strip()
                            
                            if role_name and role_content:
                                permissions = self._extract_permissions_enhanced(role_content)
                                access_level = self._determine_access_level(role_name, role_content)
                                entity_access = self._extract_entity_access(role_content)
                                
                                role = Role(
                                    name=role_name,
                                    description=f"Role extracted from: {role_content[:100]}...",
                                    permissions=permissions,
                                    access_level=access_level,
                                    entity_access=entity_access
                                )
                                roles.append(role)
                except Exception as e:
                    print(f"Error processing multi-role match: {e}")
                    continue
        
        # Split prompt into sections for better analysis
        sections = self._split_prompt_sections(prompt)
        
        for section in sections:
            # Look for explicit role definitions
            for pattern in self.role_patterns:
                matches = re.finditer(pattern, section, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        if len(match.groups()) >= 2:
                            role_name = match.group(1).strip()
                            role_content = match.group(2).strip()
                        else:
                            # Try to extract role name from content
                            role_name = self._extract_role_name_from_content(section)
                            role_content = section
                        
                        if role_name and role_content:
                            permissions = self._extract_permissions_enhanced(role_content)
                            access_level = self._determine_access_level(role_name, role_content)
                            entity_access = self._extract_entity_access(role_content)
                            
                            role = Role(
                                name=role_name,
                                description=f"Role extracted from: {role_content[:100]}...",
                                permissions=permissions,
                                access_level=access_level,
                                entity_access=entity_access
                            )
                            roles.append(role)
                    except Exception as e:
                        print(f"Error processing role match: {e}")
                        continue
        
        # Remove duplicates
        unique_roles = []
        seen_names = set()
        for role in roles:
            if role.name not in seen_names:
                unique_roles.append(role)
                seen_names.add(role.name)
        
        return unique_roles
    
    def _extract_business_rules_enhanced(self, prompt: str) -> List[BusinessRule]:
        """Enhanced business rule extraction"""
        rules = []
        
        sections = self._split_prompt_sections(prompt)
        
        for section in sections:
            for pattern in self.business_rule_patterns:
                matches = re.finditer(pattern, section, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        if len(match.groups()) >= 2:
                            condition = match.group(1).strip()
                            action = match.group(2).strip()
                        else:
                            condition = match.group(1).strip()
                            action = "Apply rule"
                        
                        rule_type = self._classify_rule_type_enhanced(condition)
                        entity = self._extract_entity_from_rule(condition)
                        
                        rule = BusinessRule(
                            name=f"Rule_{len(rules) + 1}",
                            description=f"Business rule: {condition}",
                            rule_type=rule_type,
                            entity=entity,
                            condition=condition,
                            action=action,
                            priority=1
                        )
                        rules.append(rule)
                    except Exception as e:
                        print(f"Error processing business rule: {e}")
                        continue
        
        return rules
    
    def _extract_user_access_enhanced(self, prompt: str) -> List[UserAccess]:
        """Enhanced user access pattern extraction"""
        user_access = []
        
        # Look for user-specific patterns
        user_patterns = [
            r'user\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:has|can|should)\s+(.*?)(?:\n|\.|$)',
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:user|person)\s+(?:has|can|should)\s+(.*?)(?:\n|\.|$)',
            r'(?:assign|give)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:role|permission)\s+(.*?)(?:\n|\.|$)'
        ]
        
        for pattern in user_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    user_id = match.group(1).strip()
                    access_text = match.group(2).strip()
                    
                    roles = self._extract_role_names_from_text(access_text)
                    permissions = self._extract_permissions_enhanced(access_text)
                    restrictions = self._extract_restrictions(access_text)
                    
                    access = UserAccess(
                        user_id=user_id,
                        roles=roles,
                        custom_permissions=permissions,
                        restrictions=restrictions
                    )
                    user_access.append(access)
                except Exception as e:
                    print(f"Error processing user access: {e}")
                    continue
        
        return user_access
    
    def _split_prompt_sections(self, prompt: str) -> List[str]:
        """Split prompt into logical sections for better analysis"""
        # Split by common delimiters
        sections = re.split(r'\n\s*\n|\.\s*\n|;\s*\n', prompt)
        
        # Also split by role-related keywords
        role_sections = re.split(r'(?:roles?|users?|business\s+rules?|constraints?):', prompt, re.IGNORECASE)
        
        # Combine and clean sections
        all_sections = sections + role_sections
        cleaned_sections = []
        
        for section in all_sections:
            section = section.strip()
            if len(section) > 10:  # Only keep substantial sections
                cleaned_sections.append(section)
        
        return cleaned_sections
    
    def _extract_role_name_from_content(self, content: str) -> str:
        """Extract role name from content when not explicitly defined"""
        # Look for common role patterns
        role_patterns = [
            r'\b(admin|administrator|manager|employee|customer|guest|user|member|superuser)\b',
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:role|user)\b'
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return "Unknown"
    
    def _extract_permissions_enhanced(self, text: str) -> List[PermissionType]:
        """Enhanced permission extraction with better mapping"""
        permissions = []
        text_lower = text.lower()
        
        for perm_type, keywords in self.permission_mapping.items():
            for keyword in keywords:
                if keyword in text_lower:
                    try:
                        permission = PermissionType(perm_type)
                        if permission not in permissions:
                            permissions.append(permission)
                    except ValueError:
                        continue
        
        return permissions
    
    def _determine_access_level(self, role_name: str, content: str) -> AccessLevel:
        """Determine access level based on role name and content"""
        role_lower = role_name.lower()
        content_lower = content.lower()
        
        if 'admin' in role_lower or 'administrator' in role_lower:
            return AccessLevel.ADMIN_ONLY
        elif 'public' in content_lower or 'guest' in role_lower:
            return AccessLevel.PUBLIC
        elif 'owner' in content_lower or 'own' in content_lower:
            return AccessLevel.OWNER_ONLY
        elif 'authenticated' in content_lower:
            return AccessLevel.AUTHENTICATED
        else:
            return AccessLevel.ROLE_BASED
    
    def _extract_entity_access(self, content: str) -> Dict[str, List[str]]:
        """Extract entity-specific access patterns"""
        entity_access = {}
        
        # Look for entity-specific patterns
        entity_patterns = [
            r'(\w+)\s+(?:data|records|information)\s+(?:can|should|must)\s+(.*?)(?:\n|\.|$)',
            r'(?:access|manage|view)\s+(\w+)\s+(?:data|records|information)'
        ]
        
        for pattern in entity_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                entity = match.group(1).lower()
                permissions = self._extract_permissions_enhanced(match.group(2) if len(match.groups()) > 1 else content)
                entity_access[entity] = [p.value for p in permissions]
        
        return entity_access
    
    def _classify_rule_type_enhanced(self, condition: str) -> BusinessRuleType:
        """Enhanced rule type classification"""
        condition_lower = condition.lower()
        
        for rule_type, keywords in self.rule_type_keywords.items():
            for keyword in keywords:
                if keyword in condition_lower:
                    try:
                        return BusinessRuleType(rule_type)
                    except ValueError:
                        continue
        
        return BusinessRuleType.BUSINESS_LOGIC
    
    def _extract_entity_from_rule(self, condition: str) -> Optional[str]:
        """Extract entity name from business rule condition"""
        # Look for entity references in the condition
        entity_patterns = [
            r'\b(\w+)\s+(?:data|records|information|table|entity)\b',
            r'\b(?:in|for|of)\s+(\w+)\b'
        ]
        
        for pattern in entity_patterns:
            match = re.search(pattern, condition, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return None
    
    def _extract_role_names_from_text(self, text: str) -> List[str]:
        """Extract role names from text"""
        roles = []
        
        role_pattern = r'\b(admin|manager|employee|customer|guest|member|user|admin|superuser)\b'
        matches = re.finditer(role_pattern, text, re.IGNORECASE)
        
        for match in matches:
            role_name = match.group(1).lower()
            if role_name not in roles:
                roles.append(role_name)
        
        return roles
    
    def _extract_restrictions(self, text: str) -> List[str]:
        """Extract access restrictions from text"""
        restrictions = []
        
        restriction_patterns = [
            r'(?:cannot|cannot|can\'t|must not|should not)\s+(.*?)(?:\n|\.|$)',
            r'(?:restrict|limit|deny)\s+(.*?)(?:\n|\.|$)',
            r'(?:only|except)\s+(.*?)(?:\n|\.|$)'
        ]
        
        for pattern in restriction_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                restriction = match.group(1).strip()
                if restriction:
                    restrictions.append(restriction)
        
        return restrictions
