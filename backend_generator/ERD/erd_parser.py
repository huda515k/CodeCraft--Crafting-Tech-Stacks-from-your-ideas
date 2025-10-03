# backend_generator/erd/erd_parser.py

import asyncio
import json
import base64
from io import BytesIO
from PIL import Image
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from .utils import ImageProcessor, NameConverter

class ERDParser:
    """AI-powered ERD parsing using Gemini API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Configure SDK with API key (0.8.x doesn't accept api_version in client_options)
        genai.configure(api_key=api_key)
        # Prefer a broadly available default; allow override via GEMINI_MODEL
        model_name = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
        self.model = genai.GenerativeModel(model_name)
        self.image_processor = ImageProcessor()
    
    async def parse_erd_image(
        self, 
        image_data: Optional[str] = None, 
        image_url: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Parse ERD image using Gemini AI
        """
        try:
            if image_data:
                # Validate and enhance image
                if not self.image_processor.validate_image_format(image_data):
                    raise ValueError("Invalid image format")
                
                # Enhance image for better OCR
                enhanced_image = self.image_processor.enhance_image_for_ocr(image_data)
                
                # Create prompt for ERD analysis
                prompt = self._create_erd_analysis_prompt(additional_context)
                
                # Process with Gemini
                response = await self._analyze_with_gemini(enhanced_image, prompt)
                
                return self._parse_gemini_response(response)
                
            elif image_url:
                # Handle URL-based processing
                return await self._process_image_url(image_url, additional_context)
            else:
                raise ValueError("Either image_data or image_url must be provided")
                
        except Exception as e:
            print(f"Error parsing ERD: {str(e)}")
            return None
    
    def _create_erd_analysis_prompt(self, additional_context: Optional[str] = None) -> str:
        """Create a comprehensive prompt for ERD analysis"""
        base_prompt = """
        Analyze this Entity Relationship Diagram (ERD) image and extract the following information in JSON format:

        1. **Entities**: For each entity, identify:
           - Entity name (in PascalCase)
           - All attributes with their data types
           - Primary keys (usually 'id' fields)
           - Foreign keys and their references
           - Data types (string, integer, float, boolean, date, datetime, text, json, uuid)
           - Constraints (nullable, unique, max_length, default values)

        2. **Relationships**: For each relationship, identify:
           - Source entity
           - Target entity  
           - Relationship type (1:1, 1:N, N:1, M:N)
           - Cardinality information

        3. **Additional Information**:
           - Project name (if visible)
           - Any business rules or constraints mentioned
           - Special annotations or notes

        Return the result as a valid JSON object with this structure:
        {
            "project_name": "string or null",
            "entities": [
                {
                    "name": "EntityName",
                    "attributes": [
                        {
                            "name": "attribute_name",
                            "data_type": "string|integer|float|boolean|date|datetime|text|json|uuid",
                            "is_primary_key": true/false,
                            "is_foreign_key": true/false,
                            "is_nullable": true/false,
                            "is_unique": true/false,
                            "max_length": number or null,
                            "default_value": "value or null",
                            "references_table": "table_name or null",
                            "references_column": "column_name or null"
                        }
                    ],
                    "table_name": "table_name or null"
                }
            ],
            "relationships": [
                {
                    "name": "relationship_name or null",
                    "source_entity": "SourceEntity",
                    "target_entity": "TargetEntity",
                    "relationship_type": "1:1|1:N|N:1|M:N",
                    "source_cardinality": "string or null",
                    "target_cardinality": "string or null"
                }
            ],
            "metadata": {
                "analysis_timestamp": "ISO timestamp",
                "confidence_score": 0.0-1.0,
                "notes": "any additional observations"
            }
        }

        Important guidelines:
        - Use snake_case for attribute names
        - Use PascalCase for entity names
        - Infer data types based on attribute names and context
        - Identify primary keys (usually id, entity_id, etc.)
        - Identify foreign keys and their references
        - Be thorough in identifying all entities and relationships
        - If uncertain about data types, default to 'string'
        - Ensure all JSON is valid and properly formatted
        """
        
        if additional_context:
            base_prompt += f"\n\nAdditional context: {additional_context}"
        
        return base_prompt
    
    async def _analyze_with_gemini(self, image_data: str, prompt: str) -> str:
        """Analyze image with Gemini API"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            # Detect MIME type using Pillow
            detected_mime = "image/png"
            try:
                with Image.open(BytesIO(image_bytes)) as img:
                    fmt = (img.format or "PNG").upper()
                    if fmt == "PNG":
                        detected_mime = "image/png"
                    elif fmt in ("JPG", "JPEG"):
                        detected_mime = "image/jpeg"
                    elif fmt == "GIF":
                        detected_mime = "image/gif"
                    elif fmt == "BMP":
                        detected_mime = "image/bmp"
            except Exception:
                # Fallback to PNG if detection fails
                detected_mime = "image/png"
            
            # Create content for Gemini
            content = [
                prompt,
                {
                    "mime_type": detected_mime,
                    "data": image_bytes
                }
            ]
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(content)
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response and extract JSON"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            parsed_data = json.loads(json_str)
            
            # Add timestamp
            from datetime import datetime
            parsed_data.setdefault('metadata', {})['analysis_timestamp'] = datetime.utcnow().isoformat()
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing response: {str(e)}")
    
    async def _process_image_url(self, image_url: str, additional_context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Process image from URL"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        image_data = base64.b64encode(image_bytes).decode('utf-8')
                        return await self.parse_erd_image(image_data, additional_context=additional_context)
                    else:
                        raise ValueError(f"Failed to fetch image: HTTP {response.status}")
                        
        except Exception as e:
            print(f"Error processing image URL: {str(e)}")
            return None

