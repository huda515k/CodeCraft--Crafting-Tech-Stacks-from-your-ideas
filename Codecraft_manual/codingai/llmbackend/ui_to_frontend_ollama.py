import re
import io
import os
import json
import base64
import zipfile
import requests
import sys
from typing import List, Tuple, Generator, Optional
from pathlib import Path

from qwen_stream import stream_from_llm


# ============================================================
# 🎨 Vision Model Integration (Ollama Vision Models)
# ============================================================

def encode_image_to_base64(image_data: bytes) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_data).decode('utf-8')


def analyze_ui_screenshot_streaming(image_data_list: List[bytes], image_filenames: Optional[List[str]] = None) -> Generator[str, None, None]:
    """
    Analyze UI screenshots using Ollama vision model (llama3.2-vision or similar)
    Returns detailed UI analysis for React code generation
    
    Args:
        image_data_list: List of image data as bytes
        image_filenames: Optional list of filenames for reference
    
    Yields:
        Streaming chunks of analysis text
    """
    
    if not image_data_list:
        yield "❌ No images provided for analysis\n"
        return
    
    # Prepare images for vision model
    images_base64 = []
    for idx, img_data in enumerate(image_data_list):
        try:
            img_base64 = encode_image_to_base64(img_data)
            images_base64.append(img_base64)
        except Exception as e:
            yield f"⚠️ Error encoding image {idx + 1}: {e}\n"
    
    if not images_base64:
        yield "❌ No valid images to analyze\n"
        return
    
    # Vision analysis prompt
    vision_prompt = f"""
You are an expert UI/UX analyst and frontend architect. Analyze these {len(images_base64)} UI screenshot(s) in extreme detail.

For EACH screenshot, provide:

1. **Layout Structure**:
   - Overall layout type (grid, flexbox, sidebar, dashboard, etc.)
   - Main sections and their positioning
   - Container hierarchy
   - Responsive breakpoints if visible

2. **Components Inventory**:
   - Navigation (navbar, sidebar, breadcrumbs)
   - Headers and typography styles
   - Buttons (primary, secondary, icon buttons)
   - Forms (inputs, selects, checkboxes, radio buttons)
   - Cards and containers
   - Tables or lists
   - Modals, dialogs, or overlays
   - Icons and their positions
   - Images and media elements

3. **Visual Design**:
   - Color scheme (primary, secondary, accent colors with hex codes if possible)
   - Typography (font sizes, weights, line heights)
   - Spacing system (padding, margins, gaps)
   - Border radius and shadows
   - Background colors and gradients

4. **Interactive Elements**:
   - Clickable areas (buttons, links, tabs)
   - Form fields and their labels
   - Hover states if visible
   - Active/selected states
   - Loading indicators or animations

5. **Content Structure**:
   - Text content and hierarchy
   - Data displayed (static vs dynamic)
   - Placeholder text
   - Empty states if visible

6. **Technical Requirements**:
   - Suggested React component breakdown
   - State management needs (local state, forms, data fetching)
   - Routing requirements if multi-page
   - Third-party libraries needed (icons, charts, etc.)

Be extremely detailed and technical. This analysis will be used to generate pixel-perfect React code.
"""
    
    # Stream from Ollama vision model
    try:
        # Try vision models first (use /api/chat endpoint for vision)
        vision_models = ["llava:latest", "llama3.2-vision", "bakllava"]
        model_used = None
        
        for model_name in vision_models:
            try:
                # Ollama vision API uses /api/chat endpoint with messages format
                url = "http://localhost:11434/api/chat"
                payload = {
                    "model": model_name,
                    "messages": [{
                        "role": "user",
                        "content": vision_prompt,
                        "images": images_base64
                    }],
                    "stream": True
                }
                
                response = requests.post(url, json=payload, stream=True, timeout=60)
                
                if response.status_code == 200:
                    model_used = model_name
                    yield f"🔍 Analyzing UI screenshots using {model_name}...\n\n"
                    break
            except Exception as e:
                # Try next model
                continue
        
        if not model_used:
            # Fallback: use regular model with text-based analysis
            yield "⚠️ Vision model not available, using text-based analysis with qwen2.5-coder...\n\n"
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "qwen2.5-coder:latest",
                "prompt": vision_prompt + "\n\nNote: Analyze the UI structure based on the description above.",
                "stream": True
            }
            response = requests.post(url, json=payload, stream=True, timeout=60)
            model_used = "qwen2.5-coder:latest"
        
        analysis_text = ""
        buffer = ""
        
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            # Handle both /api/chat and /api/generate response formats
            if "message" in chunk and "content" in chunk["message"]:
                # /api/chat format
                text = chunk["message"]["content"]
                buffer += text
            elif "response" in chunk:
                # /api/generate format
                text = chunk["response"]
                buffer += text
            else:
                continue
            
            # Yield each full line
            while "\n" in buffer:
                part, buffer = buffer.split("\n", 1)
                yield part + "\n"
                analysis_text += part + "\n"
                sys.stdout.write(part + "\n")
                sys.stdout.flush()
            
            # Check for completion
            if chunk.get("done") or (chunk.get("message") and chunk["message"].get("role") == "assistant" and chunk.get("done")):
                if buffer:
                    yield buffer
                    analysis_text += buffer
                    sys.stdout.write(buffer)
                    sys.stdout.flush()
                break
        
        yield "\n\n✅ UI Analysis complete!\n"
        return analysis_text
        
    except Exception as e:
        yield f"❌ Vision model error: {e}\n"
        # Fallback analysis
        yield """
📊 UI Analysis (Fallback):

Layout: Modern dashboard with sidebar navigation
Components: Navigation bar, sidebar, main content area, cards, buttons
Colors: Primary blue (#3B82F6), white backgrounds, gray text
Typography: Sans-serif, multiple heading sizes
Interactive: Multiple buttons, form inputs, navigation links
"""
        return ""


