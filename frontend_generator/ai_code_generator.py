"""
AI-Powered React Code Generator using Gemini
Generates structured, UI-matching React code using AI instead of templates
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

# Add backend directory to path to import wrapper
sys.path.insert(0, str(Path(__file__).parent.parent / "backend_generator"))
from utils.gemini_wrapper import GeminiWrapper
from .models import UIAnalysis, UIComponent


class AIReactCodeGenerator:
    """AI-powered React code generator that uses Gemini to generate code from UI analysis"""
    
    def __init__(self, api_key: str, use_cli: Optional[bool] = None):
        """
        Initialize AI code generator
        
        Args:
            api_key: Gemini API key
            use_cli: Force use CLI (True) or API (False). If None, auto-detect
        """
        self.api_key = api_key
        model_name = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
        # Use CLI for text generation (better quotas), API for images
        self.gemini = GeminiWrapper(api_key=api_key, use_cli=use_cli, model=model_name)
    
    async def generate_component_code(
        self, 
        component: UIComponent, 
        ui_analysis: UIAnalysis,
        include_typescript: bool = True
    ) -> str:
        """
        Generate React component code for a single component using AI
        
        Args:
            component: UI component to generate code for
            ui_analysis: Full UI analysis for context
            include_typescript: Whether to generate TypeScript
        
        Returns:
            React component code as string
        """
        # Build prompt for component generation
        prompt = self._build_component_prompt(component, ui_analysis, include_typescript)
        
        # Generate code using Gemini (will use CLI if available for better quotas)
        code = await self.gemini.generate_text(prompt)
        
        # Extract code from markdown code blocks if present
        code = self._extract_code_from_markdown(code)
        
        return code
    
    async def generate_project_structure(
        self,
        ui_analysis: UIAnalysis,
        project_name: str = "react-app",
        include_typescript: bool = True,
        styling_approach: str = "css-modules"
    ) -> Dict[str, str]:
        """
        Generate complete React project using AI
        
        Args:
            ui_analysis: UI analysis from image
            project_name: Name of the project
            include_typescript: Whether to use TypeScript
            styling_approach: CSS modules or tailwind
        
        Returns:
            Dictionary of file paths to file contents
        """
        try:
            # Build comprehensive prompt for project generation
            prompt = self._build_project_prompt(ui_analysis, project_name, include_typescript, styling_approach)
            
            print(f"📝 Generated prompt length: {len(prompt)} characters")
            
            # Generate project code using Gemini
            print("🤖 Calling Gemini to generate React code...")
            response = await self.gemini.generate_text(prompt)
            
            print(f"✅ Received response from Gemini, length: {len(response)} characters")
            print(f"   First 500 chars: {response[:500]}...")
            
            # Parse the response to extract files
            try:
                files = self._parse_project_response(response, include_typescript, styling_approach)
                
                print(f"📦 Parsed {len(files)} files from response")
                if files:
                    print(f"   Files: {list(files.keys())[:10]}...")  # Show first 10
                    # Post-process: Remove any image imports from generated code
                    files = self._remove_image_imports(files)
                    return files
                else:
                    raise ValueError("Parsing returned empty files dict")
            except ValueError as parse_error:
                # Re-raise parsing errors - don't silently fall back
                print(f"❌ Parsing error: {str(parse_error)}")
                raise Exception(f"Failed to parse AI-generated code: {str(parse_error)}. The AI response might be malformed. Please try again.")
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Error in generate_project_structure: {str(e)}")
            print(f"Traceback: {error_trace}")
            # Don't silently fall back - raise the error so user knows what went wrong
            raise Exception(f"Failed to generate React project: {str(e)}. Please check the UI image and try again.")
    
    def _build_component_prompt(
        self, 
        component: UIComponent, 
        ui_analysis: UIAnalysis,
        include_typescript: bool
    ) -> str:
        """Build prompt for generating a single component"""
        
        # Serialize component to JSON for context
        component_dict = component.dict() if hasattr(component, 'dict') else {
            'id': component.id,
            'name': component.name,
            'type': str(component.type) if component.type else 'container',
            'position': component.position.dict() if component.position else None,
            'style': component.style.dict() if component.style else None,
            'children': component.children,
            'text_content': component.text_content,
            'properties': [p.dict() if hasattr(p, 'dict') else p for p in component.properties] if component.properties else []
        }
        
        # Get child components for context
        child_components = []
        if component.children:
            for child_id in component.children:
                child = next((c for c in ui_analysis.components if c.id == child_id), None)
                if child:
                    child_components.append({
                        'name': child.name,
                        'type': str(child.type) if child.type else 'container',
                        'text_content': child.text_content
                    })
        
        prompt = f"""Generate a React component that exactly matches this UI component design.

COMPONENT SPECIFICATION:
{json.dumps(component_dict, indent=2)}

CHILD COMPONENTS (if any):
{json.dumps(child_components, indent=2)}

