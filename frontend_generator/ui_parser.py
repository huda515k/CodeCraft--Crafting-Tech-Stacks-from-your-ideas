# frontend_generator/ui_parser.py

import asyncio
import json
import base64
from io import BytesIO
from PIL import Image
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend directory to path to import wrapper
sys.path.insert(0, str(Path(__file__).parent.parent / "backend_generator"))
from utils.gemini_wrapper import GeminiWrapper
from .models import UIAnalysis

class UIParser:
    """AI-powered UI parsing using Gemini API or CLI (auto-detected)"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY environment variable.")
        self.api_key = api_key
        try:
            # Use wrapper (auto-detects CLI or API)
            # Default to flash-latest for API compatibility
            model_name = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
            self.gemini = GeminiWrapper(api_key=api_key, model=model_name)
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini: {str(e)}. Please check your API key.")
    
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
                
                # Optimize image to reduce processing time
                # Resize if too large (max 2048px on longest side for UI analysis)
                try:
                    img = Image.open(BytesIO(image_bytes))
                    original_size = img.size
                    max_dimension = 2048  # Gemini can handle up to 2048px well
                    
                    if max(original_size) > max_dimension:
                        print(f"📐 Resizing image from {original_size} to max {max_dimension}px for faster processing...")
                        # Calculate new size maintaining aspect ratio
                        ratio = max_dimension / max(original_size)
                        new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        # Convert back to bytes
                        output = BytesIO()
                        img_format = img.format or 'PNG'
                        img.save(output, format=img_format, optimize=True)
                        image_bytes = output.getvalue()
                        print(f"✅ Image resized to {img.size}, size reduced to {len(image_bytes)} bytes")
                except Exception as resize_error:
                    print(f"⚠️  Could not resize image: {resize_error}, using original")
                
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

CRITICAL REQUIREMENTS FOR EXACT UI-TO-REACT MAPPING:
- Extract EXACT pixel measurements (x, y, width, height) for EVERY component - these will be used for pixel-perfect positioning
- Extract EXACT color hex codes from the image - use color picker values, not approximations
- Map EVERY visible element - buttons, text, images, icons, containers, all must be identified
- Preserve EXACT positioning - if an element is at x:100, y:200, capture those exact values
- Capture EXACT spacing - padding, margin, gap values must match the design
- Extract EXACT typography - font family, size, weight, line height, color
- Preserve EXACT layout structure - flexbox/grid properties, alignment, direction
- Map ALL colors accurately - background colors, text colors, border colors, shadow colors
- Identify component hierarchy correctly - parent-child relationships must be accurate
- Extract text content exactly as shown in the UI
- This code will generate React components that MUST match the UI design pixel-perfectly

CRITICAL FOR MULTI-SCREEN APPS:
- Each screen should be analyzed as a COMPLETE, STANDALONE page
- The root component should contain ALL visible elements from the screen
- DO NOT create placeholder components - every visible element must be mapped
- Ensure the main container spans the full viewport (width: 100vw or 100%, height: 100vh or auto)
- All elements should be properly nested within the root container
- Text content must match EXACTLY what is visible in the image
- Colors must match EXACTLY - use hex codes from the actual image
- Layout must match EXACTLY - use flexbox/grid as shown in the design
- Spacing must match EXACTLY - padding, margin, gap values from the design

CRITICAL FORMATTING REQUIREMENTS:
- For layout.type, use ONLY one of these exact values: "flex", "grid", "block", "inline", "relative", "absolute", or "fixed". Do NOT use descriptive phrases like "graphic-design/absolute-positioning" - use only the simple layout type.
- For component types, use ONLY: button, input, card, header, footer, navbar, sidebar, modal, dropdown, form, list, list-item, grid, container, text, image, link, icon, logo, heading, divider, badge, avatar, tabs, accordion, carousel, or custom
- For border style, provide as an object: {"width": "1px", "style": "solid", "color": {"hex": "#ffffff"}} NOT as a CSS string
- For width and height, provide as strings with units: "32px" NOT as integers like 32
- For position.x and position.y, provide exact pixel coordinates relative to parent or viewport
- For colors, ALWAYS provide hex code - extract the exact color from the image, not approximations
- Preserve ALL positioning information - if an element is at x: 100, y: 200, include those exact values
"""
        
        if additional_context:
            base_prompt += f"\n\nAdditional context: {additional_context}"
        
        return base_prompt
    
    async def _analyze_with_gemini(self, image_bytes: bytes, prompt: str) -> str:
        """Analyze image with Gemini (CLI or API, auto-detected)"""
            try:
            # Use wrapper - it handles both CLI and API
            response = await self.gemini.generate_with_image(
                prompt=prompt,
                image_data=image_bytes
            )
                
            if not response:
                raise Exception("Gemini returned empty response")
                
            print(f"Gemini response received, length: {len(response)}")
            return response
            
            
        except Exception as e:
            error_msg = f"Error calling Gemini: {str(e)}"
            print(error_msg)
            raise Exception(error_msg) from e
    
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
            
            # Clean and normalize the parsed data before creating UIAnalysis
            parsed_data = self._clean_parsed_data(parsed_data)
            
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
    
    def _clean_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize parsed data to fix common issues"""
        if not isinstance(data, dict):
            return data
        
        # Clean components
        if "components" in data and isinstance(data["components"], list):
            cleaned_components = []
            for component in data["components"]:
                if not isinstance(component, dict):
                    cleaned_components.append(component)
                    continue
                
                # Clean style.position - if it's a string (CSS position property), remove it
                # Position model expects {x, y, width, height}, not CSS position string
                if "style" in component and isinstance(component["style"], dict):
                    style = component["style"]
                    if "position" in style:
                        position_value = style["position"]
                        # If position is a string (like "absolute", "relative", "fixed"), it's CSS position property
                        # Remove it from style.position (it should be in layout_type or display instead)
                        if isinstance(position_value, str) and position_value.lower() in ["absolute", "relative", "fixed", "static", "sticky"]:
                            # This is CSS position property, not Position object - remove it
                            # Optionally, we could set it as a separate CSS property, but for now just remove it
                            del style["position"]
                            print(f"⚠️  Removed CSS position string '{position_value}' from style.position (should be in layout_type)")
                        # If position is not a dict with x/y/width/height, remove it
                        elif isinstance(position_value, dict):
                            # Check if it has the required Position fields
                            if not any(key in position_value for key in ["x", "y", "width", "height"]):
                                # It's not a valid Position object, remove it
                                del style["position"]
                                print(f"⚠️  Removed invalid position object from style.position")
                
                cleaned_components.append(component)
            
            data["components"] = cleaned_components
        
        return data
    
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