# ============================================================
# ⚛️ React Code Generation (Qwen2.5-Coder)
# ============================================================

def generate_react_from_analysis_streaming(
    ui_analysis: str, 
    additional_specs: str = "",
    include_typescript: bool = True,
    styling_approach: str = "tailwind"
) -> Generator[str, None, None]:
    """
    Generate complete React + TypeScript + Tailwind project from UI analysis
    Uses Qwen2.5-Coder model via stream_from_llm
    
    Args:
        ui_analysis: Detailed UI analysis from vision model
        additional_specs: Optional user requirements
        include_typescript: Whether to use TypeScript
        styling_approach: "tailwind" or "css-modules"
    
    Yields:
        Streaming chunks of generated code
    """
    
    ts_note = "TypeScript" if include_typescript else "JavaScript"
    style_note = "Tailwind CSS" if styling_approach == "tailwind" else "CSS Modules"
    
    code_generation_prompt = f"""
You are an expert React + {ts_note} + {style_note} developer.
Generate a COMPLETE, production-ready React project based on this UI analysis:

{ui_analysis}

Additional Requirements:
{additional_specs if additional_specs else "None - follow the UI analysis exactly"}

🎯 CRITICAL REQUIREMENTS:

1. **Tech Stack**:
   - React 18+ with {"TypeScript" if include_typescript else "JavaScript"}
   - Vite as build tool
   - {"Tailwind CSS 3+" if styling_approach == "tailwind" else "CSS Modules"} for styling
   - Lucide React for icons
   - React Router for navigation (if multi-page)

2. **Project Structure**:
   ```
   project/
   ├── index.html
   ├── package.json
   ├── vite.config.ts
   {"├── tailwind.config.js" if styling_approach == "tailwind" else ""}
   {"├── postcss.config.js" if styling_approach == "tailwind" else ""}
   ├── tsconfig.json
   ├── src/
   │   ├── main.tsx
   │   ├── App.tsx
   │   ├── index.css
   │   ├── components/
   │   │   ├── ui/           (reusable UI components)
   │   │   └── layout/       (layout components)
   │   ├── pages/            (page components)
   │   ├── hooks/            (custom hooks)
   │   └── types/            (TypeScript types)
   ```

3. **Code Quality**:
   - Pixel-perfect implementation matching the UI analysis
   - Proper {"TypeScript types" if include_typescript else "PropTypes"} for all props and state
   - Responsive design (mobile, tablet, desktop)
   - Accessible components (ARIA labels, semantic HTML)
   - Clean, maintainable code with proper comments
   - No placeholder code - everything must be functional

4. **Styling**:
   - Use ONLY {"Tailwind utility classes" if styling_approach == "tailwind" else "CSS Modules"}
   - Match colors, spacing, and typography from analysis
   - Implement hover states and transitions
   - Consistent component spacing

5. **Components**:
   - Break UI into reusable components
   - Extract common patterns (buttons, cards, inputs)
   - Implement all interactive features
   - Handle loading and error states

📤 OUTPUT FORMAT:

Output MULTIPLE files using this EXACT format for EACH file:

```tsx filename=src/App.tsx
// Complete file content here
```

```json filename=package.json
// Complete file content here
```

RULES:
- Every file must start with ```<language> filename=<path>
- Use relative paths (e.g., src/components/Button.tsx)
- Include ALL necessary files (no TODOs or placeholders)
- Files must be complete and runnable
- No explanations between code blocks
- Note: Use safe React + TS + Tailwind + Vite boilerplate only.
- Don't copy user code. Exclude favicon or <link rel="icon">.
- Import Tailwind from './styles/globals.css' or './index.css' (not '/tailwind.css').

Generate the complete project now:
"""
    
    try:
        yield "⚛️ Generating React code...\n\n"
        
        generated_code = ""
        for chunk in stream_from_llm(code_generation_prompt):
            yield chunk
            generated_code += chunk
        
        yield "\n\n✅ React code generation complete!\n"
        return generated_code
        
    except Exception as e:
        yield f"❌ Code generation error: {e}\n"
        return ""