UI CONTEXT:
- Project: {ui_analysis.project_name or 'React App'}
- Layout Type: {ui_analysis.layout.type if ui_analysis.layout and ui_analysis.layout.type else 'flex'}
- Color Palette: {json.dumps(ui_analysis.color_palette.dict() if ui_analysis.color_palette and hasattr(ui_analysis.color_palette, 'dict') else {}, indent=2)}

REQUIREMENTS:
1. Generate a {component.name} component that EXACTLY matches the UI design
2. Use {'TypeScript' if include_typescript else 'JavaScript'} with {'CSS Modules' if True else 'Tailwind CSS'}
3. Preserve EXACT positioning, colors, spacing, and typography from the design
4. Ensure proper component structure with imports and exports
5. Use semantic HTML elements appropriate for the component type
6. Include all child components as nested elements
7. Apply styles exactly as specified in the component style
8. Make sure the component is well-structured and production-ready

OUTPUT FORMAT:
Return ONLY the React component code, no explanations. The code should be:
- Complete and runnable
- Properly formatted
- Include imports and exports
- Use CSS modules with className={{styles.componentName}}
- Match the UI design pixel-perfectly

Generate the component code now:"""
        
        return prompt
    
    def _build_project_prompt(
        self,
        ui_analysis: UIAnalysis,
        project_name: str,
        include_typescript: bool,
        styling_approach: str
    ) -> str:
        """Build prompt for generating complete React project"""
        
        # Serialize UI analysis for context
        ui_dict = {
            'project_name': ui_analysis.project_name or project_name,
            'layout': ui_analysis.layout.dict() if ui_analysis.layout and hasattr(ui_analysis.layout, 'dict') else {},
            'components': [
                {
                    'id': c.id,
                    'name': c.name,
                    'type': str(c.type) if c.type else 'container',
                    'position': c.position.dict() if c.position and hasattr(c.position, 'dict') else {},
                    'style': c.style.dict() if c.style and hasattr(c.style, 'dict') else {},
                    'children': c.children,
                    'parent_id': c.parent_id,
                    'text_content': c.text_content,
                    'properties': [p.dict() if hasattr(p, 'dict') else p for p in c.properties] if c.properties else []
                }
                for c in ui_analysis.components
            ],
            'color_palette': ui_analysis.color_palette.dict() if ui_analysis.color_palette and hasattr(ui_analysis.color_palette, 'dict') else {},
            'typography': ui_analysis.typography.dict() if ui_analysis.typography and hasattr(ui_analysis.typography, 'dict') else {}
        }
        
        prompt = f"""You are a React code generator. Generate a complete, production-ready React project that EXACTLY matches this UI design.

UI DESIGN SPECIFICATION:
{json.dumps(ui_dict, indent=2)}

PROJECT REQUIREMENTS:
1. Project Name: {project_name}
2. Language: {'TypeScript' if include_typescript else 'JavaScript'}
3. Styling: {styling_approach}
4. Framework: React 18+ with Vite
5. All components must match the UI design pixel-perfectly

CRITICAL OUTPUT FORMAT - YOU MUST FOLLOW THIS EXACTLY:
You MUST return code in this exact format. Each file must start with "FILE: " followed by the file path, then a newline, then a code block:

FILE: package.json
```json
{{package.json content}}
```

FILE: vite.config.{'ts' if include_typescript else 'js'}
```{'typescript' if include_typescript else 'javascript'}
{{vite config content}}
```

FILE: index.html
```html
{{index.html content}}
```

FILE: src/index.{'tsx' if include_typescript else 'jsx'}
```{'typescript' if include_typescript else 'javascript'}
{{index file content}}
```

FILE: src/App.{'tsx' if include_typescript else 'jsx'}
```{'typescript' if include_typescript else 'javascript'}
{{App component content - this should render ALL components from the UI analysis}}
```

FILE: src/index.css
```css
{{global styles}}
```

For EACH component in the UI analysis, you MUST generate:

FILE: src/components/{{ComponentName}}.{'tsx' if include_typescript else 'jsx'}
```{'typescript' if include_typescript else 'javascript'}
{{component code that matches the UI exactly}}
```

FILE: src/components/{{ComponentName}}.module.css
```css
{{component styles that match the UI exactly}}
```

IMPORTANT:
- You MUST generate code for ALL components listed in the UI analysis
- The App component MUST import and render all the UI components
- Each component MUST match its position, colors, spacing, and typography from the UI analysis
- DO NOT generate placeholder or fallback code - generate the ACTUAL UI components
- The generated code MUST be complete and runnable
- **CRITICAL: DO NOT import or reference any external image files (PNG, JPG, SVG, etc.)**
  - If you see icons/images in the UI, use:
    * Unicode emoji (🎨, 📱, ⚙️, 🏠, etc.) for simple icons
    * Inline SVG for icons (create the SVG code directly in the component)
    * CSS background colors/gradients to represent images
    * Placeholder divs with background colors matching the image colors
  - NEVER use: import icon from "/assets/icon.png" or import icon from "../assets/icon.png"
  - NEVER use: <img src="/assets/image.png" /> or <img src="../assets/image.png" />
  - NEVER use: require() for images
  - If an image is required, create a placeholder div with appropriate styling and background color

