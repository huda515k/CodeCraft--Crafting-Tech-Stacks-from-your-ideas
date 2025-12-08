#!/usr/bin/env python3
"""
Generate complete Social Network app with all screens in ONE project
Creates a single ZIP with React Router connecting all components
"""

import requests
import zipfile
import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Optional

SERVER_URL = "http://localhost:8000"

# All 12 screens with their routes and descriptions
SCREENS = [
    {
        "name": "WelcomeScreen",
        "display_name": "Welcome/Splash Screen",
        "image": "welcome_splash.png",
        "route": "/",
        "description": "Welcome screen with teal background, 'SOCIAL NETWORK' title, speech bubbles, and 'LET'S GO!' button"
    },
    {
        "name": "SignInScreen",
        "display_name": "Sign In/Sign Up Form",
        "image": "sign_in_form.png",
        "route": "/signin",
        "description": "Sign in form with name, email, password fields, checkbox, and SIGN IN button"
    },
    {
        "name": "NavigationMenu",
        "display_name": "Navigation Menu/Sidebar",
        "image": "navigation_menu.png",
        "route": "/menu",
        "description": "Sidebar menu with profile, HOME, MESSAGES, MY SUBSCRIBERS, SETTINGS, NOTIFICATION"
    },
    {
        "name": "UserProfile",
        "display_name": "User Profile View",
        "image": "user_profile.png",
        "route": "/profile",
        "description": "User profile with picture, name, description, and interests grid (music, food, culture, etc.)"
    },
    {
        "name": "SubscribersList",
        "display_name": "My Subscribers List",
        "image": "subscribers_list.png",
        "route": "/subscribers",
        "description": "Grid of subscriber profile pictures with names"
    },
    {
        "name": "TopContacts",
        "display_name": "Top Contacts/Recommendations",
        "image": "top_contacts.png",
        "route": "/contacts",
        "description": "Search bar, recommendations carousel, and my contacts list"
    },
    {
        "name": "MemoriesList",
        "display_name": "My Memories (List View)",
        "image": "memories_list.png",
        "route": "/memories",
        "description": "Vertical list of memory cards with images, titles, likes, and comments"
    },
    {
        "name": "MemoriesGrid",
        "display_name": "Experience Memories (Grid View)",
        "image": "memories_grid.png",
        "route": "/memories/grid",
        "description": "Grid of square image placeholders with search bar"
    },
    {
        "name": "UploadPhoto",
        "display_name": "Message/Upload Photo",
        "image": "upload_photo.png",
        "route": "/upload",
        "description": "Upload photo screen with camera icon, caption input, and POST button"
    },
    {
        "name": "MessagesList",
        "display_name": "Messages List",
        "image": "messages_list.png",
        "route": "/messages",
        "description": "List of message previews with profile pictures, names, message snippets, and unread badges"
    },
    {
        "name": "HelpSupport",
        "display_name": "Help and Support",
        "image": "help_support.png",
        "route": "/help",
        "description": "Contact form with email, question type, message field, and SEND button"
    },
    {
        "name": "ChatView",
        "display_name": "Experience Memories (Chat View)",
        "image": "chat_view.png",
        "route": "/chat",
        "description": "Chat interface with message bubbles (left white, right teal) and message input"
    }
]

def generate_screen_component(image_path: str, screen_info: dict) -> Optional[Dict]:
    """Generate React component for a single screen"""
    print(f"   📱 {screen_info['display_name']}...", end=" ", flush=True)
    
    if not os.path.exists(image_path):
        print("⚠️  Image not found")
        return None
    
    url = f"{SERVER_URL}/frontend/generate-react"
    
    context = f"""
Generate a complete React component for the {screen_info['display_name']} screen.

CRITICAL REQUIREMENTS:
- Color scheme: Teal/turquoise (#00CED1 or similar), white (#FFFFFF), and yellow/gold (#FFD700 or similar)
- Mobile-first design (typical mobile screen dimensions: 400x800px)
- Include ALL UI elements exactly as shown: buttons, inputs, text, icons, images, cards
- Match the layout structure precisely
- Use proper React component structure with TypeScript
- Component name should be: {screen_info['name']}
- Export as default export
- Make sure all components are visible and properly styled

Screen Description:
{screen_info['description']}

Return a complete, runnable React component that can be imported and used directly.
"""
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'include_typescript': 'true',
                'styling_approach': 'css-modules',
                'additional_context': context
            }
            
            response = requests.post(url, files=files, data=data, timeout=300)
            
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}")
                return None
            
            # Extract ZIP to temp directory
            temp_dir = tempfile.mkdtemp(prefix=f"screen_{screen_info['name']}_")
            zip_path = os.path.join(temp_dir, "screen.zip")
            
            with open(zip_path, 'wb') as zf:
                zf.write(response.content)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(temp_dir)
            
            print("✅")
            return {
                'screen_info': screen_info,
                'temp_dir': temp_dir
            }
            
    except Exception as e:
        print(f"❌ {str(e)[:50]}")
        return None

