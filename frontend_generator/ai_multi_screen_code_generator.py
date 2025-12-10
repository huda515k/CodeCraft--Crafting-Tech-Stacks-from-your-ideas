"""
AI-Powered Multi-Screen React Code Generator using Gemini
Generates structured, UI-matching React code for multiple screens using AI
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import re

# Add backend directory to path to import wrapper
sys.path.insert(0, str(Path(__file__).parent.parent / "backend_generator"))
from utils.gemini_wrapper import GeminiWrapper
from .models import UIAnalysis, UIComponent


class AIMultiScreenCodeGenerator:
    """AI-powered multi-screen React code generator that uses Gemini to generate code from multiple UI analyses"""
    
    def __init__(self, api_key: str, use_cli: Optional[bool] = None):
        """
        Initialize AI multi-screen code generator
        
        Args:
            api_key: Gemini API key
            use_cli: Force use CLI (True) or API (False). If None, auto-detect
        """
        self.api_key = api_key
        model_name = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
        # Use CLI for text generation (better quotas), API for images
        self.gemini = GeminiWrapper(api_key=api_key, use_cli=use_cli, model=model_name)
    
    async def generate_multi_screen_project(
        self,
        screen_analyses: List[Dict[str, Any]],  # List of {ui_analysis, screen_name, screen_route}
        project_name: str = "multi-screen-app",
        include_typescript: bool = True,
        styling_approach: str = "css-modules"
    ) -> Dict[str, str]:
        """
        Generate complete multi-screen React project using AI
        
        Args:
            screen_analyses: List of dicts with 'ui_analysis', 'screen_name', 'screen_route'
            project_name: Name of the project
            include_typescript: Whether to use TypeScript
            styling_approach: CSS modules or tailwind
        
        Returns:
            Dictionary of file paths to file contents
        """
        try:
            # Build comprehensive prompt for multi-screen project generation
            prompt = self._build_multi_screen_project_prompt(
                screen_analyses, 
                project_name, 
                include_typescript, 
                styling_approach
            )
            
            print(f"📝 Generated multi-screen prompt length: {len(prompt)} characters")
            
            # Generate project code using Gemini
            print("🤖 Calling Gemini to generate multi-screen React code...")
            response = await self.gemini.generate_text(prompt)
            
            print(f"✅ Received response from Gemini, length: {len(response)} characters")
            print(f"   First 500 chars: {response[:500]}...")
            
            # Parse the response to extract files
            try:
                files = self._parse_project_response(response, include_typescript, styling_approach)
                
                print(f"📦 Parsed {len(files)} files from response")
                if files:
                    print(f"   Files: {list(files.keys())[:10]}...")  # Show first 10
                    return files
                else:
                    raise ValueError("Parsing returned empty files dict")
            except ValueError as parse_error:
                print(f"❌ Parsing error: {str(parse_error)}")
                raise Exception(f"Failed to parse AI-generated code: {str(parse_error)}. The AI response might be malformed. Please try again.")
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Error in generate_multi_screen_project: {str(e)}")
            print(f"Traceback: {error_trace}")
            raise Exception(f"Failed to generate multi-screen React project: {str(e)}. Please check the UI images and try again.")
    
    def _build_multi_screen_project_prompt(
        self,
        screen_analyses: List[Dict[str, Any]],
        project_name: str,
        include_typescript: bool,
        styling_approach: str
    ) -> str:
        """Build prompt for generating complete multi-screen React project"""
        
        # Serialize all screen analyses
        screens_data = []
        for screen_data in screen_analyses:
            ui_analysis = screen_data['ui_analysis']
            screen_name = screen_data['screen_name']
            screen_route = screen_data['screen_route']
            
            ui_dict = {
                'screen_name': screen_name,
                'screen_route': screen_route,
                'project_name': ui_analysis.project_name if hasattr(ui_analysis, 'project_name') else screen_name,
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
            screens_data.append(ui_dict)
        
        prompt = f"""You are a React code generator. Generate a complete, production-ready multi-screen React project that EXACTLY matches these UI designs.

MULTI-SCREEN UI DESIGN SPECIFICATION:
{json.dumps(screens_data, indent=2)}

PROJECT REQUIREMENTS:
1. Project Name: {project_name}
2. Language: {'TypeScript' if include_typescript else 'JavaScript'}
3. Styling: {styling_approach}
4. Framework: React 18+ with Vite
5. Routing: React Router DOM for navigation between screens
6. All components must match the UI designs pixel-perfectly

CRITICAL OUTPUT FORMAT - YOU MUST FOLLOW THIS EXACTLY:
You MUST return code in this exact format. Each file must start with "FILE: " followed by the file path, then a newline, then a code block:

FILE: package.json
```json
{{package.json content with react-router-dom dependency}}
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
{{App component with React Router - MUST include all screens with their routes}}
```

FILE: src/index.css
```css
{{global styles}}
```

For EACH screen in the screens_data, generate:

FILE: src/screens/{{ScreenName}}.{'tsx' if include_typescript else 'jsx'}
```{'typescript' if include_typescript else 'javascript'}
{{Screen component code that EXACTLY matches the UI design for this screen}}
```

