# frontend_generator/code_generator.py

from typing import Dict, List
from .models import UIAnalysis, UIComponent, Style, ComponentType

class ReactCodeGenerator:
    """Generate React code from UI analysis"""
    
    def __init__(self, include_typescript: bool = True, styling_approach: str = "css-modules"):
        self.include_typescript = include_typescript
        self.styling_approach = styling_approach
    
    def _format_css_dimension(self, value):
        """Format a dimension value for CSS - handles both numeric and CSS string values"""
        if value is None:
            return None
        if isinstance(value, str):
            # Already a CSS value (e.g., '100vh', 'auto', 'calc(...)', '100%')
            return value
        if isinstance(value, (int, float)):
            # Numeric value, append 'px'
            return f"{value}px"
        # Fallback: convert to string
        return str(value)
    
    def generate_project(self, ui_analysis: UIAnalysis, project_name: str = "react-app") -> Dict[str, str]:
        """
        Generate complete React project files from UI analysis
        Returns dictionary of file paths to file contents
        """
        files = {}
        
        # Generate package.json
        files["package.json"] = self._generate_package_json(project_name)
        
        # Generate index.html (REQUIRED for Vite)
        files["index.html"] = self._generate_index_html(project_name)
        
        # Generate vite.config.js (REQUIRED for Vite)
        files["vite.config.ts" if self.include_typescript else "vite.config.js"] = self._generate_vite_config()
        
        # Generate tsconfig.json and tsconfig.node.json if TypeScript
        if self.include_typescript:
            files["tsconfig.json"] = self._generate_tsconfig()
            files["tsconfig.node.json"] = self._generate_tsconfig_node()
        
        # Generate main App component
        files["src/App.tsx" if self.include_typescript else "src/App.jsx"] = self._generate_app_component(ui_analysis)
        
        # Generate index file
        files["src/index.tsx" if self.include_typescript else "src/index.jsx"] = self._generate_index_file()
        
        # Generate individual components
        for component in ui_analysis.components:
            component_file = self._generate_component(component, ui_analysis)
            component_name = self._sanitize_component_name(component.name)
            file_ext = "tsx" if self.include_typescript else "jsx"
            files[f"src/components/{component_name}.{file_ext}"] = component_file
            
            # Generate CSS file if using CSS modules
            if self.styling_approach == "css-modules":
                css_file = self._generate_component_styles(component)
                files[f"src/components/{component_name}.module.css"] = css_file
        
        # Generate global styles
        files["src/index.css"] = self._generate_global_styles(ui_analysis)
        
        # Generate README
        files["README.md"] = self._generate_readme(project_name, ui_analysis)
        
        return files
    
    def _generate_package_json(self, project_name: str) -> str:
        """Generate package.json"""
        deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0"
        }
        
        if self.include_typescript:
            deps.update({
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "typescript": "^5.0.0"
            })
        
        if self.styling_approach == "tailwind":
            deps["tailwindcss"] = "^3.3.0"
            deps["autoprefixer"] = "^10.4.0"
            deps["postcss"] = "^8.4.0"
        
        dev_deps = {
            "@vitejs/plugin-react": "^4.0.0",
            "vite": "^4.4.0"
        }
        
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": deps,
            "devDependencies": dev_deps
        }
        
        import json
        return json.dumps(package_json, indent=2)
    
    def _generate_tsconfig(self) -> str:
        """Generate TypeScript configuration"""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }
        
        import json
        return json.dumps(tsconfig, indent=2)
    
    def _generate_tsconfig_node(self) -> str:
        """Generate TypeScript configuration for Node.js files (Vite config, etc.)"""
        tsconfig_node = {
            "compilerOptions": {
                "composite": True,
                "skipLibCheck": True,
                "module": "ESNext",
                "moduleResolution": "bundler",
                "allowSyntheticDefaultImports": True
            },
            "include": ["vite.config.ts"]
        }
        
        import json
        return json.dumps(tsconfig_node, indent=2)
    
    def _generate_app_component(self, ui_analysis: UIAnalysis) -> str:
        """Generate main App component"""
        file_ext = "tsx" if self.include_typescript else "jsx"
        
        # Find root components (components without parents)
        root_components = [c for c in ui_analysis.components if c.parent_id is None]
        
        imports = []
        components = []
        
        for root_comp in root_components:
            comp_name = self._sanitize_component_name(root_comp.name)
            imports.append(f"import {comp_name} from './components/{comp_name}.{file_ext}';")
            components.append(f"      <{comp_name} />")
        
        import_str = "\n".join(imports)
        component_str = "\n".join(components) if components else "      <div>No components found</div>"
        
        # Get layout type for app container
        layout_type = "flex"
        if ui_analysis.layout and ui_analysis.layout.type:
            layout_type = ui_analysis.layout.type.value if hasattr(ui_analysis.layout.type, 'value') else str(ui_analysis.layout.type)
        
        # Generate layout styles inline or via className
        app_class = "app"
        if layout_type == "flex":
            app_class += " app-flex"
        elif layout_type == "grid":
            app_class += " app-grid"
        
        if self.include_typescript:
            return f"""import React from 'react';
{import_str}
import './index.css';

const App: React.FC = () => {{
  return (
    <div className="{app_class}">
{component_str}
    </div>
  );
}};

export default App;
"""
        else:
            return f"""import React from 'react';
{import_str}
import './index.css';

function App() {{
  return (
    <div className="{app_class}">
{component_str}
    </div>
  );
}}

export default App;
"""
    
    def _get_html_element_for_component_type(self, component_type: ComponentType) -> str:
        """Map component type to appropriate HTML element"""
        type_mapping = {
            ComponentType.BUTTON: "button",
            ComponentType.INPUT: "input",
            ComponentType.HEADING: "h1",
            ComponentType.H1: "h1",
            ComponentType.H2: "h2",
            ComponentType.H3: "h3",
            ComponentType.TEXT: "span",
            ComponentType.PARAGRAPH: "p",
            ComponentType.LINK: "a",
            ComponentType.IMAGE: "img",
            ComponentType.HEADER: "header",
            ComponentType.FOOTER: "footer",
            ComponentType.NAVBAR: "nav",
            ComponentType.FORM: "form",
            ComponentType.LIST: "ul",
            ComponentType.LIST_ITEM: "li",
            ComponentType.ICON: "span",  # Icons are typically spans with icon classes
            ComponentType.BADGE: "span",
            ComponentType.AVATAR: "div",  # Avatar is typically a div with styling
        }
        return type_mapping.get(component_type, "div")
    
    def _generate_component(self, component: UIComponent, ui_analysis: UIAnalysis) -> str:
        """Generate React component code"""
        comp_name = self._sanitize_component_name(component.name)
        file_ext = "tsx" if self.include_typescript else "jsx"
        
        # Get the appropriate HTML element for this component type
        html_element = self._get_html_element_for_component_type(component.type)
        is_self_closing = html_element in ["input", "img"]
        
        # Generate props interface if TypeScript and has properties
        props_interface = ""
        props_name = ""
        if self.include_typescript and component.properties:
            props_list = []
            for prop in component.properties:
                type_map = {
                    "string": "string",
                    "number": "number",
                    "boolean": "boolean"
                }
                prop_type = type_map.get(prop.type, "any")
                optional = "?" if not prop.required else ""
                default_val = f" = {repr(prop.default_value)}" if prop.default_value else ""
                props_list.append(f"  {prop.name}{optional}: {prop_type}{default_val};")
            
            if props_list:
                props_interface = f"interface {comp_name}Props {{\n" + "\n".join(props_list) + "\n}\n\n"
                props_name = f": {comp_name}Props"
        
        # Generate child components and their imports
        children_components = []
        child_imports = []
        if component.children:
            for child_id in component.children:
                child_comp = next((c for c in ui_analysis.components if c.id == child_id), None)
                if child_comp:
                    child_name = self._sanitize_component_name(child_comp.name)
                    children_components.append(f"        <{child_name} />")
                    # Add import for child component
                    child_imports.append(f"import {child_name} from './{child_name}.{file_ext}';")
        
        # Generate component content
        content = ""
        if is_self_closing:
            # Self-closing elements (input, img) don't have children content
            content = ""
        elif component.text_content:
            # Use text content if available
            content = f"        {component.text_content}\n"
        elif children_components:
            # Use child components if available
            content = "\n".join(children_components)
        else:
            # If no content and no children, add a visible placeholder
            # This ensures the component is visible even if empty
            if html_element in ["button", "input"]:
                content = f"        {component.name}\n"
            elif html_element in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                content = f"        {component.name}\n"
            else:
                content = f"        {component.name}\n"
        
        # Generate className based on styling approach
        if self.styling_approach == "css-modules":
            className = f"className={{styles.{comp_name.lower()}}}"
        else:
            className = f'className="{comp_name.lower()}"'
        
        # Generate attributes for input elements
        attributes = ""
        if html_element == "input":
            # Add placeholder and other input attributes
            placeholder = component.attributes.get("placeholder", "")
            if placeholder:
                attributes = f' placeholder="{placeholder}"'
            if component.text_content:
                attributes += f' defaultValue="{component.text_content}"'
        
        # Generate import statement for styles
        style_import = ""
        if self.styling_approach == "css-modules":
            style_import = f"import styles from './{comp_name}.module.css';\n"
        
        # Combine all imports
        all_imports = "import React from 'react';\n"
        if child_imports:
            all_imports += "\n".join(child_imports) + "\n"
        if style_import:
            all_imports += style_import
        
        # Generate component JSX
        if is_self_closing:
            element_jsx = f"    <{html_element} {className}{attributes} />"
        else:
            element_jsx = f"    <{html_element} {className}{attributes}>\n{content}\n    </{html_element}>"
        
        if self.include_typescript:
            # Only add props interface and type if there are actual props
            props_declaration = f": {comp_name}Props" if component.properties and props_interface else ""
            props_param = "props" if component.properties else ""
            return f"""{all_imports}{props_interface}const {comp_name}: React.FC{props_declaration} = ({props_param}) => {{
  return (
{element_jsx}
  );
}};

export default {comp_name};
"""
        else:
            props_param = "props" if component.properties else ""
            return f"""{all_imports}function {comp_name}({props_param}) {{
  return (
{element_jsx}
  );
}}

export default {comp_name};
"""
    
    def _generate_component_styles(self, component: UIComponent) -> str:
        """Generate CSS module styles for component"""
        comp_name = self._sanitize_component_name(component.name).lower()
        style = component.style
        
        css_rules = [f".{comp_name} {{"]
        
        # Ensure component has display property
        if style and style.layout_type:
            if style.layout_type.value == "flex":
                css_rules.append("  display: flex;")
            elif style.layout_type.value == "grid":
                css_rules.append("  display: grid;")
            else:
                css_rules.append("  display: block;")
        else:
            # Default to block if no layout type specified
            css_rules.append("  display: block;")
        
        # Add position if available (check both component.position and style.position)
        pos = None
        if component.position:
            pos = component.position
        elif style and style.position:
            pos = style.position
        
        if pos:
            if pos.x is not None:
                css_rules.append(f"  position: relative;")
                x_value = self._format_css_dimension(pos.x)
                css_rules.append(f"  left: {x_value};")
            if pos.y is not None:
                y_value = self._format_css_dimension(pos.y)
                css_rules.append(f"  top: {y_value};")
            if pos.width is not None:
                width_value = self._format_css_dimension(pos.width)
                css_rules.append(f"  width: {width_value};")
            if pos.height is not None:
                height_value = self._format_css_dimension(pos.height)
                css_rules.append(f"  height: {height_value};")
        
        if style:
            if style.background_color:
                # Handle different color formats (rgba, rgb, hex)
                if style.background_color.rgba:
                    css_rules.append(f"  background-color: {style.background_color.rgba};")
                elif style.background_color.rgb:
                    css_rules.append(f"  background-color: {style.background_color.rgb};")
                elif style.background_color.hex:
                    css_rules.append(f"  background-color: {style.background_color.hex};")
            
            if style.typography:
                typo = style.typography
                if typo.font_family:
                    css_rules.append(f"  font-family: {typo.font_family};")
                if typo.font_size:
                    css_rules.append(f"  font-size: {typo.font_size};")
                if typo.font_weight:
                    css_rules.append(f"  font-weight: {typo.font_weight};")
                if typo.color:
                    # Handle different color formats
                    if typo.color.rgba:
                        css_rules.append(f"  color: {typo.color.rgba};")
                    elif typo.color.rgb:
                        css_rules.append(f"  color: {typo.color.rgb};")
                    elif typo.color.hex:
                        css_rules.append(f"  color: {typo.color.hex};")
                if typo.text_align:
                    css_rules.append(f"  text-align: {typo.text_align};")
            
            if style.spacing:
                spacing = style.spacing
                if spacing.padding:
                    css_rules.append(f"  padding: {spacing.padding};")
                if spacing.margin:
                    css_rules.append(f"  margin: {spacing.margin};")
                if spacing.gap:
                    css_rules.append(f"  gap: {spacing.gap};")
            
            if style.border:
                border = style.border
                if border.width:
                    css_rules.append(f"  border-width: {border.width};")
                if border.style:
                    css_rules.append(f"  border-style: {border.style};")
                if border.color:
                    # Handle different color formats
                    if border.color.rgba:
                        css_rules.append(f"  border-color: {border.color.rgba};")
                    elif border.color.rgb:
                        css_rules.append(f"  border-color: {border.color.rgb};")
                    elif border.color.hex:
                        css_rules.append(f"  border-color: {border.color.hex};")
                if border.radius:
                    css_rules.append(f"  border-radius: {border.radius};")
            
            if style.shadow:
                shadow = style.shadow
                shadow_parts = []
                if shadow.x:
                    shadow_parts.append(str(shadow.x))
                if shadow.y:
                    shadow_parts.append(str(shadow.y))
                if shadow.blur:
                    shadow_parts.append(str(shadow.blur))
                if shadow.spread:
                    shadow_parts.append(str(shadow.spread))
                if shadow.color:
                    # Handle different color formats (hex, rgb, rgba)
                    if shadow.color.rgba:
                        shadow_parts.append(shadow.color.rgba)
                    elif shadow.color.rgb:
                        shadow_parts.append(shadow.color.rgb)
                    elif shadow.color.hex:
                        shadow_parts.append(shadow.color.hex)
                if shadow_parts:
                    css_rules.append(f"  box-shadow: {' '.join(shadow_parts)};")
            
            # Layout type already handled above, but add flex/grid properties if needed
            if style.layout_type:
                if style.layout_type.value == "flex":
                    # display: flex already added above
                    if style.flex_direction:
                        css_rules.append(f"  flex-direction: {style.flex_direction};")
                    if style.justify_content:
                        css_rules.append(f"  justify-content: {style.justify_content};")
                    if style.align_items:
                        css_rules.append(f"  align-items: {style.align_items};")
                elif style.layout_type.value == "grid":
                    # display: grid already added above
                    if style.grid_template_columns:
                        css_rules.append(f"  grid-template-columns: {style.grid_template_columns};")
                    if style.grid_template_rows:
                        css_rules.append(f"  grid-template-rows: {style.grid_template_rows};")
            
            if style.width:
                width_value = self._format_css_dimension(style.width) if isinstance(style.width, (int, float)) else str(style.width)
                css_rules.append(f"  width: {width_value};")
            if style.height:
                height_value = self._format_css_dimension(style.height) if isinstance(style.height, (int, float)) else str(style.height)
                css_rules.append(f"  height: {height_value};")
            if style.z_index is not None:
                css_rules.append(f"  z-index: {style.z_index};")
            if style.opacity is not None:
                css_rules.append(f"  opacity: {style.opacity};")
        
        css_rules.append("}")
        return "\n".join(css_rules)
    
    def _generate_global_styles(self, ui_analysis: UIAnalysis) -> str:
        """Generate global CSS styles"""
        css = ["* {", "  margin: 0;", "  padding: 0;", "  box-sizing: border-box;", "}", ""]
        
        css.append("html, body {")
        css.append("  width: 100%;")
        css.append("  height: 100%;")
        css.append("  margin: 0;")
        css.append("  padding: 0;")
        if ui_analysis.layout and ui_analysis.layout.background_color:
            # Handle different color formats
            bg_color = None
            if ui_analysis.layout.background_color.rgba:
                bg_color = ui_analysis.layout.background_color.rgba
            elif ui_analysis.layout.background_color.rgb:
                bg_color = ui_analysis.layout.background_color.rgb
            elif ui_analysis.layout.background_color.hex:
                bg_color = ui_analysis.layout.background_color.hex
            
            if bg_color:
                css.append(f"  background-color: {bg_color};")
        else:
            css.append("  background-color: #ffffff;")
        
        if ui_analysis.typography:
            typo = ui_analysis.typography
            if typo.font_family:
                # Clean up font-family - remove comments and invalid syntax
                font_family = typo.font_family.split('(')[0].strip() if '(' in typo.font_family else typo.font_family.strip()
                # Remove common invalid patterns
                font_family = font_family.replace('(Likely ', '').replace(')', '').strip()
                if font_family:
                    css.append(f"  font-family: '{font_family}', sans-serif;")
            if typo.font_size:
                # Clean up font-size - remove comments
                font_size = typo.font_size.split('(')[0].strip() if '(' in typo.font_size else typo.font_size.strip()
                if font_size:
                    css.append(f"  font-size: {font_size};")
            if typo.color:
                # Handle different color formats
                if typo.color.rgba:
                    css.append(f"  color: {typo.color.rgba};")
                elif typo.color.rgb:
                    css.append(f"  color: {typo.color.rgb};")
                elif typo.color.hex:
                    css.append(f"  color: {typo.color.hex};")
        css.append("}")
        
        css.append("")
        css.append("#root {")
        css.append("  width: 100%;")
        css.append("  min-height: 100vh;")
        if ui_analysis.layout:
            if ui_analysis.layout.width:
                css.append(f"  max-width: {ui_analysis.layout.width};")
                css.append("  margin: 0 auto;")
        css.append("}")
        
        css.append("")
        css.append(".app {")
        css.append("  width: 100%;")
        css.append("  min-height: 100vh;")
        
        # Apply layout type
        if ui_analysis.layout and ui_analysis.layout.type:
            layout_type = ui_analysis.layout.type.value if hasattr(ui_analysis.layout.type, 'value') else str(ui_analysis.layout.type)
            if layout_type == "flex":
                css.append("  display: flex;")
                # Apply flex direction if available
                if ui_analysis.layout.width:
                    css.append(f"  width: {ui_analysis.layout.width};")
                if ui_analysis.layout.height:
                    css.append(f"  height: {ui_analysis.layout.height};")
            elif layout_type == "grid":
                css.append("  display: grid;")
            else:
                css.append("  display: block;")
        
        if ui_analysis.layout:
            if ui_analysis.layout.padding:
                css.append(f"  padding: {ui_analysis.layout.padding};")
        css.append("}")
        
        return "\n".join(css)
    
    def _generate_index_file(self) -> str:
        """Generate index.tsx/jsx file"""
        if self.include_typescript:
            return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        else:
            return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    def _generate_index_html(self, project_name: str) -> str:
        """Generate index.html file for Vite"""
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.{'tsx' if self.include_typescript else 'jsx'}"></script>
  </body>
</html>
"""
    
    def _generate_vite_config(self) -> str:
        """Generate vite.config.js/ts file"""
        if self.include_typescript:
            return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
"""
        else:
            return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
"""
    
    def _generate_readme(self, project_name: str, ui_analysis: UIAnalysis) -> str:
        """Generate README.md"""
        components_list = "\n".join([f"- {c.name} ({c.type.value})" for c in ui_analysis.components])
        
        return f"""# {project_name}

React application generated from UI design.

## Components

{components_list}

## Getting Started

\`\`\`bash
npm install
npm run dev
\`\`\`

## Build

\`\`\`bash
npm run build
\`\`\`

Generated by CodeCraft Frontend Generator.
"""
    
    def _sanitize_component_name(self, name: str) -> str:
        """Sanitize component name for use in code"""
        # Remove special characters, capitalize first letter of each word
        import re
        name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        words = name.split()
        return ''.join(word.capitalize() for word in words) if words else "Component"