def extract_components_from_screen(temp_dir: str, screen_name: str) -> Dict[str, str]:
    """Extract all components and CSS from a generated screen"""
    components = {}
    src_dir = Path(temp_dir) / "src"
    
    if not src_dir.exists():
        return components
    
    # Get all component files
    for comp_file in (src_dir / "components").rglob("*.tsx"):
        rel_path = comp_file.relative_to(src_dir / "components")
        with open(comp_file, 'r', encoding='utf-8') as f:
            components[f"src/components/{rel_path}"] = f.read()
    
    # Get all CSS files
    for css_file in src_dir.rglob("*.css"):
        rel_path = css_file.relative_to(src_dir)
        with open(css_file, 'r', encoding='utf-8') as f:
            components[f"src/{rel_path}"] = f.read()
    
    return components

def find_main_component(components: Dict[str, str], screen_name: str) -> Optional[str]:
    """Find the main container component for a screen"""
    # Look for components that might be the main container
    for path, content in components.items():
        if screen_name.lower().replace('screen', '').replace('view', '') in path.lower():
            return path
        if 'container' in path.lower() or 'main' in path.lower():
            return path
    
    # Return the first component if no match
    comp_files = [p for p in components.keys() if p.endswith('.tsx')]
    return comp_files[0] if comp_files else None

def create_complete_project(screen_results: List[Dict], output_path: str = "social_network_complete_app.zip"):
    """Create a complete project with all screens connected via React Router"""
    print(f"\n🔨 Creating complete app with {len([r for r in screen_results if r])} screens...")
    
    project_files = {}
    screen_components_map = {}
    all_components = {}
    
    # Collect all components from generated screens
    for result in screen_results:
        if not result:
            continue
        
        screen_info = result['screen_info']
        screen_name = screen_info['name']
        temp_dir = result['temp_dir']
        
        # Extract components
        components = extract_components_from_screen(temp_dir, screen_name)
        all_components.update(components)
        
        # Find main component
        main_comp_path = find_main_component(components, screen_name)
        if main_comp_path:
            # Get component name from path
            comp_name = Path(main_comp_path).stem
            # Capitalize first letter
            comp_name = comp_name[0].upper() + comp_name[1:] if comp_name else screen_name
            
            screen_components_map[screen_name] = {
                'component_name': comp_name,
                'component_path': main_comp_path,
                'route': screen_info['route'],
                'display_name': screen_info['display_name']
            }
    
    if not screen_components_map:
        print("❌ No screens were generated successfully")
        return None
    
    # 1. package.json with React Router
    package_json = {
        "name": "social-network-app",
        "version": "1.0.0",
        "private": True,
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.20.0"
        },
        "devDependencies": {
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "@vitejs/plugin-react": "^4.0.0",
            "typescript": "^5.0.0",
            "vite": "^4.4.0"
        }
    }
    project_files["package.json"] = json.dumps(package_json, indent=2)
    
    # 2. vite.config.ts
    project_files["vite.config.ts"] = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
"""
    
    # 3. tsconfig.json
    project_files["tsconfig.json"] = json.dumps({
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
            "strict": True
        },
        "include": ["src"]
    }, indent=2)
    
    # 4. index.html
    project_files["index.html"] = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Social Network App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.tsx"></script>
  </body>
</html>
"""
    
    # 5. Add all extracted components and CSS
    project_files.update(all_components)
    
    # 6. Create screen wrapper components that import the actual components
    screen_imports = []
    screen_routes = []
    
    for screen_name, screen_data in screen_components_map.items():
        comp_name = screen_data['component_name']
        comp_path = screen_data['component_path']
        route = screen_data['route']
        
        # Import path (relative from screens directory)
        import_path = comp_path.replace('src/components/', '../components/').replace('.tsx', '')
        
        # Create screen wrapper
        screen_imports.append(f"import {comp_name} from '{import_path}';")
        screen_routes.append(f'        <Route path="{route}" element={{<{comp_name} />}} />')
        
        # Create screen file
        project_files[f"src/screens/{screen_name}.tsx"] = f"""import React from 'react';
import {comp_name} from '{import_path}';

const {screen_name}: React.FC = () => {{
  return <{comp_name} />;
}};

export default {screen_name};
"""
    
    # 7. Create App.tsx with React Router
    project_files["src/App.tsx"] = f"""import React from 'react';
import {{ BrowserRouter, Routes, Route, Link, useNavigate }} from 'react-router-dom';
{chr(10).join(screen_imports)}
import './index.css';

const Navigation: React.FC = () => {{
  return (
    <nav className="app-navigation">
      <Link to="/">Welcome</Link>
      <Link to="/signin">Sign In</Link>
      <Link to="/profile">Profile</Link>
      <Link to="/messages">Messages</Link>
      <Link to="/memories">Memories</Link>
      <Link to="/contacts">Contacts</Link>
    </nav>
  );
}};

const App: React.FC = () => {{
  return (
    <BrowserRouter>
      <div className="app">
        <Navigation />
        <main className="app-main">
          <Routes>
{chr(10).join(screen_routes)}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}};

export default App;
"""
    
    # 8. index.tsx
    project_files["src/index.tsx"] = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    # 9. Enhanced index.css with navigation styles
    project_files["src/index.css"] = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  font-family: 'Poppins', 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