FILE: src/screens/{{ScreenName}}.module.css
```css
{{Screen styles that EXACTLY match the UI design}}
```

For EACH component in each screen's UI analysis, generate:

FILE: src/components/{{ComponentName}}.{'tsx' if include_typescript else 'javascript'}
```{'typescript' if include_typescript else 'javascript'}
{{Component code that matches the UI exactly}}
```

FILE: src/components/{{ComponentName}}.module.css
```css
{{Component styles that match the UI exactly}}
```

CRITICAL REQUIREMENTS:
1. The App.tsx/jsx MUST use React Router with BrowserRouter, Routes, and Route
2. Each screen MUST be accessible via its specified route (screen_route)
3. Each screen component MUST render ALL components from its UI analysis
4. Each component MUST match its position, colors, spacing, and typography from the UI analysis EXACTLY
5. Use CSS modules with proper className bindings
6. Ensure all imports are correct
7. Make the code production-ready and well-structured
8. The generated UI must match the design pixel-perfectly
9. All elements must be properly aligned and not scattered
10. Use proper React patterns (functional components, hooks if needed)
11. Preserve EXACT pixel measurements, colors, and layout from each UI design
12. Each screen should be a complete, standalone component that matches its UI design exactly
13. **CRITICAL: DO NOT import or reference any external image files (PNG, JPG, SVG, etc.)**
    - If you see icons/images in the UI, use:
      * Unicode emoji (🎨, 📱, ⚙️, 🏠, etc.) for simple icons
      * Inline SVG for icons (create the SVG code directly in the component)
      * CSS background colors/gradients to represent images
      * Placeholder divs with background colors matching the image colors
    - NEVER use: import icon from "/assets/icon.png" or import icon from "../assets/icon.png"
    - NEVER use: <img src="/assets/image.png" /> or <img src="../assets/image.png" />
    - NEVER use: require() for images
    - If an image is required, create a placeholder div with appropriate styling and background color

SCREEN ROUTING REQUIREMENTS:
- The App component MUST import all screen components
- Each screen MUST have a Route with its exact screen_route path
- Add a default route "/" that redirects to the first screen
- Use Navigate from react-router-dom for the default redirect

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

Generate the complete multi-screen project now, following the exact format above. Remember: NO image imports, use CSS/emoji/inline SVG only."""

        return prompt
    
    def _parse_project_response(
        self,
        response: str,
        include_typescript: bool,
        styling_approach: str
    ) -> Dict[str, str]:
        """Parse AI response to extract project files"""
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

        # Always ensure we have at least essential files
        if not files:
            print("   No files parsed, will use fallback")
            # Note: screen_count not available here, use default
            files = self._generate_fallback_files(include_typescript, styling_approach, 1)
            print(f"✅ Generated {len(files)} fallback files")

        return files
    
    def _generate_fallback_files(
        self,
        include_typescript: bool,
        styling_approach: str,
        screen_count: int = 1
    ) -> Dict[str, str]:
        """Generate minimal fallback files if AI parsing fails"""
        file_ext = "tsx" if include_typescript else "jsx"
        
        files = {}
        
        # package.json with all common dependencies (including lucide-react for icons)
        files["package.json"] = json.dumps({
            "name": "multi-screen-app",
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
                **({"typescript": "^5.6.0", "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1", "@types/node": "^22.10.0"} if include_typescript else {})
            }
        }, indent=2)
        
        # vite.config
        if include_typescript:
            files["vite.config.ts"] = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
"""
        else:
            files["vite.config.js"] = """import { defineConfig } from 'vite';
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
    <title>Multi-Screen App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.{file_ext}"></script>
  </body>
</html>
"""
        
        # index.tsx/jsx
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
        
        # App.tsx/jsx with React Router
        screen_imports = "\n".join([f"import Screen{i+1} from './screens/Screen{i+1}';" for i in range(screen_count)])
        screen_routes = "\n".join([
            f'        <Route path="{"/" if i == 0 else f"/screen{i+1}"}" element={{<Screen{i+1} />}} />'
            for i in range(screen_count)
        ])
        
        files[f"src/App.{file_ext}"] = f"""import React from 'react';
import {{ BrowserRouter, Routes, Route, Navigate }} from 'react-router-dom';
{screen_imports}
import './index.css';

const App: React.FC = () => {{
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={{<Navigate to="/screen1" replace />}} />
{screen_routes}
      </Routes>
    </BrowserRouter>
  );
}};

export default App;
"""
        
        # index.css
        files["src/index.css"] = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

#root {
  width: 100%;
  min-height: 100vh;
}
"""
        
        # Generate minimal screen components
        for i in range(screen_count):
            files[f"src/screens/Screen{i+1}.{file_ext}"] = f"""import React from 'react';
import styles from './Screen{i+1}.module.css';

const Screen{i+1}: React.FC = () => {{
  return (
    <div className={{styles.container}}>
      <h1>Screen {i+1}</h1>
      <p>Screen content will be generated here</p>
    </div>
  );
}};

export default Screen{i+1};
"""
            
            files[f"src/screens/Screen{i+1}.module.css"] = f""".container {{
  width: 100%;
  min-height: 100vh;
  padding: 20px;
}}
"""
        
        return files