# ============================================================
# 🛠️ Code Extraction & File Processing
# ============================================================

def clean_code_block(code: str) -> str:
    """Remove markdown fences and clean code"""
    code = code.strip()
    code = re.sub(r"^```[a-zA-Z0-9]*\n?", "", code)
    code = re.sub(r"```$", "", code)
    return code.strip()


def extract_react_files(generated_output: str) -> List[Tuple[str, str]]:
    """
    Extract multiple files from generated React code
    Returns list of (filepath, content) tuples
    """
    files = []
    seen = set()
    
    # Pattern: ```tsx filename=src/App.tsx
    filename_pattern = re.compile(
        r"```(\w+)\s+filename=([^\n]+)\n([\s\S]*?)```",
        re.MULTILINE | re.DOTALL
    )
    
    for match in filename_pattern.finditer(generated_output):
        lang, filepath, content = match.groups()
        filepath = filepath.strip()
        
        if filepath and content and filepath not in seen:
            files.append((filepath, clean_code_block(content)))
            seen.add(filepath)
    
    # Fallback: look for standard filename comments or other patterns
    if not files:
        # Try pattern: ```tsx:src/App.tsx
        alt_pattern = re.compile(
            r"```(\w+):([^\n]+)\n([\s\S]*?)```",
            re.MULTILINE | re.DOTALL
        )
        for match in alt_pattern.finditer(generated_output):
            lang, filepath, content = match.groups()
            filepath = filepath.strip()
            if filepath and content and filepath not in seen:
                files.append((filepath, clean_code_block(content)))
                seen.add(filepath)
    
    # Additional fallback: look for JSON-style dicts
    if not files:
        try:
            data = json.loads(generated_output)
            if isinstance(data, dict):
                for path, content in data.items():
                    if isinstance(content, (dict, list)):
                        content = json.dumps(content, indent=2)
                    path, content = str(path).strip(), str(content).strip()
                    if path and content and path not in seen:
                        files.append((path, clean_code_block(content)))
                        seen.add(path)
        except Exception:
            pass
    
    return files


def create_project_zip(files: List[Tuple[str, str]]) -> io.BytesIO:
    """Create a zip file from list of (filepath, content) tuples"""
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filepath, content in files:
            zip_file.writestr(filepath, content)
    
    buffer.seek(0)
    return buffer


# ============================================================
# 🚀 Main Pipeline Function
# ============================================================

