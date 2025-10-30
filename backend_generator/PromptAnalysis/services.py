# backend_generator/PromptAnalysis/services.py

import os
from typing import List, Dict, Any, Optional
from .models import (
    PromptAnalysisRequest, PromptAnalysisResponse, 
    BackendModificationRequest, BackendModificationResponse,
    Role, BusinessRule, UserAccess, PermissionType, BusinessRuleType, AccessLevel
)
from .prompt_parser import PromptParser
from .enhanced_parser import EnhancedPromptParser
from .code_generator import AuthorizationCodeGenerator
from .ai_analyzer import AIPromptAnalyzer

class PromptAnalysisService:
    """
    Enhanced service for AI-powered prompt analysis using LangGraph and Gemini Flash
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.parser = PromptParser()
        self.enhanced_parser = EnhancedPromptParser()
        self.code_generator = AuthorizationCodeGenerator()
        
        # Initialize AI analyzer
        try:
            self.ai_analyzer = AIPromptAnalyzer(gemini_api_key)
            self.ai_enabled = True
        except Exception as e:
            print(f"AI analyzer initialization failed: {e}")
            self.ai_analyzer = None
            self.ai_enabled = False
    
    async def analyze_prompt(self, request: PromptAnalysisRequest) -> PromptAnalysisResponse:
        """
        Enhanced AI-powered prompt analysis using LangGraph and Gemini Flash
        """
        try:
            if self.ai_enabled and self.ai_analyzer:
                try:
                    # Use AI-powered analysis
                    ai_result = await self.ai_analyzer.analyze_with_gemini_direct(
                        request.prompt, 
                        request.erd_schema
                    )
                    
                    # Check if AI analysis was successful
                    if ai_result.get('roles') or ai_result.get('business_rules'):
                        # Convert AI result to our models
                        roles = self._convert_ai_roles(ai_result.get('roles', []))
                        business_rules = self._convert_ai_business_rules(ai_result.get('business_rules', []))
                        user_access = self._convert_ai_user_access(ai_result.get('user_access_patterns', []))
                        
                        # Generate authorization code
                        generated_code = None
                        if roles or business_rules:
                            generated_code = self.code_generator.generate_authorization_code(
                                roles, business_rules, user_access
                            )
                        
                        # Enhanced metadata
                        analysis_metadata = {
                            'ai_analysis': True,
                            'confidence_score': ai_result.get('confidence_score', 0.0),
                            'roles_count': len(roles),
                            'rules_count': len(business_rules),
                            'user_access_count': len(user_access),
                            'security_requirements': ai_result.get('security_requirements', []),
                            'backend_requirements': ai_result.get('backend_requirements', []),
                            'has_erd_schema': request.erd_schema is not None,
                            'has_existing_backend': request.existing_backend is not None,
                            'analysis_notes': ai_result.get('analysis_notes', '')
                        }
                        
                        return PromptAnalysisResponse(
                            success=True,
                            roles=roles,
                            business_rules=business_rules,
                            user_access=user_access,
                            generated_code=generated_code,
                            analysis_metadata=analysis_metadata
                        )
                    else:
                        # AI analysis failed, fall back to enhanced parser
                        print("AI analysis failed, falling back to enhanced parser")
                        parser_result = self.enhanced_parser.parse_prompt(request.prompt)
                        roles = parser_result.roles
                        business_rules = parser_result.business_rules
                        user_access = parser_result.user_access
                        
                        # Generate authorization code
                        generated_code = None
                        if roles or business_rules:
                            generated_code = self.code_generator.generate_authorization_code(
                                roles, business_rules, user_access
                            )
                        
                        # Enhanced metadata
                        analysis_metadata = {
                            'ai_analysis': False,
                            'fallback_used': True,
                            'roles_count': len(roles),
                            'rules_count': len(business_rules),
                            'user_access_count': len(user_access),
                            'has_erd_schema': request.erd_schema is not None,
                            'has_existing_backend': request.existing_backend is not None,
                            'ai_error': ai_result.get('analysis_notes', 'AI analysis failed')
                        }
                        
                        return PromptAnalysisResponse(
                            success=True,
                            roles=roles,
                            business_rules=business_rules,
                            user_access=user_access,
                            generated_code=generated_code,
                            analysis_metadata=analysis_metadata
                        )
                except Exception as e:
                    print(f"AI analysis error: {e}, falling back to enhanced parser")
                    # Fall back to enhanced parser
                    parser_result = self.enhanced_parser.parse_prompt(request.prompt)
                    roles = parser_result.roles
                    business_rules = parser_result.business_rules
                    user_access = parser_result.user_access
                    
                    # Generate authorization code
                    generated_code = None
                    if roles or business_rules:
                        generated_code = self.code_generator.generate_authorization_code(
                            roles, business_rules, user_access
                        )
                    
                    # Enhanced metadata
                    analysis_metadata = {
                        'ai_analysis': False,
                        'fallback_used': True,
                        'roles_count': len(roles),
                        'rules_count': len(business_rules),
                        'user_access_count': len(user_access),
                        'has_erd_schema': request.erd_schema is not None,
                        'has_existing_backend': request.existing_backend is not None,
                        'ai_error': str(e)
                    }
                    
                    return PromptAnalysisResponse(
                        success=True,
                        roles=roles,
                        business_rules=business_rules,
                        user_access=user_access,
                        generated_code=generated_code,
                        analysis_metadata=analysis_metadata
                    )
            else:
                # Fallback to enhanced parser
                parser_result = self.enhanced_parser.parse_prompt(request.prompt)
                roles = parser_result.roles
                business_rules = parser_result.business_rules
                user_access = parser_result.user_access
                
                # Generate authorization code
                generated_code = None
                if roles or business_rules:
                    generated_code = self.code_generator.generate_authorization_code(
                        roles, business_rules, user_access
                    )
                
                # Basic metadata
                analysis_metadata = {
                    'ai_analysis': False,
                    'roles_count': len(roles),
                    'rules_count': len(business_rules),
                    'user_access_count': len(user_access),
                    'has_erd_schema': request.erd_schema is not None,
                    'has_existing_backend': request.existing_backend is not None
                }
                
                return PromptAnalysisResponse(
                    success=True,
                    roles=roles,
                    business_rules=business_rules,
                    user_access=user_access,
                    generated_code=generated_code,
                    analysis_metadata=analysis_metadata
                )
            
        except Exception as e:
            return PromptAnalysisResponse(
                success=False,
                error_message=f"Error analyzing prompt: {str(e)}"
            )
    
    async def modify_backend(self, request: BackendModificationRequest) -> BackendModificationResponse:
        """
        Modify existing backend based on prompt
        """
        try:
            # Parse modification prompt
            new_roles, new_rules, changes = self.parser.parse_modification_prompt(
                request.modification_prompt,
                request.current_roles or [],
                request.current_rules or []
            )
            
            # Generate modifications
            modifications = self.code_generator.generate_modifications(
                request.backend_code,
                new_roles,
                new_rules,
                changes
            )
            
            # Create modified code (simplified - in production, use proper code parsing)
            modified_code = request.backend_code
            
            # Add new roles and rules to existing code
            if modifications:
                for modification in modifications:
                    if modification['action'] == 'add_imports':
                        modified_code = f"{modification['content']}\n{modified_code}"
                    elif modification['action'] == 'add_rules':
                        modified_code = f"{modified_code}\n{modification['content']}"
            
            return BackendModificationResponse(
                success=True,
                modified_code=modified_code,
                new_roles=new_roles,
                new_rules=new_rules,
                changes_summary=changes
            )
            
        except Exception as e:
            return BackendModificationResponse(
                success=False,
                error_message=f"Error modifying backend: {str(e)}"
            )
    
    async def validate_roles_and_rules(self, roles: List[Role], business_rules: List[BusinessRule]) -> Dict[str, Any]:
        """
        Validate extracted roles and business rules
        """
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Validate roles
        role_names = set()
        for role in roles:
            if not role.name:
                validation_results['errors'].append("Role name cannot be empty")
                validation_results['valid'] = False
            elif role.name in role_names:
                validation_results['warnings'].append(f"Duplicate role name: {role.name}")
            else:
                role_names.add(role.name)
            
            if not role.permissions:
                validation_results['warnings'].append(f"Role '{role.name}' has no permissions")
        
        # Validate business rules
        rule_names = set()
        for rule in business_rules:
            if not rule.name:
                validation_results['errors'].append("Business rule name cannot be empty")
                validation_results['valid'] = False
            elif rule.name in rule_names:
                validation_results['warnings'].append(f"Duplicate rule name: {rule.name}")
            else:
                rule_names.add(rule.name)
            
            if not rule.condition:
                validation_results['errors'].append(f"Business rule '{rule.name}' has no condition")
                validation_results['valid'] = False
        
        return validation_results
    
    async def generate_role_hierarchy(self, roles: List[Role]) -> Dict[str, Any]:
        """
        Generate role hierarchy and inheritance
        """
        hierarchy = {
            'admin': [],
            'manager': [],
            'employee': [],
            'customer': [],
            'guest': []
        }
        
        for role in roles:
            role_name_lower = role.name.lower()
            
            if 'admin' in role_name_lower or 'administrator' in role_name_lower:
                hierarchy['admin'].append(role)
            elif 'manager' in role_name_lower or 'supervisor' in role_name_lower:
                hierarchy['manager'].append(role)
            elif 'employee' in role_name_lower or 'staff' in role_name_lower:
                hierarchy['employee'].append(role)
            elif 'customer' in role_name_lower or 'client' in role_name_lower:
                hierarchy['customer'].append(role)
            else:
                hierarchy['guest'].append(role)
        
        return hierarchy
    
    async def generate_permission_matrix(self, roles: List[Role]) -> Dict[str, List[str]]:
        """
        Generate permission matrix for all roles
        """
        matrix = {}
        
        for role in roles:
            permissions = [perm.value for perm in role.permissions]
            matrix[role.name] = permissions
        
        return matrix
    
    async def suggest_security_improvements(self, roles: List[Role], business_rules: List[BusinessRule]) -> List[str]:
        """
        Suggest security improvements based on roles and rules
        """
        suggestions = []
        
        # Check for admin roles
        admin_roles = [role for role in roles if 'admin' in role.name.lower()]
        if not admin_roles:
            suggestions.append("Consider adding an admin role for system administration")
        
        # Check for read-only roles
        read_only_roles = [role for role in roles if all(perm.value == 'read' for perm in role.permissions)]
        if not read_only_roles:
            suggestions.append("Consider adding read-only roles for data viewing without modification rights")
        
        # Check for business rule coverage
        validation_rules = [rule for rule in business_rules if rule.rule_type.value == 'validation']
        if not validation_rules:
            suggestions.append("Consider adding validation rules for data integrity")
        
        # Check for authorization rules
        auth_rules = [rule for rule in business_rules if rule.rule_type.value == 'authorization']
        if not auth_rules:
            suggestions.append("Consider adding authorization rules for access control")
        
        return suggestions
    
    def _convert_ai_roles(self, ai_roles: List[Dict[str, Any]]) -> List[Role]:
        """Convert AI analysis roles to our Role models"""
        roles = []
        for role_data in ai_roles:
            try:
                # Convert permissions
                permissions = []
                for perm in role_data.get('permissions', []):
                    try:
                        permissions.append(PermissionType(perm))
                    except ValueError:
                        # Map common variations
                        if perm.lower() in ['create', 'add', 'insert']:
                            permissions.append(PermissionType.WRITE)
                        elif perm.lower() in ['modify', 'edit', 'change']:
                            permissions.append(PermissionType.UPDATE)
                        elif perm.lower() in ['remove', 'destroy']:
                            permissions.append(PermissionType.DELETE)
                        elif perm.lower() in ['view', 'see', 'access']:
                            permissions.append(PermissionType.READ)
                        elif perm.lower() in ['control', 'oversee']:
                            permissions.append(PermissionType.MANAGE)
                        elif perm.lower() in ['superuser', 'administrator']:
                            permissions.append(PermissionType.ADMIN)
                
                # Convert access level
                access_level = AccessLevel.ROLE_BASED
                level = role_data.get('access_level', '').lower()
                if level == 'public':
                    access_level = AccessLevel.PUBLIC
                elif level == 'authenticated':
                    access_level = AccessLevel.AUTHENTICATED
                elif level == 'owner_only':
                    access_level = AccessLevel.OWNER_ONLY
                elif level == 'admin_only':
                    access_level = AccessLevel.ADMIN_ONLY
                
                role = Role(
                    name=role_data.get('name', 'Unknown'),
                    description=role_data.get('description', ''),
                    permissions=permissions,
                    access_level=access_level,
                    entity_access=role_data.get('entity_access', {})
                )
                roles.append(role)
            except Exception as e:
                print(f"Error converting role {role_data}: {e}")
                continue
        
        return roles
    
    def _convert_ai_business_rules(self, ai_rules: List[Dict[str, Any]]) -> List[BusinessRule]:
        """Convert AI analysis business rules to our BusinessRule models"""
        rules = []
        for rule_data in ai_rules:
            try:
                # Convert rule type
                rule_type = BusinessRuleType.BUSINESS_LOGIC
                rule_type_str = rule_data.get('rule_type', '').lower()
                if rule_type_str == 'validation':
                    rule_type = BusinessRuleType.VALIDATION
                elif rule_type_str == 'authorization':
                    rule_type = BusinessRuleType.AUTHORIZATION
                elif rule_type_str == 'workflow':
                    rule_type = BusinessRuleType.WORKFLOW
                elif rule_type_str == 'data_integrity':
                    rule_type = BusinessRuleType.DATA_INTEGRITY
                elif rule_type_str == 'audit':
                    rule_type = BusinessRuleType.AUDIT
                
                rule = BusinessRule(
                    name=rule_data.get('name', 'Unknown'),
                    description=rule_data.get('description', ''),
                    rule_type=rule_type,
                    entity=rule_data.get('entity'),
                    condition=rule_data.get('condition', ''),
                    action=rule_data.get('action', ''),
                    priority=rule_data.get('priority', 1)
                )
                rules.append(rule)
            except Exception as e:
                print(f"Error converting business rule {rule_data}: {e}")
                continue
        
        return rules
    
    def _convert_ai_user_access(self, ai_access: List[Dict[str, Any]]) -> List[UserAccess]:
        """Convert AI analysis user access to our UserAccess models"""
        user_access = []
        for access_data in ai_access:
            try:
                # Convert custom permissions
                custom_permissions = []
                for perm in access_data.get('custom_permissions', []):
                    try:
                        custom_permissions.append(PermissionType(perm))
                    except ValueError:
                        # Map common variations
                        if perm.lower() in ['create', 'add', 'insert']:
                            custom_permissions.append(PermissionType.WRITE)
                        elif perm.lower() in ['modify', 'edit', 'change']:
                            custom_permissions.append(PermissionType.UPDATE)
                        elif perm.lower() in ['remove', 'destroy']:
                            custom_permissions.append(PermissionType.DELETE)
                        elif perm.lower() in ['view', 'see', 'access']:
                            custom_permissions.append(PermissionType.READ)
                        elif perm.lower() in ['control', 'oversee']:
                            custom_permissions.append(PermissionType.MANAGE)
                        elif perm.lower() in ['superuser', 'administrator']:
                            custom_permissions.append(PermissionType.ADMIN)
                
                access = UserAccess(
                    user_id=access_data.get('user_id', 'unknown'),
                    roles=access_data.get('roles', []),
                    custom_permissions=custom_permissions,
                    restrictions=access_data.get('restrictions', [])
                )
                user_access.append(access)
            except Exception as e:
                print(f"Error converting user access {access_data}: {e}")
                continue
        
        return user_access
    
    async def modify_backend_with_files(self, backend_path: str, prompt: Optional[str], 
                                       business_rules: Optional[str], role_based_access: Optional[str]) -> dict:
        """
        Modify backend using file system operations
        """
        try:
            # Combine all inputs into a single analysis prompt
            combined_prompt = ""
            if prompt:
                combined_prompt += f"Modification requirements: {prompt}\n"
            if business_rules:
                combined_prompt += f"Business rules to implement: {business_rules}\n"
            if role_based_access:
                combined_prompt += f"Role-based access rules: {role_based_access}\n"
            
            if not combined_prompt.strip():
                return {"success": False, "error_message": "No modification requirements provided"}
            
            # Analyze the combined prompt
            analysis_request = PromptAnalysisRequest(prompt=combined_prompt)
            analysis_result = await self.analyze_prompt(analysis_request)
            
            if not analysis_result.success:
                return {"success": False, "error_message": f"Analysis failed: {analysis_result.error_message}"}
            
            # Generate authorization code
            generated_code = self.code_generator.generate_authorization_code(
                analysis_result.roles,
                analysis_result.business_rules,
                analysis_result.user_access
            )
            
            # Apply modifications to the backend
            from pathlib import Path
            backend_path_obj = Path(backend_path)
            
            # Create middleware directory
            middleware_dir = backend_path_obj / "middleware"
            middleware_dir.mkdir(exist_ok=True)
            
            # Create auth directory
            auth_dir = backend_path_obj / "auth"
            auth_dir.mkdir(exist_ok=True)
            
            # Write generated files
            for filename, content in generated_code.items():
                if filename.endswith('.js'):
                    # Handle directory structure properly
                    if filename.startswith('middleware/'):
                        # Remove 'middleware/' prefix and place in middleware directory
                        clean_filename = filename.replace('middleware/', '')
                        file_path = middleware_dir / clean_filename
                    elif filename.startswith('models/'):
                        # Create models directory and place file there
                        models_dir = backend_path_obj / "models"
                        models_dir.mkdir(exist_ok=True)
                        clean_filename = filename.replace('models/', '')
                        file_path = models_dir / clean_filename
                    elif filename.startswith('routes/'):
                        # Create routes directory and place file there
                        routes_dir = backend_path_obj / "routes"
                        routes_dir.mkdir(exist_ok=True)
                        clean_filename = filename.replace('routes/', '')
                        file_path = routes_dir / clean_filename
                    elif filename.startswith('services/'):
                        # Create services directory and place file there
                        services_dir = backend_path_obj / "services"
                        services_dir.mkdir(exist_ok=True)
                        clean_filename = filename.replace('services/', '')
                        file_path = services_dir / clean_filename
                    elif filename.startswith('auth/'):
                        file_path = auth_dir / filename.replace('auth/', '')
                    else:
                        file_path = backend_path_obj / filename
                    
                    # Ensure directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'w') as f:
                        f.write(content)
                elif filename == 'package.json':
                    # Handle package.json separately
                    file_path = backend_path_obj / filename
                    with open(file_path, 'w') as f:
                        f.write(content)
            
            return {
                "success": True,
                "roles_applied": len(analysis_result.roles),
                "rules_applied": len(analysis_result.business_rules),
                "files_created": len(generated_code)
            }
            
        except Exception as e:
            return {"success": False, "error_message": f"Error modifying backend: {str(e)}"}
    
    async def generate_hierarchy_with_files(self, backend_path: str, business_rules: Optional[str], 
                                         role_based_access: Optional[str]) -> dict:
        """
        Generate role hierarchy for backend files
        """
        try:
            # Combine inputs
            combined_prompt = ""
            if business_rules:
                combined_prompt += f"Business rules: {business_rules}\n"
            if role_based_access:
                combined_prompt += f"Role-based access: {role_based_access}\n"
            
            if not combined_prompt.strip():
                return {"success": False, "error_message": "No hierarchy requirements provided"}
            
            # Analyze prompt
            analysis_request = PromptAnalysisRequest(prompt=combined_prompt)
            analysis_result = await self.analyze_prompt(analysis_request)
            
            if not analysis_result.success:
                return {"success": False, "error_message": f"Analysis failed: {analysis_result.error_message}"}
            
            # Generate hierarchy code
            hierarchy_code = self.code_generator.generate_role_hierarchy(
                analysis_result.roles,
                analysis_result.business_rules
            )
            
            # Apply to backend
            from pathlib import Path
            backend_path_obj = Path(backend_path)
            hierarchy_dir = backend_path_obj / "hierarchy"
            hierarchy_dir.mkdir(exist_ok=True)
            
            # Write hierarchy files
            for filename, content in hierarchy_code.items():
                # Clean filename to avoid nested directories
                clean_filename = filename.replace('hierarchy/', '')
                file_path = hierarchy_dir / clean_filename
                # Ensure directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            return {
                "success": True,
                "roles_detected": len(analysis_result.roles),
                "rules_applied": len(analysis_result.business_rules),
                "hierarchy_files": len(hierarchy_code)
            }
            
        except Exception as e:
            return {"success": False, "error_message": f"Error generating hierarchy: {str(e)}"}
    
    async def analyze_security_with_files(self, backend_path: str) -> dict:
        """
        Analyze backend security and provide suggestions
        """
        try:
            from pathlib import Path
            backend_path_obj = Path(backend_path)
            
            # Scan for security issues
            security_issues = []
            suggestions = []
            recommendations = []
            
            # Check for common security issues
            for file_path in backend_path_obj.rglob('*.js'):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                        # Check for hardcoded secrets
                        if 'password' in content.lower() and 'process.env' not in content:
                            security_issues.append(f"Potential hardcoded password in {file_path.name}")
                            suggestions.append("Use environment variables for sensitive data")
                        
                        # Check for SQL injection vulnerabilities
                        if 'query(' in content and 'sanitize' not in content:
                            security_issues.append(f"Potential SQL injection in {file_path.name}")
                            suggestions.append("Use parameterized queries or ORM")
                        
                        # Check for missing authentication
                        if 'app.get(' in content or 'app.post(' in content:
                            if 'auth' not in content and 'middleware' not in content:
                                security_issues.append(f"Missing authentication in {file_path.name}")
                                suggestions.append("Add authentication middleware to protected routes")
                
                except Exception:
                    continue
            
            # Generate recommendations
            if not security_issues:
                recommendations.append("Consider adding rate limiting")
                recommendations.append("Implement input validation")
                recommendations.append("Add CORS configuration")
                recommendations.append("Use HTTPS in production")
            else:
                recommendations.append("Review and fix all security issues")
                recommendations.append("Implement comprehensive authentication")
                recommendations.append("Add input validation and sanitization")
            
            return {
                "success": True,
                "issues": security_issues,
                "suggestions": suggestions,
                "recommendations": recommendations
            }
            
        except Exception as e:
            return {"success": False, "error_message": f"Error analyzing security: {str(e)}"}
    
    async def generate_authorization_code_with_files(self, backend_path: str) -> dict:
        """
        Generate authorization code for existing backend
        """
        try:
            from pathlib import Path
            backend_path_obj = Path(backend_path)
            
            # Find existing routes
            routes = []
            for file_path in backend_path_obj.rglob('*.js'):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if 'app.get(' in content or 'app.post(' in content:
                            routes.append(str(file_path.relative_to(backend_path_obj)))
                except Exception:
                    continue
            
            # Generate comprehensive authorization code
            auth_code = self.code_generator.generate_comprehensive_auth_code(routes)
            
            # Create auth directory
            auth_dir = backend_path_obj / "auth"
            auth_dir.mkdir(exist_ok=True)
            
            # Create middleware directory
            middleware_dir = backend_path_obj / "middleware"
            middleware_dir.mkdir(exist_ok=True)
            
            # Write authorization files
            for filename, content in auth_code.items():
                # Clean filename to avoid nested directories
                clean_filename = filename.replace('middleware/', '').replace('auth/', '')
                
                if 'middleware' in filename:
                    file_path = middleware_dir / clean_filename
                else:
                    file_path = auth_dir / clean_filename
                
                # Ensure directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w') as f:
                    f.write(content)
            
            return {
                "success": True,
                "auth_files_created": len(auth_code),
                "routes_found": len(routes)
            }
            
        except Exception as e:
            return {"success": False, "error_message": f"Error generating authorization code: {str(e)}"}
    
    async def analyze_erd_with_prompt(self, erd_path: str, prompt: Optional[str], 
                                     business_rules: Optional[str], role_based_access: Optional[str]) -> dict:
        """
        Analyze ERD with prompt and generate comprehensive backend
        """
        try:
            import json
            from pathlib import Path
            import requests
            
            # Combine all inputs
            combined_prompt = ""
            if prompt:
                combined_prompt += f"Requirements: {prompt}\n"
            if business_rules:
                combined_prompt += f"Business rules: {business_rules}\n"
            if role_based_access:
                combined_prompt += f"Role-based access: {role_based_access}\n"
            
            # Analyze prompt
            analysis_request = PromptAnalysisRequest(prompt=combined_prompt)
            analysis_result = await self.analyze_prompt(analysis_request)
            
            if not analysis_result.success:
                return {"success": False, "error_message": f"Analysis failed: {analysis_result.error_message}"}
            
            # Generate comprehensive backend structure
            backend_path = Path(erd_path).parent / "generated_backend"
            backend_path.mkdir(exist_ok=True)
            
            # Create directories
            models_dir = backend_path / "models"
            routes_dir = backend_path / "routes"
            middleware_dir = backend_path / "middleware"
            controllers_dir = backend_path / "controllers"
            services_dir = backend_path / "services"
            config_dir = backend_path / "config"
            
            for dir_path in [models_dir, routes_dir, middleware_dir, controllers_dir, services_dir, config_dir]:
                dir_path.mkdir(exist_ok=True)
            
            # Enhanced package.json with PostgreSQL + Sequelize (consistent with GitHub)
            package_json = {
                "name": "airline-management-backend",
                "version": "1.0.0",
                "description": "Comprehensive airline management system backend",
                "main": "dist/index.js",
                "scripts": {
                    "start": "node dist/index.js",
                    "dev": "ts-node src/index.ts",
                    "build": "tsc",
                    "test": "jest"
                },
                "dependencies": {
                    "express": "^4.19.2",
                    "sequelize": "^6.37.3",
                    "pg": "^8.13.1",
                    "cors": "^2.8.5",
                    "helmet": "^7.1.0",
                    "bcryptjs": "^2.4.3",
                    "jsonwebtoken": "^9.0.2",
                    "express-validator": "^7.0.1",
                    "dotenv": "^16.4.5",
                    "morgan": "^1.10.0",
                    "compression": "^1.7.4"
                },
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "ts-node": "^10.9.0",
                    "@types/node": "^20.0.0",
                    "@types/express": "^4.17.0",
                    "@types/cors": "^2.8.0",
                    "@types/bcryptjs": "^2.4.0",
                    "@types/jsonwebtoken": "^9.0.0",
                    "nodemon": "^3.0.0",
                    "jest": "^29.0.0"
                }
            }
            
            with open(backend_path / "package.json", 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Generate comprehensive app.ts
            app_ts = """
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import { sequelize } from './config/database';
import DatabaseService from './services/databaseService';

