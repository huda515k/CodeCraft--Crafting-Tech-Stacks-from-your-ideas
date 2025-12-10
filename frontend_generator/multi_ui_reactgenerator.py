"""
Enhanced AI-Powered Multi-Screen React Code Generator
Analyzes multiple UI screens and generates complete connected React application
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import re
import asyncio
import zipfile
import base64
from io import BytesIO

# Add backend directory to path to import wrapper
sys.path.insert(0, str(Path(__file__).parent.parent / "backend_generator"))
from utils.gemini_wrapper import GeminiWrapper
from .models import UIAnalysis, UIComponent


class EnhancedMultiScreenGenerator:
    """
    Enhanced multi-screen React code generator that:
    1. Analyzes multiple UI screen images
    2. Detects navigation elements and connections between screens
    3. Generates a complete, routed React application
    """
    
    def __init__(self, api_key: str, use_cli: Optional[bool] = None):
        """
        Initialize the enhanced multi-screen generator
        
        Args:
            api_key: Gemini API key
            use_cli: Force use CLI (True) or API (False). If None, auto-detect
        """
        self.api_key = api_key
        model_name = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
        self.gemini = GeminiWrapper(api_key=api_key, use_cli=use_cli, model=model_name)
    
    async def analyze_screen_image(
        self,
        image_path: str,
        screen_name: str,
        screen_index: int
    ) -> Dict[str, Any]:
        """
        Analyze a single screen image to extract UI structure
        
        Args:
            image_path: Path to the screen image
            screen_name: Name of the screen
            screen_index: Index of the screen
            
        Returns:
            Dictionary containing screen analysis
        """
        prompt = f"""Analyze this UI design image for screen "{screen_name}" (Screen #{screen_index + 1}).

Extract the following information in JSON format:

{{
  "screen_name": "{screen_name}",
  "screen_type": "login|home|dashboard|profile|settings|list|detail|form|other",
  "layout": {{
    "type": "flex|grid|absolute",
    "direction": "row|column",
    "width": "pixel value or percentage",
    "height": "pixel value or percentage",
    "background_color": "hex color"
  }},
  "navigation_elements": [
    {{
      "type": "button|link|tab|menu_item|back_button|hamburger",
      "text": "button text",
      "position": {{"x": 0, "y": 0, "width": 0, "height": 0}},
      "target_screen": "name or description of where this navigates to",
      "action": "navigate|back|open_menu|close"
    }}
  ],
  "components": [
    {{
      "id": "unique_id",
      "name": "ComponentName",
      "type": "header|button|input|text|image|card|list|navbar|footer|container",
      "position": {{"x": 0, "y": 0, "width": 0, "height": 0}},
      "style": {{
        "background_color": "hex or transparent",
        "text_color": "hex",
        "font_size": "px value",
        "font_weight": "normal|bold|number",
        "border": "description",
        "border_radius": "px value",
        "padding": "px value",
        "margin": "px value"
      }},
      "text_content": "text if any",
      "properties": [
        {{"name": "prop_name", "value": "prop_value"}}
      ],
      "children": ["child_component_ids"],
      "parent_id": "parent_id or null"
    }}
  ],
  "color_palette": {{
    "primary": "hex color",
    "secondary": "hex color",
    "background": "hex color",
    "text": "hex color",
    "accent": "hex color"
  }},
  "typography": {{
    "heading_font": "font name",
    "heading_size": "px value",
    "body_font": "font name",
    "body_size": "px value"
  }},
  "spacing": {{
    "padding": "default padding value",
    "margin": "default margin value"
  }}
}}

IMPORTANT:
1. Measure positions and sizes as accurately as possible
2. Identify ALL navigation elements (buttons, links, tabs that might navigate)
3. For navigation elements, try to infer where they navigate to based on text/icons
4. Extract exact colors from the design
5. Identify component hierarchy (parent-child relationships)
6. Be precise with measurements - the generated code must match pixel-perfectly"""

        try:
            # Handle file path - read file and convert to base64 if it's a path
            if isinstance(image_path, str) and os.path.exists(image_path):
                # It's a file path, read it and convert to base64
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')
            elif isinstance(image_path, str):
                # Assume it's already base64
                image_data = image_path
            else:
                # It's bytes, convert to base64
                image_data = base64.b64encode(image_path).decode('utf-8')
            
            # For image analysis, we need to use the API (not CLI)
            response = await self.gemini.generate_with_image(prompt, image_data)
            
            # Parse JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                raise ValueError("Could not extract JSON from AI response")
                
        except Exception as e:
            print(f"❌ Error analyzing screen {screen_name}: {str(e)}")
            # Return minimal fallback analysis
            return {
                "screen_name": screen_name,
                "screen_type": "other",
                "layout": {
                    "type": "flex",
                    "direction": "column",
                    "width": "100%",
                    "height": "100vh",
                    "background_color": "#ffffff"
                },
                "navigation_elements": [],
                "components": [],
                "color_palette": {
                    "primary": "#007bff",
                    "secondary": "#6c757d",
                    "background": "#ffffff",
                    "text": "#212529",
                    "accent": "#28a745"
                },
                "typography": {
                    "heading_font": "Arial",
                    "heading_size": "24px",
                    "body_font": "Arial",
                    "body_size": "16px"
                },
                "spacing": {
                    "padding": "16px",
                    "margin": "8px"
                }
            }
    
    async def analyze_multiple_screens(
        self,
        screen_images: List[Dict[str, str]]  # [{"path": "path/to/image", "name": "ScreenName"}]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple screen images in parallel
        
        Args:
            screen_images: List of dicts with 'path' and 'name' keys
            
        Returns:
            List of screen analyses
        """
        print(f"🔍 Analyzing {len(screen_images)} screens...")
        
        # Analyze all screens in parallel
        tasks = [
            self.analyze_screen_image(
                screen['path'],
                screen['name'],
                idx
            )
            for idx, screen in enumerate(screen_images)
        ]
        
        analyses = await asyncio.gather(*tasks)
        
        print(f"✅ Analyzed {len(analyses)} screens successfully")
        return analyses
    
    def detect_navigation_flow(
        self,
        screen_analyses: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Detect navigation flow between screens based on navigation elements
        
        Args:
            screen_analyses: List of screen analyses
            
        Returns:
            Dictionary mapping screen names to list of target screens
        """
        navigation_map = {}
        # Extract screen names, handling None values
        screen_names = [s.get('screen_name') or f"Screen{i+1}" for i, s in enumerate(screen_analyses)]
        
        for analysis in screen_analyses:
            source_screen = analysis.get('screen_name') or 'Unknown'
            targets = []
            
            for nav_element in analysis.get('navigation_elements', []):
                # Handle case where target_screen might be None
                target_screen = nav_element.get('target_screen')
                if target_screen is None:
                    target = ''
                elif isinstance(target_screen, str):
                    target = target_screen.lower()
                else:
                    target = str(target_screen).lower()
                
                # Try to match target with actual screen names
                for screen_name in screen_names:
                    # Ensure screen_name is a string before calling .lower()
                    screen_name_str = str(screen_name) if screen_name else ''
                    screen_name_lower = screen_name_str.lower()
                    if screen_name_lower in target or target in screen_name_lower:
                        if screen_name not in targets:
                            targets.append(screen_name)
                        break
            
            navigation_map[source_screen] = targets
        
        print(f"📊 Navigation flow detected:")
        for source, targets in navigation_map.items():
            print(f"   {source} -> {targets if targets else 'No navigation'}")
        
        return navigation_map
    
    async def generate_complete_app(
        self,
        screen_images: List[Dict[str, str]],
        project_name: str = "multi-screen-app",
        include_typescript: bool = True,
        styling_approach: str = "css-modules",
        output_format: str = "zip"  # "zip", "dict", or "files"
    ) -> Dict[str, str] | bytes:
        """
        Main method: Analyze screens and generate complete React app
        
        Args:
            screen_images: List of dicts with 'path' and 'name' keys
            project_name: Name of the project
            include_typescript: Whether to use TypeScript
            styling_approach: CSS approach (css-modules or tailwind)
            output_format: "zip" returns bytes, "dict" returns file dict, "files" writes to disk
            
        Returns:
            Zip file bytes if output_format="zip", or dictionary of file paths to contents
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting Multi-Screen App Generation")
        print(f"{'='*60}\n")
        
        # Step 1: Analyze all screens
        screen_analyses = await self.analyze_multiple_screens(screen_images)
        
        # Step 2: Detect navigation flow
        navigation_map = self.detect_navigation_flow(screen_analyses)
        
        # Step 3: Prepare data for code generation
        screens_data = []
        for idx, (analysis, screen_info) in enumerate(zip(screen_analyses, screen_images)):
            # Generate route from screen name
            screen_name = screen_info.get('name') or f"Screen{idx+1}"
            # Ensure screen_name is a string before calling .lower()
            if not isinstance(screen_name, str):
                screen_name = str(screen_name) if screen_name else f"Screen{idx+1}"
            screen_route = f"/{screen_name.lower().replace(' ', '-')}" if idx > 0 else "/"
            
            screens_data.append({
                'screen_name': screen_name,
                'screen_route': screen_route,
                'analysis': analysis,
                'navigation_targets': navigation_map.get(analysis['screen_name'], [])
            })
        
        # Step 4: Generate code
        files = await self._generate_code_from_analyses(
            screens_data,
            project_name,
            include_typescript,
            styling_approach
        )
        
        print(f"\n{'='*60}")
        print(f"✅ Multi-Screen App Generated Successfully!")
        print(f"   Total files: {len(files)}")
        print(f"   Screens: {len(screens_data)}")
        print(f"{'='*60}\n")
        
        # Step 5: Format output based on output_format
        if output_format == "zip":
            return self._create_zip(files, project_name)
        elif output_format == "files":
            self._write_files_to_disk(files, project_name)
            return files
        else:  # "dict"
            return files


    def _create_zip(self, files: Dict[str, str], project_name: str) -> bytes:
        """
        Create a zip file from the generated files
        
        Args:
            files: Dictionary of file paths to contents
            project_name: Name of the project (used as root folder in zip)
            
        Returns:
            Zip file as bytes
        """
        print(f"📦 Creating zip file for {project_name}...")
        
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, content in files.items():
                # Add project name as root folder in zip
                full_path = f"{project_name}/{file_path}"
                
                # Write file to zip
                zip_file.writestr(full_path, content)
                print(f"   ✓ Added: {full_path}")
        
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read()
        
        print(f"✅ Zip file created: {len(zip_bytes)} bytes ({len(files)} files)")
        
        return zip_bytes
    
    def _write_files_to_disk(self, files: Dict[str, str], output_dir: str) -> None:
        """
        Write generated files to disk
        
        Args:
            files: Dictionary of file paths to contents
            output_dir: Directory to write files to
        """
        print(f"💾 Writing files to disk: {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file_path, content in files.items():
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            print(f"   ✓ Written: {full_path}")
        
        print(f"✅ All files written to {output_dir}")
    
    def save_zip_to_file(self, zip_bytes: bytes, filename: str) -> str:
        """
        Save zip bytes to a file
        
        Args:
            zip_bytes: Zip file bytes
            filename: Output filename (e.g., 'my-app.zip')
            
        Returns:
            Path to saved file
        """
        output_path = Path(filename)
        output_path.write_bytes(zip_bytes)
        print(f"💾 Zip file saved to: {output_path.absolute()}")
        return str(output_path.absolute())
    
    async def _generate_code_from_analyses(
        self,
        screens_data: List[Dict[str, Any]],
        project_name: str,
        include_typescript: bool,
        styling_approach: str
    ) -> Dict[str, str]:
        """Generate React code from screen analyses"""
        
        # Build comprehensive prompt
        prompt = self._build_generation_prompt(
            screens_data,
            project_name,
            include_typescript,
            styling_approach
        )
        
        print(f"📝 Generated prompt length: {len(prompt)} characters")
        print(f"🤖 Calling Gemini to generate React code...")
        
        # Generate code
        response = await self.gemini.generate_text(prompt)
        
        print(f"✅ Received response from Gemini ({len(response)} characters)")
        
        # Parse response
        files = self._parse_code_response(response, include_typescript, len(screens_data))
        
        if not files:
            print("⚠️ Parsing failed, generating fallback files...")
            files = self._generate_fallback_files(
                screens_data,
                project_name,
                include_typescript,
                styling_approach
            )
        
        # Ensure essential files exist (package.json, vite.config, index.html, etc.)
        files = self._ensure_essential_files(files, project_name, include_typescript, styling_approach, len(screens_data))
        
        # Post-process: Remove any image imports from generated code
        files = self._remove_image_imports(files)
        
        return files
    
    def _build_generation_prompt(
        self,
        screens_data: List[Dict[str, Any]],
        project_name: str,
        include_typescript: bool,
        styling_approach: str
    ) -> str:
        """Build prompt for code generation"""
        
        # Format screens data for prompt
        screens_json = json.dumps(screens_data, indent=2)
        
        file_ext = "tsx" if include_typescript else "jsx"
        lang = "typescript" if include_typescript else "javascript"
        
        prompt = f"""You are an expert React developer. Generate a complete, production-ready multi-screen React application that EXACTLY matches these UI designs.

UI DESIGNS ANALYSIS:
{screens_json}

PROJECT SPECIFICATIONS:
- Project Name: {project_name}
- Language: {'TypeScript' if include_typescript else 'JavaScript'}
- Styling: {styling_approach}
- Framework: React 18+ with Vite
- Routing: React Router DOM v6

CRITICAL REQUIREMENTS:
1. Each screen component must EXACTLY match its UI design (pixel-perfect)
2. All navigation elements must be functional and route to correct screens
3. Use proper React patterns (functional components, hooks)
4. Implement responsive design where applicable
5. Follow best practices for code organization
6. All imports must be correct
7. Color palette and typography must match designs exactly
8. **CRITICAL: DO NOT import or reference any external image files (PNG, JPG, SVG, etc.)**
   - If you see icons/images in the UI, use:
     * Unicode emoji (🎨, 📱, ⚙️, etc.) for simple icons
     * Inline SVG for icons (create the SVG code directly in the component)
     * CSS background colors/gradients to represent images
     * Placeholder divs with background colors matching the image colors
   - NEVER use: import icon from "/assets/icon.png" or similar
   - NEVER use: <img src="/assets/image.png" /> or similar
   - If an image is required, create a placeholder div with appropriate styling

OUTPUT FORMAT - FOLLOW EXACTLY:

FILE: package.json
```json
{{
  "name": "{project_name}",
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  }},
  "devDependencies": {{
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
    {"," + '"typescript": "^5.2.0", "@types/react": "^18.2.0", "@types/react-dom": "^18.2.0"' if include_typescript else ""}
  }}
}}
```

FILE: vite.config.{file_ext.replace('x', '')}
```{lang}
import {{ defineConfig }} from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({{
  plugins: [react()],
}});
```

FILE: index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.{file_ext}"></script>
  </body>
</html>
```

FILE: src/index.{file_ext}
```{lang}
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

FILE: src/App.{file_ext}
```{lang}
// Import all screen components and set up routing
// MUST include Routes for all screens with proper navigation
```

FILE: src/index.css
```css
/* Global styles */
```

For EACH screen, generate:

FILE: src/screens/{{ScreenName}}.{file_ext}
```{lang}
// Screen component that EXACTLY matches the UI design
// Must implement all navigation elements
// Must render all components from the analysis
```

FILE: src/screens/{{ScreenName}}.module.css
```css
/* Styles that EXACTLY match the UI design */
```

For each unique component, generate:

FILE: src/components/{{ComponentName}}.{file_ext}
```{lang}
// Reusable component implementation
```

FILE: src/components/{{ComponentName}}.module.css
```css
/* Component styles */
```

NAVIGATION IMPLEMENTATION:
- Use react-router-dom's Link or useNavigate for navigation
- Each navigation element must route to the correct screen
- Implement back buttons using navigate(-1)
- Handle any menu/tab navigation

IMAGE/ASSET HANDLING - CRITICAL:
- DO NOT import any image files (PNG, JPG, SVG, etc.)
- DO NOT use <img src="/path/to/image.png" />
- DO NOT use import statements for images
- Instead, for icons: use Unicode emoji or inline SVG
- Instead, for images: use CSS background colors, gradients, or placeholder divs
- Create visual representation using CSS only
- Example for icon: <span>🎨</span> or create inline SVG
- Example for image placeholder: <div style={{backgroundColor: '#color', width: '100px', height: '100px'}}></div>

Now generate the complete application following this format exactly. Remember: NO image imports, use CSS/emoji/SVG only."""

        return prompt
    
    def _parse_code_response(
        self,
        response: str,
        include_typescript: bool,
        screen_count: int
    ) -> Dict[str, str]:
        """Parse AI response to extract files"""
        files = {}
        
        # Primary pattern: FILE: path + code block
        # Try multiple patterns to handle different AI response formats
        patterns = [
            # Standard: FILE: path\n```lang\ncode```
            r'FILE:\s*([^\n]+)\n```(?:typescript|tsx|ts|javascript|jsx|js|css|json|html)?\n(.*?)```',
            # Alternative: FILE: path\n```\ncode```
            r'FILE:\s*([^\n]+)\n```\n(.*?)```',
            # Alternative: ## path\n```lang\ncode```
            r'##\s*([^\n]+)\n```(?:typescript|tsx|ts|javascript|jsx|js|css|json|html)?\n(.*?)```',
            # Alternative: ### path\n```lang\ncode```
            r'###\s*([^\n]+)\n```(?:typescript|tsx|ts|javascript|jsx|js|css|json|html)?\n(.*?)```',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for file_path, code in matches:
                file_path = file_path.strip()
                code = code.strip()
                # Clean up file path (remove markdown formatting if any)
                file_path = file_path.replace('**', '').replace('*', '').strip()
                if file_path and code and file_path not in files:
                    files[file_path] = code
        
        # If still no files, try to find code blocks with file paths in comments
        if not files:
            # Look for file paths in comments before code blocks
            code_block_pattern = r'```(?:typescript|tsx|ts|javascript|jsx|js|css|json|html)?\n(.*?)```'
            code_blocks = re.findall(code_block_pattern, response, re.DOTALL)
            
            # Try to extract file paths from context (lines before code blocks)
            lines = response.split('\n')
            current_file = None
            current_code = []
            in_code_block = False
            
            for i, line in enumerate(lines):
                # Check if this line indicates a file
                if 'FILE:' in line or line.strip().startswith('##') or line.strip().startswith('###'):
                    # Save previous file if exists
                    if current_file and current_code:
                        code_text = '\n'.join(current_code)
                        # Remove code block markers
                        code_text = re.sub(r'^```.*?\n', '', code_text, flags=re.MULTILINE)
                        code_text = re.sub(r'\n```$', '', code_text, flags=re.MULTILINE)
                        if code_text.strip():
                            files[current_file] = code_text.strip()
                    
                    # Extract new file path
                    if 'FILE:' in line:
                        current_file = line.split('FILE:')[-1].strip()
                    elif line.strip().startswith('##'):
                        current_file = line.strip().lstrip('#').strip()
                    elif line.strip().startswith('###'):
                        current_file = line.strip().lstrip('#').strip()
                    current_code = []
                    in_code_block = False
                elif line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    if not in_code_block and current_file:
                        # End of code block, save it
                        code_text = '\n'.join(current_code)
                        if code_text.strip():
                            files[current_file] = code_text.strip()
                        current_file = None
                        current_code = []
                elif in_code_block and current_file:
                    current_code.append(line)
                elif current_file and not in_code_block:
                    # Still collecting code
                    current_code.append(line)
            
            # Save last file if exists
            if current_file and current_code:
                code_text = '\n'.join(current_code)
                code_text = re.sub(r'^```.*?\n', '', code_text, flags=re.MULTILINE)
                code_text = re.sub(r'\n```$', '', code_text, flags=re.MULTILINE)
                if code_text.strip():
                    files[current_file] = code_text.strip()
        
        print(f"📦 Parsed {len(files)} files from response")
        if files:
            print(f"   Files: {', '.join(sorted(files.keys())[:10])}{'...' if len(files) > 10 else ''}")
        
        return files
    
    def _remove_image_imports(self, files: Dict[str, str]) -> Dict[str, str]:
        """Remove image imports from generated code and replace with placeholders"""
        import re
        
        cleaned_files = {}
        
        for file_path, code in files.items():
            # Only process TypeScript/JavaScript/TSX/JSX files
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                cleaned_files[file_path] = code
                continue
            
            cleaned_code = code
            
            # Remove image import statements
            # Pattern: import ... from "...png" or import ... from "...jpg" etc.
            image_import_pattern = r'import\s+[^"\'`]+\s+from\s+["\'`][^"\']*\.(png|jpg|jpeg|gif|svg|webp|ico)["\'`];?\s*\n?'
            cleaned_code = re.sub(image_import_pattern, '', cleaned_code, flags=re.IGNORECASE | re.MULTILINE)
            
            # Remove require() for images
            require_pattern = r'require\(["\'`][^"\']*\.(png|jpg|jpeg|gif|svg|webp|ico)["\'`]\)'
            cleaned_code = re.sub(require_pattern, '""', cleaned_code, flags=re.IGNORECASE)
            
            # Replace <img src="...png"> with placeholder div
            img_tag_pattern = r'<img\s+[^>]*src=["\'`][^"\']*\.(png|jpg|jpeg|gif|svg|webp|ico)["\'`][^>]*/?>'
            def replace_img(match):
                # Extract alt text if present
                alt_match = re.search(r'alt=["\']([^"\']*)["\']', match.group(0))
                alt_text = alt_match.group(1) if alt_match else 'Image'
                return f'<div style={{"backgroundColor": "#e0e0e0", "width": "100%", "height": "100px", "display": "flex", "alignItems": "center", "justifyContent": "center", "color": "#999"}}>{alt_text}</div>'
            cleaned_code = re.sub(img_tag_pattern, replace_img, cleaned_code, flags=re.IGNORECASE)
            
            if cleaned_code != code:
                print(f"   🧹 Cleaned image imports from {file_path}")
            
            cleaned_files[file_path] = cleaned_code
        
        return cleaned_files
    
    def _ensure_essential_files(
        self,
        files: Dict[str, str],
        project_name: str,
        include_typescript: bool,
        styling_approach: str,
        screen_count: int
    ) -> Dict[str, str]:
        """Ensure essential project files exist, generate if missing"""
        file_ext = "tsx" if include_typescript else "jsx"
        config_ext = "ts" if include_typescript else "js"
        
        # Ensure package.json exists or update it with all required dependencies
        package_json_content = None
        if "package.json" not in files:
            print("   ⚠️  package.json not found in parsed files, generating...")
            package_json_content = {
                "name": project_name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "react": "^18.3.1",
                    "react-dom": "^18.3.1",
                    "react-router-dom": "^6.26.0"
                },
                "devDependencies": {
                    "@vitejs/plugin-react": "^4.3.1",
                    "vite": "^5.4.0",
                    **({"typescript": "^5.6.0", "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1"} if include_typescript else {})
                }
            }
        else:
            # Parse existing package.json and ensure required dependencies are present
            try:
                package_json_content = json.loads(files["package.json"])
            except json.JSONDecodeError:
                print("   ⚠️  Existing package.json is invalid, regenerating...")
                package_json_content = {
                    "name": project_name.lower().replace(" ", "-"),
                    "version": "1.0.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview"
                    },
                    "dependencies": {
                        "react": "^18.3.1",
                        "react-dom": "^18.3.1",
                        "react-router-dom": "^6.26.0"
                    },
                    "devDependencies": {
                        "@vitejs/plugin-react": "^4.3.1",
                        "vite": "^5.4.0",
                        **({"typescript": "^5.6.0", "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1"} if include_typescript else {})
                    }
                }
        
        # Ensure required dependencies are present (check generated code for imports)
        required_deps = {
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "react-router-dom": "^6.26.0"  # Always needed for multi-screen apps
        }
        
        # Check all generated files for imports to detect missing dependencies
        for file_path, code in files.items():
            if file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                # Check for lucide-react
                if 'lucide-react' in code or 'from "lucide-react"' in code or "from 'lucide-react'" in code:
                    required_deps["lucide-react"] = "^0.468.0"
                # Check for other common icon libraries
                if 'react-icons' in code or 'from "react-icons"' in code or "from 'react-icons'" in code:
                    required_deps["react-icons"] = "^5.3.0"
                # Check for other common UI libraries
                if '@mui' in code or '@material-ui' in code:
                    required_deps["@mui/material"] = "^6.1.0"
                    required_deps["@emotion/react"] = "^11.13.0"
                    required_deps["@emotion/styled"] = "^11.13.0"
        
        # Merge required dependencies into package.json
        if "dependencies" not in package_json_content:
            package_json_content["dependencies"] = {}
        
        # Add/update required dependencies
        for dep, version in required_deps.items():
            if dep not in package_json_content["dependencies"]:
                print(f"   ➕ Adding missing dependency: {dep}")
                package_json_content["dependencies"][dep] = version
        
        # Ensure devDependencies exist
        if "devDependencies" not in package_json_content:
            package_json_content["devDependencies"] = {}
        
        # Ensure Vite and React plugin are present
        if "@vitejs/plugin-react" not in package_json_content["devDependencies"]:
            package_json_content["devDependencies"]["@vitejs/plugin-react"] = "^4.3.1"
        if "vite" not in package_json_content["devDependencies"]:
            package_json_content["devDependencies"]["vite"] = "^5.4.0"
        
        # Update TypeScript dependencies if needed
        if include_typescript:
            ts_deps = {
                "typescript": "^5.6.0",
                "@types/react": "^18.3.12",
                "@types/react-dom": "^18.3.1"
            }
            for dep, version in ts_deps.items():
                if dep not in package_json_content["devDependencies"]:
                    package_json_content["devDependencies"][dep] = version
        
        files["package.json"] = json.dumps(package_json_content, indent=2)
        
        # Ensure vite.config exists
        vite_config_file = f"vite.config.{config_ext}"
        if vite_config_file not in files:
            print(f"   ⚠️  {vite_config_file} not found in parsed files, generating...")
            files[vite_config_file] = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
"""
        
        # Ensure index.html exists
        if "index.html" not in files:
            print("   ⚠️  index.html not found in parsed files, generating...")
            files["index.html"] = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.{file_ext}"></script>
  </body>
</html>
"""
        
        # Ensure src/index.tsx/jsx exists
        index_file = f"src/index.{file_ext}"
        if index_file not in files:
            print(f"   ⚠️  {index_file} not found in parsed files, generating...")
            files[index_file] = f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        
        # Ensure src/index.css exists
        if "src/index.css" not in files:
            print("   ⚠️  src/index.css not found in parsed files, generating...")
            files["src/index.css"] = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#root {
  width: 100%;
  min-height: 100vh;
}
"""
        
        return files
    
    def _generate_fallback_files(
        self,
        screens_data: List[Dict[str, Any]],
        project_name: str,
        include_typescript: bool,
        styling_approach: str
    ) -> Dict[str, str]:
        """Generate minimal fallback files"""
        
        file_ext = "tsx" if include_typescript else "jsx"
        files = {}
        
        # package.json with all common dependencies (including lucide-react for icons)
        files["package.json"] = json.dumps({
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "react-router-dom": "^6.26.0",
                "lucide-react": "^0.468.0"  # Common icon library used in generated code
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.3.1",
                "vite": "^5.4.0",
                **({"typescript": "^5.6.0", "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1"} if include_typescript else {})
            }
        }, indent=2)
        
        # vite.config
        config_ext = "ts" if include_typescript else "js"
        files[f"vite.config.{config_ext}"] = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
"""
        
        # index.html
        files["index.html"] = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.{file_ext}"></script>
  </body>
</html>
"""
        
        # index file
        files[f"src/index.{file_ext}"] = f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        
        # App with routing
        screen_imports = "\n".join([
            f"import {data['screen_name'].replace(' ', '')} from './screens/{data['screen_name'].replace(' ', '')}';"
            for data in screens_data
        ])
        
        screen_routes = "\n".join([
            f'        <Route path="{data["screen_route"]}" element={{<{data["screen_name"].replace(" ", "")} />}} />'
            for data in screens_data
        ])
        
        files[f"src/App.{file_ext}"] = f"""import React from 'react';
import {{ BrowserRouter, Routes, Route }} from 'react-router-dom';
{screen_imports}

const App{': React.FC' if include_typescript else ''} = () => {{
  return (
    <BrowserRouter>
      <Routes>
{screen_routes}
      </Routes>
    </BrowserRouter>
  );
}};

export default App;
"""
        
        # Global styles
        files["src/index.css"] = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#root {
  width: 100%;
  min-height: 100vh;
}
"""
        
        # Generate screen components
        for screen_data in screens_data:
            screen_name = screen_data['screen_name'].replace(' ', '')
            analysis = screen_data['analysis']
            
            # Screen component
            files[f"src/screens/{screen_name}.{file_ext}"] = f"""import React from 'react';
import styles from './{screen_name}.module.css';

const {screen_name}{': React.FC' if include_typescript else ''} = () => {{
  return (
    <div className={{styles.container}}>
      <h1>{screen_data['screen_name']}</h1>
      <p>This screen will be generated based on the UI design.</p>
    </div>
  );
}};

export default {screen_name};
"""
            
            # Screen styles
            bg_color = analysis.get('color_palette', {}).get('background', '#ffffff')
            text_color = analysis.get('color_palette', {}).get('text', '#000000')
            
            files[f"src/screens/{screen_name}.module.css"] = f""".container {{
  width: 100%;
  min-height: 100vh;
  background-color: {bg_color};
  color: {text_color};
  padding: 20px;
}}
"""
        
        return files


# Example usage function
async def generate_app_from_ui_screens(
    screen_images: List[Dict[str, str]],
    api_key: str,
    project_name: str = "my-app",
    use_typescript: bool = True,
    output_format: str = "zip"
) -> Dict[str, str] | bytes:
    """
    Convenience function to generate app from UI screen images
    
    Args:
        screen_images: List of {"path": "image.png", "name": "ScreenName"}
        api_key: Gemini API key
        project_name: Project name
        use_typescript: Use TypeScript
        output_format: "zip" (returns bytes), "dict" (returns dict), or "files" (writes to disk)
        
    Returns:
        Zip bytes if output_format="zip", otherwise dict of files
    """
    generator = EnhancedMultiScreenGenerator(api_key)
    
    result = await generator.generate_complete_app(
        screen_images=screen_images,
        project_name=project_name,
        include_typescript=use_typescript,
        styling_approach="css-modules",
        output_format=output_format
    )
    
    return result


# CLI usage example
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate React app from UI screen images")
    parser.add_argument("--images", nargs="+", required=True, help="Paths to screen images")
    parser.add_argument("--names", nargs="+", required=True, help="Names for each screen")
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    parser.add_argument("--project", default="my-app", help="Project name")
    parser.add_argument("--output", default="./output", help="Output directory or zip filename")
    parser.add_argument("--typescript", action="store_true", help="Use TypeScript")
    parser.add_argument("--format", choices=["zip", "files", "dict"], default="zip", 
                       help="Output format: zip file, files on disk, or dictionary")
    
    args = parser.parse_args()
    
    if len(args.images) != len(args.names):
        print("Error: Number of images must match number of names")
        sys.exit(1)
    
    # Prepare screen data
    screen_images = [
        {"path": img, "name": name}
        for img, name in zip(args.images, args.names)
    ]
    
    # Generate app
    print(f"Generating {args.project} from {len(screen_images)} screens...")
    
    result = asyncio.run(generate_app_from_ui_screens(
        screen_images=screen_images,
        api_key=args.api_key,
        project_name=args.project,
        use_typescript=args.typescript,
        output_format=args.format
    ))
    
    if args.format == "zip":
        # Save zip to file
        zip_filename = args.output if args.output.endswith('.zip') else f"{args.output}.zip"
        Path(zip_filename).write_bytes(result)
        print(f"\n✅ Zip file saved: {zip_filename}")
        print(f"\nTo extract and run:")
        print(f"  unzip {zip_filename}")
        print(f"  cd {args.project}")
        print(f"  npm install")
        print(f"  npm run dev")
        
    elif args.format == "files":
        print(f"\n✅ Files written to {args.output}")
        print(f"\nTo run the app:")
        print(f"  cd {args.output}")
        print(f"  npm install")
        print(f"  npm run dev")
        
    else:  # dict
        print(f"\n✅ Generated {len(result)} files as dictionary")
        print(f"Files: {list(result.keys())}")
        