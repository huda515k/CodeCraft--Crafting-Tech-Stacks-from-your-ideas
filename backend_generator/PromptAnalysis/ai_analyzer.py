# backend_generator/PromptAnalysis/ai_analyzer.py

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import google.generativeai as genai
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

@dataclass
class AnalysisResult:
    """Result of AI-powered prompt analysis"""
    roles: List[Dict[str, Any]]
    business_rules: List[Dict[str, Any]]
    user_access_patterns: List[Dict[str, Any]]
    security_requirements: List[str]
    backend_requirements: List[str]
    confidence_score: float
    analysis_metadata: Dict[str, Any]

class AIPromptAnalyzer:
    """
    AI-powered prompt analyzer using LangGraph and Gemini Flash
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Initialize Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize LangChain with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.gemini_api_key,
            temperature=0.1
        )
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for prompt analysis"""
        
        # Define the state
        @dataclass
        class AnalysisState:
            prompt: str
            erd_schema: Optional[Dict[str, Any]]
            roles: List[Dict[str, Any]]
            business_rules: List[Dict[str, Any]]
            user_access: List[Dict[str, Any]]
            security_requirements: List[str]
            backend_requirements: List[str]
            confidence_score: float
            errors: List[str]
            metadata: Dict[str, Any]
        
        # Define tools
        @tool
        def extract_roles(prompt: str) -> List[Dict[str, Any]]:
            """Extract roles and permissions from prompt"""
            system_prompt = """
            You are an expert in role-based access control (RBAC) analysis. 
            Extract all roles, permissions, and access patterns from the given prompt.
            
            Return a JSON array of roles with this structure:
            [
                {
                    "name": "role_name",
                    "description": "role description",
                    "permissions": ["read", "write", "update", "delete", "admin", "manage"],
                    "access_level": "public|authenticated|role_based|owner_only|admin_only",
                    "entity_access": {
                        "entity_name": ["permission1", "permission2"]
                    }
                }
            ]
            
            Be thorough and extract ALL roles mentioned, even implicit ones.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Analyze this prompt for roles and permissions:\n\n{prompt}")
            ]
            
            response = self.llm.invoke(messages)
            try:
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return []
            except Exception as e:
                print(f"Error parsing roles: {e}")
                return []
        
        @tool
        def extract_business_rules(prompt: str) -> List[Dict[str, Any]]:
            """Extract business rules and constraints from prompt"""
            system_prompt = """
            You are an expert in business rule analysis. 
            Extract all business rules, constraints, and validation logic from the given prompt.
            
            Return a JSON array of business rules with this structure:
            [
                {
                    "name": "rule_name",
                    "description": "rule description",
                    "rule_type": "validation|authorization|workflow|data_integrity|business_logic|audit",
                    "entity": "entity_name (if applicable)",
                    "condition": "rule condition",
                    "action": "action to take",
                    "priority": 1
                }
            ]
            
            Look for patterns like:
            - "must have", "should have", "cannot", "only", "restrict"
            - "validate", "check", "ensure", "require"
            - "if...then", "when...do", "unless"
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Analyze this prompt for business rules:\n\n{prompt}")
            ]
            
            response = self.llm.invoke(messages)
            try:
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return []
            except Exception as e:
                print(f"Error parsing business rules: {e}")
                return []
        
        @tool
        def extract_user_access_patterns(prompt: str) -> List[Dict[str, Any]]:
            """Extract user access patterns and restrictions"""
            system_prompt = """
            You are an expert in user access control analysis.
            Extract user access patterns, restrictions, and special permissions from the prompt.
            
            Return a JSON array of user access patterns:
            [
                {
                    "user_id": "user_identifier",
                    "roles": ["role1", "role2"],
                    "custom_permissions": ["permission1", "permission2"],
                    "restrictions": ["restriction1", "restriction2"],
                    "special_access": "description of special access"
                }
            ]
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Analyze this prompt for user access patterns:\n\n{prompt}")
            ]
            
            response = self.llm.invoke(messages)
            try:
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return []
            except Exception as e:
                print(f"Error parsing user access: {e}")
                return []
        
        @tool
        def analyze_security_requirements(prompt: str) -> List[str]:
            """Analyze security requirements from prompt"""
            system_prompt = """
            You are a cybersecurity expert. Analyze the prompt for security requirements,
            vulnerabilities, and security best practices that should be implemented.
            
            Return a JSON array of security requirements:
            [
                "requirement1",
                "requirement2",
                "requirement3"
            ]
            
            Look for:
            - Authentication requirements
            - Authorization patterns
            - Data protection needs
            - Audit requirements
            - Compliance needs
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Analyze this prompt for security requirements:\n\n{prompt}")
            ]
            
            response = self.llm.invoke(messages)
            try:
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return []
            except Exception as e:
                print(f"Error parsing security requirements: {e}")
                return []
        
        @tool
        def analyze_backend_requirements(prompt: str, erd_schema: Optional[Dict[str, Any]] = None) -> List[str]:
            """Analyze backend implementation requirements"""
            system_prompt = """
            You are a backend architecture expert. Analyze the prompt and ERD schema
            to determine backend implementation requirements.
            
            Return a JSON array of backend requirements:
            [
                "requirement1",
                "requirement2",
                "requirement3"
            ]
            
            Consider:
            - Database schema modifications
            - API endpoint requirements
            - Middleware needs
            - Authentication/authorization implementation
            - Business logic implementation
            """
            
            context = f"Prompt: {prompt}\n\n"
            if erd_schema:
                context += f"ERD Schema: {json.dumps(erd_schema, indent=2)}\n\n"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Analyze backend requirements:\n\n{context}")
            ]
            
            response = self.llm.invoke(messages)
            try:
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return []
            except Exception as e:
                print(f"Error parsing backend requirements: {e}")
                return []
        
        # Define workflow nodes
        def extract_roles_node(state: AnalysisState) -> AnalysisState:
            """Extract roles from prompt"""
            try:
                roles = extract_roles.invoke({"prompt": state.prompt})
                state.roles = roles
                state.metadata["roles_extracted"] = len(roles)
            except Exception as e:
                state.errors.append(f"Error extracting roles: {str(e)}")
            return state
        
        def extract_rules_node(state: AnalysisState) -> AnalysisState:
            """Extract business rules from prompt"""
            try:
                rules = extract_business_rules.invoke({"prompt": state.prompt})
                state.business_rules = rules
                state.metadata["rules_extracted"] = len(rules)
            except Exception as e:
                state.errors.append(f"Error extracting business rules: {str(e)}")
            return state
        
        def extract_access_node(state: AnalysisState) -> AnalysisState:
            """Extract user access patterns"""
            try:
                access_patterns = extract_user_access_patterns.invoke({"prompt": state.prompt})
                state.user_access = access_patterns
                state.metadata["access_patterns_extracted"] = len(access_patterns)
            except Exception as e:
                state.errors.append(f"Error extracting user access: {str(e)}")
            return state
        
        def analyze_security_node(state: AnalysisState) -> AnalysisState:
            """Analyze security requirements"""
            try:
                security_reqs = analyze_security_requirements.invoke({"prompt": state.prompt})
                state.security_requirements = security_reqs
                state.metadata["security_requirements"] = len(security_reqs)
            except Exception as e:
                state.errors.append(f"Error analyzing security: {str(e)}")
            return state
        
        def analyze_backend_node(state: AnalysisState) -> AnalysisState:
            """Analyze backend requirements"""
            try:
                backend_reqs = analyze_backend_requirements.invoke({
                    "prompt": state.prompt,
                    "erd_schema": state.erd_schema
                })
                state.backend_requirements = backend_reqs
                state.metadata["backend_requirements"] = len(backend_reqs)
            except Exception as e:
                state.errors.append(f"Error analyzing backend requirements: {str(e)}")
            return state
        
        def calculate_confidence_node(state: AnalysisState) -> AnalysisState:
            """Calculate confidence score"""
            try:
                # Calculate confidence based on extracted information
                total_items = len(state.roles) + len(state.business_rules) + len(state.user_access)
                error_penalty = len(state.errors) * 0.1
                
                if total_items == 0:
                    state.confidence_score = 0.0
                else:
                    state.confidence_score = max(0.0, min(1.0, (total_items / 10.0) - error_penalty))
                
                state.metadata["confidence_calculation"] = {
                    "total_items": total_items,
                    "errors": len(state.errors),
                    "confidence": state.confidence_score
                }
            except Exception as e:
                state.errors.append(f"Error calculating confidence: {str(e)}")
                state.confidence_score = 0.0
            return state
        
        # Build the workflow
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("extract_roles", extract_roles_node)
        workflow.add_node("extract_rules", extract_rules_node)
        workflow.add_node("extract_access", extract_access_node)
        workflow.add_node("analyze_security", analyze_security_node)
        workflow.add_node("analyze_backend", analyze_backend_node)
        workflow.add_node("calculate_confidence", calculate_confidence_node)
        
        # Add edges
        workflow.add_edge("extract_roles", "extract_rules")
        workflow.add_edge("extract_rules", "extract_access")
        workflow.add_edge("extract_access", "analyze_security")
        workflow.add_edge("analyze_security", "analyze_backend")
        workflow.add_edge("analyze_backend", "calculate_confidence")
        workflow.add_edge("calculate_confidence", END)
        
        # Set entry point
        workflow.set_entry_point("extract_roles")
        
        return workflow.compile()
    
    async def analyze_prompt(self, prompt: str, erd_schema: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Analyze prompt using AI-powered LangGraph workflow
        """
        try:
            # Initialize state
            initial_state = {
                "prompt": prompt,
                "erd_schema": erd_schema,
                "roles": [],
                "business_rules": [],
                "user_access": [],
                "security_requirements": [],
                "backend_requirements": [],
                "confidence_score": 0.0,
                "errors": [],
                "metadata": {}
            }
            
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            
            # Create analysis result
            analysis_result = AnalysisResult(
                roles=result.get("roles", []),
                business_rules=result.get("business_rules", []),
                user_access_patterns=result.get("user_access", []),
                security_requirements=result.get("security_requirements", []),
                backend_requirements=result.get("backend_requirements", []),
                confidence_score=result.get("confidence_score", 0.0),
                analysis_metadata=result.get("metadata", {})
            )
            
            return analysis_result
            
        except Exception as e:
            # Return error result
            return AnalysisResult(
                roles=[],
                business_rules=[],
                user_access_patterns=[],
                security_requirements=[],
                backend_requirements=[],
                confidence_score=0.0,
                analysis_metadata={"error": str(e)}
            )
    
    async def analyze_with_gemini_direct(self, prompt: str, erd_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Direct analysis using Gemini Flash for comprehensive prompt understanding
        """
        try:
            # Prepare context
            context = f"""
            Analyze this user prompt for a Node.js backend system with role-based access control and business rules.
            
            User Prompt: {prompt}
            
            """
            
            if erd_schema:
                context += f"""
            ERD Schema Context:
            {json.dumps(erd_schema, indent=2)}
            """
            
            context += """
            
            Please provide a comprehensive analysis in JSON format with the following structure:
            {
                "roles": [
                    {
                        "name": "role_name",
                        "description": "role description",
                        "permissions": ["read", "write", "update", "delete", "admin", "manage"],
                        "access_level": "public|authenticated|role_based|owner_only|admin_only",
                        "entity_access": {
                            "entity_name": ["permission1", "permission2"]
                        }
                    }
                ],
                "business_rules": [
                    {
                        "name": "rule_name",
                        "description": "rule description",
                        "rule_type": "validation|authorization|workflow|data_integrity|business_logic|audit",
                        "entity": "entity_name",
                        "condition": "rule condition",
                        "action": "action to take",
                        "priority": 1
                    }
                ],
                "user_access_patterns": [
                    {
                        "user_id": "user_identifier",
                        "roles": ["role1", "role2"],
                        "custom_permissions": ["permission1", "permission2"],
                        "restrictions": ["restriction1", "restriction2"]
                    }
                ],
                "security_requirements": [
                    "requirement1",
                    "requirement2"
                ],
                "backend_requirements": [
                    "requirement1",
                    "requirement2"
                ],
                "confidence_score": 0.95,
                "analysis_notes": "Additional analysis notes"
            }
            
            Be thorough and extract ALL roles, rules, and requirements mentioned in the prompt.
            """
            
            # Generate response using Gemini
            response = self.model.generate_content(context)
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                else:
                    # Fallback parsing
                    return self._parse_fallback_response(response.text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return self._parse_fallback_response(response.text)
                
        except Exception as e:
            print(f"Error in direct Gemini analysis: {e}")
            return {
                "roles": [],
                "business_rules": [],
                "user_access_patterns": [],
                "security_requirements": [],
                "backend_requirements": [],
                "confidence_score": 0.0,
                "analysis_notes": f"Error: {str(e)}"
            }
    
    def _parse_fallback_response(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        return {
            "roles": [],
            "business_rules": [],
            "user_access_patterns": [],
            "security_requirements": [],
            "backend_requirements": [],
            "confidence_score": 0.5,
            "analysis_notes": f"Fallback parsing used. Original response: {response_text[:200]}..."
        }
