# frontend_generator/ui_parser.py

import asyncio
import json
import base64
from io import BytesIO
from PIL import Image
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from .models import UIAnalysis

class UIParser:
    """AI-powered UI parsing using Gemini API"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY environment variable.")
        self.api_key = api_key
        try:
            genai.configure(api_key=api_key)
            model_name = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini model: {str(e)}. Please check your API key.")
    
    async def parse_ui_image(
        self, 
        image_data: Optional[str] = None, 
        image_url: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Optional[UIAnalysis]:
        """
        Parse UI image using Gemini AI and return structured analysis
        """
        try:
            if image_data:
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                
                # Create prompt for UI analysis
                prompt = self._create_ui_analysis_prompt(additional_context)
                
                # Process with Gemini
                response = await self._analyze_with_gemini(image_bytes, prompt)
                
                # Parse response
                return self._parse_gemini_response(response)
                
            elif image_url:
                # Handle URL-based processing
                return await self._process_image_url(image_url, additional_context)
            else:
                raise ValueError("Either image_data or image_url must be provided")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = str(e)
            print(f"Error parsing UI: {error_msg}")
            print(f"Traceback: {error_details}")
            # Re-raise with more context
            raise Exception(f"UI parsing failed: {error_msg}") from e
    
    def _create_ui_analysis_prompt(self, additional_context: Optional[str] = None) -> str:
        """Create a comprehensive prompt for UI analysis"""
        base_prompt = """
Analyze this UI design image (can be from Figma, Canva, or a screenshot) and extract the following information in JSON format:

1. **Layout Structure**:
   - Overall layout type (MUST be one of: flex, grid, block, inline, relative, absolute, or fixed - use only these exact values)
   - Width and height of the main container
   - Background colors
   - Padding and spacing patterns

