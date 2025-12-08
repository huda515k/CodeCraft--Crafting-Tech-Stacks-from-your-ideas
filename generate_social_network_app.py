#!/usr/bin/env python3
"""
Generate complete Social Network app with all 12 screens
Creates a single downloadable project with React Router for navigation
"""

import requests
import zipfile
import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple

SERVER_URL = "http://localhost:8000"

# All 12 screens with their descriptions
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

def generate_screen_component(image_path: str, screen_info: dict) -> Dict:
    """Generate React component for a single screen"""
    print(f"\n📱 Generating: {screen_info['display_name']}")
    
    if not os.path.exists(image_path):
        print(f"   ⚠️  Image not found: {image_path}")
        return None
    
    url = f"{SERVER_URL}/frontend/generate-react"
    
    context = f"""
Generate a complete React component for the {screen_info['display_name']} screen.

Design Requirements:
- Color scheme: Teal/turquoise (#00CED1 or similar), white (#FFFFFF), and yellow/gold (#FFD700 or similar)
- Mobile-first design (typical mobile screen dimensions)
- Include all UI elements exactly as shown: buttons, inputs, text, icons, images
- Match the layout structure precisely
- Use proper React component structure with TypeScript
- Component name should be: {screen_info['name']}

Screen Description:
{screen_info['description']}

Make sure all interactive elements (buttons, inputs, etc.) are properly styled and visible.
"""
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'include_typescript': 'true',
                'styling_approach': 'css-modules',
                'additional_context': context
            }
            
            print(f"   📤 Uploading to server...")
            response = requests.post(url, files=files, data=data, timeout=300)
            
            if response.status_code != 200:
                print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
                return None
            
            # Extract ZIP to temp directory
            temp_dir = tempfile.mkdtemp(prefix=f"screen_{screen_info['name']}_")
            zip_path = os.path.join(temp_dir, "screen.zip")
            
            with open(zip_path, 'wb') as zf:
                zf.write(response.content)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(temp_dir)
            
            print(f"   ✅ Generated successfully")
            return {
                'screen_info': screen_info,
                'temp_dir': temp_dir,
                'components': list(Path(temp_dir).rglob('*.tsx')),
                'css_files': list(Path(temp_dir).rglob('*.css'))
            }
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_multi_screen_project(screen_results: List[Dict], output_path: str = "social_network_app.zip"):
    """Combine all screens into a single project with React Router"""
    print(f"\n🔨 Creating multi-screen project...")
    
    # Create project structure
    project_files = {}
    
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
    
    # 5. Collect all components and CSS from generated screens
    all_components = {}
    all_css = {}
    screen_components = {}
    
    for result in screen_results:
        if not result:
            continue
        
        screen_name = result['screen_info']['name']
        temp_dir = result['temp_dir']
        
        # Find the main screen component
        src_dir = Path(temp_dir) / "src"
        if not src_dir.exists():
            continue
        
        # Get components
        for comp_file in (src_dir / "components").rglob("*.tsx"):
            rel_path = comp_file.relative_to(src_dir)
            with open(comp_file, 'r') as f:
                all_components[f"src/components/{rel_path}"] = f.read()
        
        # Get CSS files
        for css_file in src_dir.rglob("*.css"):
            rel_path = css_file.relative_to(src_dir)
            with open(css_file, 'r') as f:
                all_css[f"src/{rel_path}"] = f.read()
        
        # Find the main screen component (usually the root component)
        # We'll create screen wrapper components
        screen_components[screen_name] = result['screen_info']
    
    # Add all components and CSS
    project_files.update(all_components)
    project_files.update(all_css)
    
    # 6. Create screen wrapper components with routing
    routes = []
    imports = []
    
    for screen_name, screen_info in screen_components.items():
        # Create a simple wrapper that imports the main component
        # For now, we'll create placeholder screens that can be replaced
        route_path = screen_info['route']
        imports.append(f"import {screen_name} from './screens/{screen_name}';")
        routes.append(f'        <Route path="{route_path}" element={{<{screen_name} />}} />')
    
    # 7. Create App.tsx with React Router
    project_files["src/App.tsx"] = f"""import React from 'react';
import {{ BrowserRouter, Routes, Route, Link }} from 'react-router-dom';
{chr(10).join(imports)}
import './index.css';

const App: React.FC = () => {{
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navigation">
          <Link to="/">Home</Link>
          <Link to="/signin">Sign In</Link>
          <Link to="/profile">Profile</Link>
          <Link to="/messages">Messages</Link>
        </nav>
        <Routes>
{chr(10).join(routes)}
        </Routes>
      </div>
    </BrowserRouter>
  );
}};

export default App;
"""
    
    # 8. Create screen components (placeholders that will be replaced with actual generated components)
    for screen_name, screen_info in screen_components.items():
        project_files[f"src/screens/{screen_name}.tsx"] = f"""import React from 'react';
import '../index.css';

const {screen_name}: React.FC = () => {{
  return (
    <div className="screen-container">
      <h1>{screen_info['display_name']}</h1>
      <p>This screen will be replaced with the generated component.</p>
      <p>Route: {screen_info['route']}</p>
    </div>
  );
}};

export default {screen_name};
"""
    
    # 9. index.tsx
    project_files["src/index.tsx"] = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    # 10. index.css
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
  font-family: 'Poppins', 'Montserrat', sans-serif;
}

#root {
  width: 100%;
  min-height: 100vh;
}

.app {
  width: 100%;
  min-height: 100vh;
}

.navigation {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background-color: #00CED1;
}

.navigation a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.navigation a:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.screen-container {
  padding: 2rem;
  min-height: calc(100vh - 60px);
}
"""
    
    # 11. README
    project_files["README.md"] = f"""# Social Network App

Complete React application with {len(screen_components)} screens.

## Screens

{chr(10).join([f"- **{info['display_name']}**: {info['route']}" for info in screen_components.values()])}

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
    
    # Create ZIP
    zip_buffer = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    for file_path, content in project_files.items():
        zip_buffer.writestr(file_path, content)
    zip_buffer.close()
    
    print(f"   ✅ Created: {output_path}")
    return output_path

def main():
    """Main function"""
    print("=" * 70)
    print("🚀 SOCIAL NETWORK APP GENERATOR")
    print("=" * 70)
    print(f"\n📱 Generating {len(SCREENS)} screens...")
    print("💡 Make sure all image files are in the current directory\n")
    
    # Generate each screen
    screen_results = []
    for screen in SCREENS:
        image_path = screen['image']
        result = generate_screen_component(image_path, screen)
        screen_results.append(result)
    
    # Create combined project
    successful_screens = [r for r in screen_results if r is not None]
    if successful_screens:
        print(f"\n✅ Successfully generated {len(successful_screens)}/{len(SCREENS)} screens")
        output_zip = create_multi_screen_project(successful_screens)
        print(f"\n🎉 Complete project ready: {output_zip}")
        print(f"   Extract and run: npm install && npm run dev")
    else:
        print("\n❌ No screens were generated successfully")
        print("   Please check that:")
        print("   1. Image files are in the current directory")
        print("   2. Server is running at http://localhost:8000")
        print("   3. GEMINI_API_KEY is set")

if __name__ == "__main__":
    main()