IMAGE/ASSET HANDLING - CRITICAL:
- DO NOT import any image files (PNG, JPG, SVG, etc.)
- DO NOT use <img src="/path/to/image.png" /> or <img src="../path/to/image.png" />
- DO NOT use import statements for images (e.g., import icon from "/assets/icon.png")
- DO NOT use require() for images
- Instead, for icons: use Unicode emoji or inline SVG created directly in the component
- Instead, for images: use CSS background colors, gradients, or placeholder divs
- Create visual representation using CSS only
- Example for icon: <span style={{fontSize: '24px'}}>🎨</span> or create inline SVG
- Example for image placeholder: <div style={{backgroundColor: '#color', width: '100px', height: '100px', borderRadius: '4px'}}></div>

Generate the complete project now. Remember: NO image imports, use CSS/emoji/inline SVG only."""
        
        return prompt
    
    def _extract_code_from_markdown(self, text: str) -> str:
        """Extract code from markdown code blocks"""
        import re
        
        # Try to find code blocks
        code_blocks = re.findall(r'```(?:typescript|tsx|ts|javascript|jsx|js|css|json|html)?\n(.*?)```', text, re.DOTALL)
        if code_blocks:
            # Return the first code block
            return code_blocks[0].strip()
        
        # If no code blocks, return the text as-is (might already be code)
        return text.strip()
    
    def _parse_project_response(
        self, 
        response: str, 
        include_typescript: bool,
        styling_approach: str
    ) -> Dict[str, str]:
        """Parse AI response to extract project files"""
        import re
        
        files = {}
        
        print(f"🔍 Parsing response for files...")
        
        # Pattern to match FILE: path followed by code block
        pattern = r'FILE:\s*([^\n]+)\n```(?:typescript|tsx|ts|javascript|jsx|js|css|json|html)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        print(f"   Found {len(matches)} matches with FILE: pattern")
        
        for file_path, code in matches:
            file_path = file_path.strip()
            code = code.strip()
            if file_path and code:
                files[file_path] = code
        
        # If no files were extracted, try a simpler pattern
        if not files:
            print("   Trying alternative parsing method...")
            # Look for any code blocks and try to infer file paths
            code_blocks = re.findall(r'```(?:typescript|tsx|ts|javascript|jsx|js|css|json|html)?\n(.*?)```', response, re.DOTALL)
            print(f"   Found {len(code_blocks)} code blocks")
            
            if code_blocks:
                # Try to extract file paths from context
                lines = response.split('\n')
                current_file = None
                current_code = []
                
                for line in lines:
                    if 'FILE:' in line:
                        if current_file and current_code:
                            # Extract code from current_code (remove markdown markers)
                            code_text = '\n'.join(current_code)
                            # Remove code block markers if present
                            code_text = re.sub(r'^```.*?\n', '', code_text, flags=re.MULTILINE)
                            code_text = re.sub(r'\n```$', '', code_text, flags=re.MULTILINE)
                            files[current_file] = code_text.strip()
                        current_file = line.split('FILE:')[-1].strip()
                        current_code = []
                    elif current_file:
                        current_code.append(line)
                
                if current_file and current_code:
                    code_text = '\n'.join(current_code)
                    code_text = re.sub(r'^```.*?\n', '', code_text, flags=re.MULTILINE)
                    code_text = re.sub(r'\n```$', '', code_text, flags=re.MULTILINE)
                    files[current_file] = code_text.strip()
        
        print(f"   Parsed {len(files)} files")
        
        # Always ensure we have at least fallback files
        if not files:
            print("   No files parsed, will use fallback")
        
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

    def _generate_fallback_files(
        self, 
        include_typescript: bool, 
        styling_approach: str
    ) -> Dict[str, str]:
        """Generate minimal fallback files if AI response couldn't be parsed"""
        file_ext = "tsx" if include_typescript else "jsx"
        
        return {
            "package.json": json.dumps({
                "name": "react-app",
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
                    "lucide-react": "^0.468.0"  # Common icon library
                },
                "devDependencies": {
                    "@vitejs/plugin-react": "^4.3.1",
                    "vite": "^5.4.0",
                    **({"typescript": "^5.6.0", "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1"} if include_typescript else {})
                }
            }, indent=2),
            f"vite.config.{'ts' if include_typescript else 'js'}": f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({{
  plugins: [react()],
}})
""",
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>React App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.tsx"></script>
  </body>
</html>
""",
            f"src/index.{file_ext}": f"""import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
            "src/App.tsx": """import React from 'react'
import './index.css'

const App: React.FC = () => {
  return (
    <div className="app">
      <h1>React App</h1>
    </div>
  )
}

export default App
""",
            "src/index.css": """* {
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
        }

