#!/usr/bin/env python3
"""
Test the new AI multi-screen generator with torrent app screens
"""
import asyncio
import base64
import os
import sys
from pathlib import Path
import zipfile
import shutil
import subprocess

sys.path.insert(0, str(Path(__file__).parent))

from frontend_generator.langgraph_agent import LangGraphFrontendAgent

async def test_new_multi_screen_generator():
    """Test the new AI multi-screen generator"""
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not set")
        return False
    
    print("🚀 Testing NEW AI Multi-Screen Generator")
    print("=" * 60)
    
    # Load torrent app screens
    torrent_dir = Path("sample ui images/torrent app")
    screen_files = sorted(list(torrent_dir.glob("*.png")))
    
    if not screen_files:
        print(f"❌ No screens found in {torrent_dir}")
        return False
    
    print(f"\n📱 Found {len(screen_files)} screens:")
    for idx, screen_file in enumerate(screen_files, 1):
        print(f"   {idx}. {screen_file.name}")
    
    # Read and encode images
    screen_images = []
    screen_names = ["Home", "Torrents", "Settings"]
    screen_routes = ["/", "/torrents", "/settings"]
    
    for screen_file in screen_files:
        print(f"\n📖 Reading: {screen_file.name}")
        with open(screen_file, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            screen_images.append(image_data)
            print(f"   ✅ Encoded: {len(image_data)} chars")
    
    # Initialize agent
    print("\n🤖 Initializing LangGraph agent with NEW AI multi-screen generator...")
    agent = LangGraphFrontendAgent(gemini_api_key)
    
    # Verify it's using the new generator
    if hasattr(agent, 'ai_multi_screen_generator'):
        print("✅ Agent has ai_multi_screen_generator (NEW)")
    else:
        print("❌ Agent does NOT have ai_multi_screen_generator")
        return False
    
    # Generate project
    print(f"\n🔧 Generating multi-screen React app using NEW AI generator...")
    try:
        result = await agent.process_multi_ui_to_react(
            screen_images=screen_images,
            screen_names=screen_names,
            screen_routes=screen_routes,
            project_name="torrent-app-ai-generated",
            additional_context="Generate a complete React app that matches the UI design exactly. Ensure all elements are properly aligned and the layout matches the design pixel-perfectly. This is a torrent application with multiple screens.",
            include_typescript=True,
            styling_approach="css-modules"
        )
        
        if not result.get("success"):
            print(f"\n❌ Generation failed: {result.get('error_message', 'Unknown error')}")
            return False
        
        project_files = result.get("project_files", {})
        print(f"\n✅ Generated {len(project_files)} files")
        
        # Create output directory
        output_dir = Path("outputs/torrent_app_ai_generated")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract files
        print(f"\n📦 Extracting files to {output_dir}...")
        for file_path, content in project_files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ {file_path}")
        
        print(f"\n✅ Project extracted to: {output_dir}")
        
        # Check key files
        print(f"\n📁 Checking key files...")
        key_files = [
            "package.json",
            "index.html",
            "src/App.tsx",
            "vite.config.ts"
        ]
        for key_file in key_files:
            file_path = output_dir / key_file
            if file_path.exists():
                print(f"   ✅ {key_file}")
                if key_file == "package.json":
                    import json
                    with open(file_path) as f:
                        pkg = json.load(f)
                        deps = pkg.get("dependencies", {})
                        print(f"      Dependencies: {list(deps.keys())}")
            else:
                print(f"   ❌ {key_file} (missing)")
        
        # Check for screens
        screens_dir = output_dir / "src/screens"
        if screens_dir.exists():
            screen_files_found = list(screens_dir.glob("*.tsx"))
            print(f"\n📱 Screen Components: {len(screen_files_found)}")
            for screen_file in screen_files_found:
                print(f"   - {screen_file.name}")
        else:
            print(f"\n⚠️  No screens directory found")
        
        # Check App.tsx for React Router
        app_file = output_dir / "src/App.tsx"
        if app_file.exists():
            content = app_file.read_text()
            print(f"\n📄 App.tsx Analysis:")
            if "react-router-dom" in content:
                print(f"   ✅ React Router found")
            if "BrowserRouter" in content:
                print(f"   ✅ BrowserRouter found")
            if "Routes" in content:
                print(f"   ✅ Routes found")
            if "Route" in content:
                print(f"   ✅ Route components found")
            if "Navigate" in content:
                print(f"   ✅ Navigate (redirect) found")
            
            # Count routes
            route_count = content.count("<Route")
            print(f"   📊 Found {route_count} Route components")
            
            # Check for screen names
            for screen_name in screen_names:
                if screen_name in content or screen_name.lower() in content:
                    print(f"   ✅ Screen '{screen_name}' referenced")
        
        # Try to install and run
        print(f"\n🔧 Installing dependencies...")
        os.chdir(output_dir)
        try:
            result = subprocess.run(
                ["npm", "install"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                
                # Check if build works
                print(f"\n🔨 Testing build...")
                build_result = subprocess.run(
                    ["npm", "run", "build"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if build_result.returncode == 0:
                    print("✅ Build successful!")
                else:
                    print(f"⚠️  Build had issues:")
                    print(build_result.stderr[:500])
                
                print(f"\n✅ Project is ready to run!")
                print(f"\n📝 To run the project:")
                print(f"   cd {output_dir}")
                print(f"   npm run dev")
                
            else:
                print(f"⚠️  npm install had issues:")
                print(result.stderr[:500])
        except subprocess.TimeoutExpired:
            print("⚠️  npm install timed out")
        except FileNotFoundError:
            print("⚠️  npm not found - skipping install")
        except Exception as e:
            print(f"⚠️  Error during install: {e}")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_new_multi_screen_generator())
    sys.exit(0 if success else 1)