def ui_to_react_pipeline_streaming(
    image_data_list: List[bytes],
    additional_requirements: str = "",
    include_typescript: bool = True,
    styling_approach: str = "tailwind"
) -> Generator[str, None, None]:
    """
    Complete pipeline: UI screenshots → Analysis → React code → Files
    
    Args:
        image_data_list: List of UI screenshot image data as bytes
        additional_requirements: Optional user specifications
        include_typescript: Whether to use TypeScript
        styling_approach: "tailwind" or "css-modules"
    
    Yields:
        Streaming updates and final generated code
    """
    
    yield "🎨 ════════════════════════════════════════\n"
    yield "   UI SCREENSHOT TO REACT CODE (Ollama)\n"
    yield "════════════════════════════════════════\n\n"
    
    # Step 1: Analyze UI with vision model
    yield "📸 Step 1/3: Analyzing UI screenshots...\n"
    yield "─" * 50 + "\n"
    
    ui_analysis = ""
    for chunk in analyze_ui_screenshot_streaming(image_data_list):
        yield chunk
        ui_analysis += chunk
    
    yield "\n" + "─" * 50 + "\n\n"
    
    # Step 2: Generate React code
    yield "⚛️  Step 2/3: Generating React code...\n"
    yield "─" * 50 + "\n"
    
    generated_code = ""
    for chunk in generate_react_from_analysis_streaming(
        ui_analysis, 
        additional_requirements,
        include_typescript,
        styling_approach
    ):
        yield chunk
        generated_code += chunk
    
    yield "\n" + "─" * 50 + "\n\n"
    
    # Step 3: Extract files
    yield "📦 Step 3/3: Extracting files...\n"
    yield "─" * 50 + "\n"
    
    try:
        files = extract_react_files(generated_code)
        
        if not files:
            yield "⚠️  No files extracted. Attempting fallback extraction...\n"
            # Try to extract from code blocks without filename
            code_block_pattern = re.compile(
                r"```(\w+)\n([\s\S]*?)```",
                re.MULTILINE | re.DOTALL
            )
            file_counter = 1
            for match in code_block_pattern.finditer(generated_code):
                lang, content = match.groups()
                ext_map = {
                    'tsx': '.tsx', 'ts': '.ts', 'jsx': '.jsx', 'js': '.js',
                    'json': '.json', 'html': '.html', 'css': '.css', 'md': '.md'
                }
                ext = ext_map.get(lang, '.txt')
                filename = f"file_{file_counter}{ext}"
                files.append((filename, clean_code_block(content)))
                file_counter += 1
        
        yield f"✅ Extracted {len(files)} files:\n"
        for filepath, _ in files[:20]:  # Show first 20 files
            yield f"   • {filepath}\n"
        if len(files) > 20:
            yield f"   ... and {len(files) - 20} more files\n"
        
        yield "\n✨ React project generated successfully!\n\n"
        yield "═" * 50 + "\n"
        
        # Return files for further processing
        return files
        
    except Exception as e:
        yield f"\n❌ Error processing project: {e}\n"
        return []


# ============================================================
# 🎯 Simplified Entry Point (for integration)
# ============================================================

def ui_to_frontend_ollama(
    image_data: bytes,
    additional_context: str = "",
    include_typescript: bool = True,
    styling_approach: str = "tailwind"
) -> Generator[str, None, None]:
    """
    Main entry point for UI to Frontend conversion using Ollama
    Compatible with the existing module structure
    
    Args:
        image_data: Single image as bytes
        additional_context: Optional additional requirements
        include_typescript: Whether to use TypeScript
        styling_approach: "tailwind" or "css-modules"
    
    Yields:
        Streaming code chunks
    """
    for chunk in ui_to_react_pipeline_streaming(
        [image_data],
        additional_context,
        include_typescript,
        styling_approach
    ):
        yield chunk


def ui_to_frontend_ollama_multiple(
    image_data_list: List[bytes],
    additional_context: str = "",
    include_typescript: bool = True,
    styling_approach: str = "tailwind"
) -> Generator[str, None, None]:
    """
    Entry point for multiple UI images to Frontend conversion using Ollama
    
    Args:
        image_data_list: List of images as bytes
        additional_context: Optional additional requirements
        include_typescript: Whether to use TypeScript
        styling_approach: "tailwind" or "css-modules"
    
    Yields:
        Streaming code chunks
    """
    for chunk in ui_to_react_pipeline_streaming(
        image_data_list,
        additional_context,
        include_typescript,
        styling_approach
    ):
        yield chunk