#root {
  width: 100%;
  min-height: 100vh;
}

.app {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-navigation {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #00CED1;
  flex-wrap: wrap;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.app-navigation a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.app-navigation a:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.app-navigation a.active {
  background-color: rgba(255, 255, 255, 0.3);
}

.app-main {
  flex: 1;
  width: 100%;
  min-height: calc(100vh - 60px);
}
"""
    
    # 10. README
    screens_list = "\n".join([f"- **{data['display_name']}**: `{data['route']}`" for data in screen_components_map.values()])
    project_files["README.md"] = f"""# Social Network App

Complete React application with {len(screen_components_map)} connected screens.

## 🚀 Getting Started

```bash
npm install
npm run dev
```

Then open http://localhost:3000 in your browser.

## 📱 Available Screens

{screens_list}

## 🧭 Navigation

Use the navigation bar at the top to switch between screens, or navigate directly using the routes above.

## 🏗️ Project Structure

```
src/
├── App.tsx              # Main app with React Router
├── index.tsx            # Entry point
├── index.css            # Global styles
├── screens/             # Screen wrappers
│   ├── WelcomeScreen.tsx
│   ├── SignInScreen.tsx
│   └── ...
└── components/          # Reusable components
    ├── [Component].tsx
    └── [Component].module.css
```

## 🎨 Design

- **Primary Color**: Teal/Turquoise (#00CED1)
- **Secondary Color**: White (#FFFFFF)
- **Accent Color**: Yellow/Gold (#FFD700)
- **Mobile-first** responsive design

## 📦 Build

```bash
npm run build
```

## 🔧 Development

```bash
npm run dev
```

Generated by CodeCraft Frontend Generator.
"""
    
    # Create ZIP
    print(f"   📦 Creating ZIP file...")
    zip_buffer = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    for file_path, content in project_files.items():
        zip_buffer.writestr(file_path, content)
    zip_buffer.close()
    
    print(f"   ✅ Created: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")
    return output_path

def main():
    """Main function"""
    print("=" * 70)
    print("🚀 SOCIAL NETWORK - COMPLETE APP GENERATOR")
    print("=" * 70)
    print(f"\n📱 Generating all {len(SCREENS)} screens into ONE complete app...\n")
    
    # Check server
    try:
        health = requests.get(f"{SERVER_URL}/frontend/health", timeout=5)
        if health.status_code != 200:
            print(f"❌ Server health check failed: {health.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running: python3 main.py")
        return
    
    # Generate each screen
    screen_results = []
    for i, screen in enumerate(SCREENS, 1):
        print(f"[{i}/{len(SCREENS)}] ", end="")
        image_path = screen['image']
        result = generate_screen_component(image_path, screen)
        screen_results.append(result)
    
    # Create combined project
    successful_screens = [r for r in screen_results if r is not None]
    
    if not successful_screens:
        print(f"\n❌ No screens were generated successfully")
        print("   Please check that:")
        print("   1. Image files are in the current directory")
        print("   2. Server is running at http://localhost:8000")
        print("   3. GEMINI_API_KEY is set")
        return
    
    print(f"\n✅ Successfully generated {len(successful_screens)}/{len(SCREENS)} screens")
    
    output_zip = create_complete_project(screen_results)
    
    if output_zip:
        print(f"\n" + "=" * 70)
        print(f"🎉 COMPLETE APP GENERATED!")
        print("=" * 70)
        print(f"\n📦 Output: {output_zip}")
        print(f"📊 Screens: {len(successful_screens)}/{len(SCREENS)}")
        print(f"\n🚀 To use:")
        print(f"   1. Extract: unzip {output_zip} -d social_network_app")
        print(f"   2. Install: cd social_network_app && npm install")
        print(f"   3. Run: npm run dev")
        print(f"   4. Open: http://localhost:3000")
        print(f"\n💡 All screens are connected via React Router!")
        print(f"   Use the navigation bar to switch between screens.")

if __name__ == "__main__":
    main()