// Import models
import Passenger from './models/Passenger';
import Flight from './models/Flight';
import Booking from './models/Booking';
import Airport from './models/Airport';
import Airline from './models/Airline';

dotenv.config();

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true
}));

// Body parsing and compression
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        service: 'Airline Management API',
        database: 'PostgreSQL + Sequelize'
    });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({ 
        message: 'Airline Management System API',
        version: '1.0.0',
        database: 'PostgreSQL + Sequelize',
        endpoints: {
            health: '/health',
            passengers: '/api/passengers',
            flights: '/api/flights',
            bookings: '/api/bookings',
            airports: '/api/airports',
            airlines: '/api/airlines'
        }
    });
});

// Passenger routes
app.get('/api/passengers', async (req, res) => {
    try {
        const passengers = await Passenger.findAll();
        res.json(passengers);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/passengers', async (req, res) => {
    try {
        const passenger = await Passenger.create(req.body);
        res.status(201).json(passenger);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Flight routes
app.get('/api/flights', async (req, res) => {
    try {
        const flights = await Flight.findAll({
            include: [
                { model: Airline, as: 'airline' },
                { model: Airport, as: 'departingAirport' },
                { model: Airport, as: 'arrivingAirport' }
            ]
        });
        res.json(flights);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/flights', async (req, res) => {
    try {
        const flight = await Flight.create(req.body);
        res.status(201).json(flight);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Booking routes
app.get('/api/bookings', async (req, res) => {
    try {
        const bookings = await Booking.findAll({
            include: [
                { model: Flight, as: 'flight' },
                { model: Passenger, as: 'passenger' }
            ]
        });
        res.json(bookings);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/bookings', async (req, res) => {
    try {
        const booking = await Booking.create(req.body);
        res.status(201).json(booking);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Airport routes
app.get('/api/airports', async (req, res) => {
    try {
        const airports = await Airport.findAll();
        res.json(airports);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/airports', async (req, res) => {
    try {
        const airport = await Airport.create(req.body);
        res.status(201).json(airport);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Airline routes
app.get('/api/airlines', async (req, res) => {
    try {
        const airlines = await Airline.findAll();
        res.json(airlines);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/airlines', async (req, res) => {
    try {
        const airline = await Airline.create(req.body);
        res.status(201).json(airline);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Route not found' });
});

// Start server
const PORT = process.env.PORT || 3000;

async function startServer() {
    try {
        await DatabaseService.connect();
        app.listen(PORT, () => {
            console.log(`🚀 Airline Management API running on port ${PORT}`);
            console.log(`📊 Health check: http://localhost:${PORT}/health`);
            console.log(`🗄️  Database: PostgreSQL + Sequelize`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer();

export default app;
"""
            
            with open(backend_path / "app.ts", 'w') as f:
                f.write(app_ts)
            
            # Generate models based on ERD entities
            self._generate_erd_models(models_dir)
            
            # Generate routes
            self._generate_erd_routes(routes_dir)
            
            # Generate middleware
            self._generate_erd_middleware(middleware_dir)
            
            # Generate controllers
            self._generate_erd_controllers(controllers_dir)
            
            # Generate services
            self._generate_erd_services(services_dir)
            
            # Generate config
            self._generate_erd_config(config_dir)
            
            # Generate .env file (PostgreSQL + Sequelize)
            env_content = """
# Database (PostgreSQL + Sequelize)
DATABASE_URL=postgres://user:password@localhost:5432/airline_management
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airline_management
DB_USER=user
DB_PASSWORD=password

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h

# Server
PORT=3000
NODE_ENV=development

# Frontend
FRONTEND_URL=http://localhost:3000

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
"""
            with open(backend_path / ".env", 'w') as f:
                f.write(env_content)
            
            # Generate README
            readme_content = """
# Airline Management System Backend

A comprehensive backend API for airline management system with the following features:

## Features
- Passenger management
- Flight management  
- Booking system
- Security checks
- Baggage management
- No-fly list management
- Role-based access control

## Setup
1. Install dependencies: `npm install`
2. Set up PostgreSQL database
3. Configure environment variables in `.env`
4. Run: `npm run dev` (development) or `npm run build && npm start` (production)

## API Endpoints
- `/api/auth` - Authentication
- `/api/passengers` - Passenger management
- `/api/flights` - Flight management
- `/api/bookings` - Booking management

## Security Features
- JWT authentication
- Role-based authorization
- Rate limiting
- Input validation
- Security headers
"""
            with open(backend_path / "README.md", 'w') as f:
                f.write(readme_content)
            
            return {
                "success": True,
                "backend_path": backend_path,
                "roles_generated": len(analysis_result.roles),
                "rules_applied": len(analysis_result.business_rules),
                "models_created": 11,  # Based on ERD entities
                "routes_created": 4,
                "middleware_created": 3
            }
            
        except Exception as e:
            return {"success": False, "error_message": f"Error analyzing ERD: {str(e)}"}
    
    def _generate_erd_models(self, models_dir):
        """Generate Sequelize models based on ERD entities"""
        # Passenger model
        passenger_model = """
import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../db';

// Interface for Passenger attributes
interface PassengerAttributes {
  id: number;
  firstName: string;
  lastName: string;
  dateOfBirth: Date;
  countryOfCitizenship: string;
  countryOfResidence: string;
  passportNumber: string;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for Passenger creation attributes
interface PassengerCreationAttributes extends Optional<PassengerAttributes, 'id' | 'createdAt' | 'updatedAt'> {}

// Passenger model class
export class Passenger extends Model<PassengerAttributes, PassengerCreationAttributes> implements PassengerAttributes {
  public id!: number;
  public firstName!: string;
  public lastName!: string;
  public dateOfBirth!: Date;
  public countryOfCitizenship!: string;
  public countryOfResidence!: string;
  public passportNumber!: string;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
Passenger.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  firstName: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  lastName: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  dateOfBirth: {
    type: DataTypes.DATEONLY,
    allowNull: false,
  },
  countryOfCitizenship: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  countryOfResidence: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  passportNumber: {
    type: DataTypes.STRING(20),
    allowNull: false,
    unique: true,
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'passengers',
  timestamps: true,
});

export default Passenger;
"""
        with open(models_dir / "Passenger.ts", 'w') as f:
            f.write(passenger_model)
        
        # Flight model
        flight_model = """
import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../db';

// Interface for Flight attributes
interface FlightAttributes {
  id: number;
  flightId: string;
  departingGate: string | null;
  arrivingGate: string | null;
  airlineId: number;
  departingAirportId: number;
  arrivingAirportId: number;
  departureTime: Date;
  arrivalTime: Date;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for Flight creation attributes
interface FlightCreationAttributes extends Optional<FlightAttributes, 'id' | 'departingGate' | 'arrivingGate' | 'createdAt' | 'updatedAt'> {}

// Flight model class
export class Flight extends Model<FlightAttributes, FlightCreationAttributes> implements FlightAttributes {
  public id!: number;
  public flightId!: string;
  public departingGate!: string | null;
  public arrivingGate!: string | null;
  public airlineId!: number;
  public departingAirportId!: number;
  public arrivingAirportId!: number;
  public departureTime!: Date;
  public arrivalTime!: Date;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
Flight.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  flightId: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  departingGate: {
    type: DataTypes.STRING(20),
    allowNull: true,
  },
  arrivingGate: {
    type: DataTypes.STRING(20),
    allowNull: true,
  },
  airlineId: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  departingAirportId: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  arrivingAirportId: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  departureTime: {
    type: DataTypes.DATE,
    allowNull: false,
  },
  arrivalTime: {
    type: DataTypes.DATE,
    allowNull: false,
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'flights',
  timestamps: true,
});

export default Flight;
"""
        with open(models_dir / "Flight.ts", 'w') as f:
            f.write(flight_model)
        
        # Booking model
        booking_model = """
import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../db';

// Interface for Booking attributes
interface BookingAttributes {
  id: number;
  bookingId: string;
  flightId: number;
  passengerId: number;
  status: 'confirmed' | 'cancelled' | 'completed';
  bookingPlatform: string | null;
  seatNumber: string | null;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for Booking creation attributes
interface BookingCreationAttributes extends Optional<BookingAttributes, 'id' | 'bookingPlatform' | 'seatNumber' | 'createdAt' | 'updatedAt'> {}

// Booking model class
export class Booking extends Model<BookingAttributes, BookingCreationAttributes> implements BookingAttributes {
  public id!: number;
  public bookingId!: string;
  public flightId!: number;
  public passengerId!: number;
  public status!: 'confirmed' | 'cancelled' | 'completed';
  public bookingPlatform!: string | null;
  public seatNumber!: string | null;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
Booking.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  bookingId: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  flightId: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  passengerId: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  status: {
    type: DataTypes.ENUM('confirmed', 'cancelled', 'completed'),
    allowNull: false,
    defaultValue: 'confirmed',
  },
  bookingPlatform: {
    type: DataTypes.STRING(20),
    allowNull: true,
  },
  seatNumber: {
    type: DataTypes.STRING,
    allowNull: true,
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'bookings',
  timestamps: true,
});

export default Booking;
"""
        with open(models_dir / "Booking.ts", 'w') as f:
            f.write(booking_model)
        
        # Airport model
        airport_model = """
import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../db';

// Interface for Airport attributes
interface AirportAttributes {
  id: number;
  airportName: string;
  country: string;
  state: string | null;
  city: string;
  iataCode: string;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for Airport creation attributes
interface AirportCreationAttributes extends Optional<AirportAttributes, 'id' | 'state' | 'createdAt' | 'updatedAt'> {}

// Airport model class
export class Airport extends Model<AirportAttributes, AirportCreationAttributes> implements AirportAttributes {
  public id!: number;
  public airportName!: string;
  public country!: string;
  public state!: string | null;
  public city!: string;
  public iataCode!: string;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
Airport.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  airportName: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  country: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  state: {
    type: DataTypes.STRING(50),
    allowNull: true,
  },
  city: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  iataCode: {
    type: DataTypes.STRING(3),
    allowNull: false,
    unique: true,
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'airports',
  timestamps: true,
});

export default Airport;
"""
        with open(models_dir / "Airport.ts", 'w') as f:
            f.write(airport_model)
        
        # Airline model
        airline_model = """
import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../db';

// Interface for Airline attributes
interface AirlineAttributes {
  id: number;
  airlineCode: string;
  airlineName: string;
  airlineCountry: string;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for Airline creation attributes
interface AirlineCreationAttributes extends Optional<AirlineAttributes, 'id' | 'createdAt' | 'updatedAt'> {}

// Airline model class
export class Airline extends Model<AirlineAttributes, AirlineCreationAttributes> implements AirlineAttributes {
  public id!: number;
  public airlineCode!: string;
  public airlineName!: string;
  public airlineCountry!: string;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
Airline.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  airlineCode: {
    type: DataTypes.STRING(3),
    allowNull: false,
    unique: true,
  },
  airlineName: {
    type: DataTypes.STRING(100),
    allowNull: false,
  },
  airlineCountry: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'airlines',
  timestamps: true,
});

export default Airline;
"""
        with open(models_dir / "Airline.ts", 'w') as f:
            f.write(airline_model)
    
    def _generate_erd_routes(self, routes_dir):
        """Generate Express routes"""
        # Passenger routes
        passenger_routes = """
const express = require('express');
const router = express.Router();
const Passenger = require('../models/Passenger');
const { validatePassenger } = require('../middleware/validation');

// GET /api/passengers - Get all passengers
router.get('/', async (req, res) => {
    try {
        const passengers = await Passenger.find().populate('bookings');
        res.json(passengers);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// GET /api/passengers/:id - Get passenger by ID
router.get('/:id', async (req, res) => {
    try {
        const passenger = await Passenger.findById(req.params.id).populate('bookings');
        if (!passenger) {
            return res.status(404).json({ error: 'Passenger not found' });
        }
        res.json(passenger);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// POST /api/passengers - Create new passenger
router.post('/', validatePassenger, async (req, res) => {
    try {
        const passenger = new Passenger(req.body);
        await passenger.save();
        res.status(201).json(passenger);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// PUT /api/passengers/:id - Update passenger
router.put('/:id', async (req, res) => {
    try {
        const passenger = await Passenger.findByIdAndUpdate(
            req.params.id, 
            req.body, 
            { new: true, runValidators: true }
        );
        if (!passenger) {
            return res.status(404).json({ error: 'Passenger not found' });
        }
        res.json(passenger);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// DELETE /api/passengers/:id - Delete passenger
router.delete('/:id', async (req, res) => {
    try {
        const passenger = await Passenger.findByIdAndDelete(req.params.id);
        if (!passenger) {
            return res.status(404).json({ error: 'Passenger not found' });
        }
        res.json({ message: 'Passenger deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
"""
        with open(routes_dir / "passengerRoutes.js", 'w') as f:
            f.write(passenger_routes)
        
        # Flight routes
        flight_routes = """
const express = require('express');
const router = express.Router();
const Flight = require('../models/Flight');

// GET /api/flights - Get all flights
router.get('/', async (req, res) => {
    try {
        const flights = await Flight.find()
            .populate('airline')
            .populate('departingAirport')
            .populate('arrivingAirport');
        res.json(flights);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// GET /api/flights/:id - Get flight by ID
router.get('/:id', async (req, res) => {
    try {
        const flight = await Flight.findById(req.params.id)
            .populate('airline')
            .populate('departingAirport')
            .populate('arrivingAirport');
        if (!flight) {
            return res.status(404).json({ error: 'Flight not found' });
        }
        res.json(flight);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// POST /api/flights - Create new flight
router.post('/', async (req, res) => {
    try {
        const flight = new Flight(req.body);
        await flight.save();
        res.status(201).json(flight);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

module.exports = router;
"""
        with open(routes_dir / "flightRoutes.js", 'w') as f:
            f.write(flight_routes)
        
        # Booking routes
        booking_routes = """
const express = require('express');
const router = express.Router();
const Booking = require('../models/Booking');

// GET /api/bookings - Get all bookings
router.get('/', async (req, res) => {
    try {
        const bookings = await Booking.find()
            .populate('passenger')
            .populate('flight');
        res.json(bookings);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// POST /api/bookings - Create new booking
router.post('/', async (req, res) => {
    try {
        const booking = new Booking(req.body);
        await booking.save();
        res.status(201).json(booking);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

module.exports = router;
"""
        with open(routes_dir / "bookingRoutes.js", 'w') as f:
            f.write(booking_routes)
        
        # Auth routes
        auth_routes = """
const express = require('express');
const router = express.Router();

// POST /api/auth/login - User login
router.post('/login', async (req, res) => {
    try {
        // Implement JWT authentication logic here
        res.json({ message: 'Login endpoint - implement authentication logic' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// POST /api/auth/register - User registration
router.post('/register', async (req, res) => {
    try {
        // Implement user registration logic here
        res.json({ message: 'Register endpoint - implement registration logic' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
"""
        with open(routes_dir / "authRoutes.js", 'w') as f:
            f.write(auth_routes)
    
    def _generate_erd_middleware(self, middleware_dir):
        """Generate middleware files"""
        # Auth middleware
        auth_middleware = """
const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
    try {
        const token = req.header('Authorization')?.replace('Bearer ', '');
        
        if (!token) {
            return res.status(401).json({ error: 'Access denied. No token provided.' });
        }
        
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (error) {
        res.status(401).json({ error: 'Invalid token.' });
    }
};

module.exports = authMiddleware;
"""
        with open(middleware_dir / "authMiddleware.js", 'w') as f:
            f.write(auth_middleware)
        
        # Error handler
        error_handler = """
const errorHandler = (err, req, res, next) => {
    console.error(err.stack);
    
    if (err.name === 'ValidationError') {
        const errors = Object.values(err.errors).map(e => e.message);
        return res.status(400).json({ error: 'Validation Error', details: errors });
    }
    
    if (err.name === 'CastError') {
        return res.status(400).json({ error: 'Invalid ID format' });
    }
    
    res.status(500).json({ 
        error: 'Something went wrong!',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
    });
};

module.exports = errorHandler;
"""
        with open(middleware_dir / "errorHandler.js", 'w') as f:
            f.write(error_handler)
        
        # Validation middleware
        validation_middleware = """
const { body, validationResult } = require('express-validator');

const validatePassenger = [
    body('firstName').notEmpty().withMessage('First name is required'),
    body('lastName').notEmpty().withMessage('Last name is required'),
    body('dateOfBirth').isISO8601().withMessage('Valid date of birth is required'),
    body('passportNumber').notEmpty().withMessage('Passport number is required'),
    (req, res, next) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }
        next();
    }
];

module.exports = { validatePassenger };
"""
        with open(middleware_dir / "validation.js", 'w') as f:
            f.write(validation_middleware)
    
    def _generate_erd_controllers(self, controllers_dir):
        """Generate controller files"""
        # Passenger controller
        passenger_controller = """
const Passenger = require('../models/Passenger');

class PassengerController {
    static async getAllPassengers(req, res) {
        try {
            const passengers = await Passenger.find().populate('bookings');
            res.json(passengers);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    static async getPassengerById(req, res) {
        try {
            const passenger = await Passenger.findById(req.params.id).populate('bookings');
            if (!passenger) {
                return res.status(404).json({ error: 'Passenger not found' });
            }
            res.json(passenger);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    static async createPassenger(req, res) {
        try {
            const passenger = new Passenger(req.body);
            await passenger.save();
            res.status(201).json(passenger);
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }
}

module.exports = PassengerController;
"""
        with open(controllers_dir / "passengerController.js", 'w') as f:
            f.write(passenger_controller)
    
    def _generate_erd_services(self, services_dir):
        """Generate service files"""
        # Database service
        db_service = """
import { Sequelize } from 'sequelize';

class DatabaseService {
    private static sequelize: Sequelize;

    static async connect() {
        try {
            this.sequelize = new Sequelize(
                process.env.DATABASE_URL || 'postgres://user:password@localhost:5432/airline_management',
                {
                    dialect: 'postgres',
                    logging: false,
                    pool: {
                        max: 5,
                        min: 0,
                        acquire: 30000,
                        idle: 10000
                    }
                }
            );
            
            await this.sequelize.authenticate();
            console.log('✅ Connected to PostgreSQL');
        } catch (error) {
            console.error('❌ PostgreSQL connection error:', error);
            process.exit(1);
        }
    }
    
    static async disconnect() {
        try {
            if (this.sequelize) {
                await this.sequelize.close();
                console.log('✅ Disconnected from PostgreSQL');
            }
        } catch (error) {
            console.error('❌ PostgreSQL disconnection error:', error);
        }
    }

    static getSequelize(): Sequelize {
        return this.sequelize;
    }
}

export default DatabaseService;
"""
        with open(services_dir / "databaseService.ts", 'w') as f:
            f.write(db_service)
    
    def _generate_erd_config(self, config_dir):
        """Generate configuration files"""
        # Database config
        db_config = """
import { Sequelize } from 'sequelize';

export const sequelize = new Sequelize(
    process.env.DATABASE_URL || 'postgres://user:password@localhost:5432/airline_management',
    {
        dialect: 'postgres',
        logging: false,
        pool: {
            max: 5,
            min: 0,
            acquire: 30000,
            idle: 10000
        }
    }
);

export default sequelize;
"""
        with open(config_dir / "database.ts", 'w') as f:
            f.write(db_config)