2. **Components**: For each UI component, identify:
   - Component ID (unique identifier)
   - Component name (descriptive name)
   - Component type (button, card, input, header, footer, navbar, sidebar, modal, form, etc.)
   - Position and dimensions (x, y, width, height)
   - Text content (if applicable)
   - Parent component ID (if it's a child)
   - Child component IDs (if it has children)

3. **Styling for Each Component**:
   - Background color (hex, rgb, rgba)
   - Typography (font family, size, weight, line height, text color, alignment)
   - Spacing (margin, padding, gap)
   - Border (width, style, color, radius)
   - Shadow (x, y, blur, spread, color)
   - Layout properties (display, flex-direction, justify-content, align-items, grid properties)
   - Width, height, z-index, opacity

4. **Color Palette**:
   - Primary color
   - Secondary color
   - Accent color
   - Background color
   - Text color
   - Border color
   - Any custom colors used

5. **Typography**:
   - Default font family
   - Font sizes used
   - Font weights used
   - Line heights used

6. **Interactive Elements**:
   - Buttons (primary, secondary, variants)
   - Input fields
   - Links
   - Hover states (if visible)
   - Active states (if visible)

Return the result as a valid JSON object with this structure:
{
    "project_name": "string or null",
    "layout": {
        "type": "flex|grid|block|inline|relative|absolute|fixed",
        "width": "string",
        "height": "string",
        "background_color": {
            "hex": "#ffffff",
            "rgb": "rgb(255, 255, 255)",
            "rgba": "rgba(255, 255, 255, 1)"
        },
        "padding": "string"
    },
    "components": [
        {
            "id": "component-1",
            "name": "Header",
            "type": "header",
            "position": {
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 80
            },
            "style": {
                "background_color": {"hex": "#ffffff"},
                "typography": {
                    "font_family": "Arial",
                    "font_size": "16px",
                    "font_weight": "400",
                    "color": {"hex": "#000000"}
                },
                "spacing": {
                    "padding": "20px",
                    "margin": "0"
                },
                "layout_type": "flex",
                "flex_direction": "row",
                "justify_content": "space-between",
                "align_items": "center"
                // ... other style properties
            },
            "children": ["component-2", "component-3"],
            "parent_id": null,
            "properties": [
                {
                    "name": "title",
                    "type": "string",
                    "required": false
                }
            ],
            "text_content": "Header Text",
            "attributes": {}
        }
        // ... more components
    ],
    "color_palette": {
        "primary": {"hex": "#007bff"},
        "secondary": {"hex": "#6c757d"},
        "accent": {"hex": "#ffc107"},
        "background": {"hex": "#ffffff"},
        "text": {"hex": "#000000"},
        "custom": [
            {"hex": "#ff0000", "name": "red"}
        ]
    },
    "typography": {
        "font_family": "Arial, sans-serif",
        "font_size": "16px",
        "font_weight": "400",
        "line_height": "1.5",
        "color": {"hex": "#000000"}
    },
    "metadata": {
        "total_components": 10,
        "analysis_timestamp": "ISO timestamp",
        "confidence_score": 0.95,
        "notes": "any additional observations"
    }
}

Important guidelines:
- Be extremely precise with pixel measurements
- Extract exact color hex codes
- Identify all components hierarchically
- Capture all styling details accurately
- Use consistent naming conventions (camelCase for component names)
- Identify reusable components vs one-off components
- Note any interactive states (hover, active, disabled)
- If text is visible, extract it exactly
- Identify layout patterns (flexbox, grid, absolute positioning)
- Ensure all JSON is valid and properly formatted
- Be thorough - this will be used to generate pixel-perfect React code

CRITICAL FORMATTING REQUIREMENTS:
- For layout.type, use ONLY one of these exact values: "flex", "grid", "block", "inline", "relative", "absolute", or "fixed". Do NOT use descriptive phrases like "graphic-design/absolute-positioning" - use only the simple layout type.
- For component types, use ONLY: button, input, card, header, footer, navbar, sidebar, modal, dropdown, form, list, list-item, grid, container, text, image, link, icon, logo, heading, divider, badge, avatar, tabs, accordion, carousel, or custom
- For border style, provide as an object: {"width": "1px", "style": "solid", "color": {"hex": "#ffffff"}} NOT as a CSS string
- For width and height, provide as strings with units: "32px" NOT as integers like 32
"""
        
        if additional_context:
            base_prompt += f"\n\nAdditional context: {additional_context}"
        
        return base_prompt
    
    async def _analyze_with_gemini(self, image_bytes: bytes, prompt: str) -> str:
        """Analyze image with Gemini API"""
        try:
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
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.model.generate_content(content)
                )
                
                if not response:
                    raise Exception("Gemini API returned empty response")
                
                response_text = response.text if hasattr(response, 'text') else str(response)
                
                if not response_text:
                    raise Exception("Gemini API returned response with no text content")
                
                print(f"Gemini response received, length: {len(response_text)}")
                return response_text
                
            except Exception as e:
                error_msg = f"Error calling Gemini API: {str(e)}"
                if hasattr(e, 'message'):
                    error_msg += f" - {e.message}"
                print(error_msg)
                raise Exception(error_msg) from e
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _parse_gemini_response(self, response_text: str) -> UIAnalysis:
        """Parse Gemini response and extract UI analysis"""
        try:
            print(f"Raw Gemini response (first 500 chars): {response_text[:500]}")
            
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                print(f"Full response: {response_text}")
                raise ValueError(f"No JSON found in response. Response length: {len(response_text)}")
            
            json_str = response_text[json_start:json_end]
            print(f"Extracted JSON (first 500 chars): {json_str[:500]}")
            
            # Try to parse the JSON
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                print(f"Problematic JSON (first 1000 chars): {json_str[:1000]}")
                # Try to fix common JSON issues
                fixed_json = self._fix_common_json_issues(json_str)
                if fixed_json != json_str:
                    print("Attempting to fix JSON issues...")
                    try:
                        parsed_data = json.loads(fixed_json)
                    except json.JSONDecodeError as e2:
                        raise ValueError(f"Invalid JSON even after fixing: {str(e2)}")
                else:
                    raise ValueError(f"Invalid JSON in response: {str(e)}")
            
            print(f"Parsed data keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
            
            # Convert to UIAnalysis model - handle missing fields gracefully
            try:
                ui_analysis = UIAnalysis(**parsed_data)
            except Exception as e:
                print(f"Error creating UIAnalysis model: {str(e)}")
                print(f"Parsed data structure: {json.dumps(parsed_data, indent=2)[:1000]}")
                raise ValueError(f"Failed to create UIAnalysis from parsed data: {str(e)}")
            
            return ui_analysis
            
        except Exception as e:
            raise ValueError(f"Error parsing response: {str(e)}")
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON issues that AI might generate"""
        import re
        
        # Fix trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix comments (remove single-line comments)
        json_str = re.sub(r'//.*?(\n|$)', r'\1', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str
    
    async def _process_image_url(self, image_url: str, additional_context: Optional[str] = None) -> Optional[UIAnalysis]:
        """Process image from URL"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        image_data = base64.b64encode(image_bytes).decode('utf-8')
                        return await self.parse_ui_image(image_data, additional_context=additional_context)
                    else:
                        raise ValueError(f"Failed to fetch image: HTTP {response.status}")
                        
        except Exception as e:
            print(f"Error processing image URL: {str(e)}")
            return None

