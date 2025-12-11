#!/usr/bin/env python3
"""
Test script for multi-screen frontend generation using LangGraph agent
Tests with torrent app screens
"""

import asyncio
import base64
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from frontend_generator.langgraph_agent import LangGraphFrontendAgent

async def test_multi_screen_agent():
    """Test the multi-screen agent with torrent app screens"""
    
    # Get Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        return False
    
    print("🚀 Testing Multi-Screen LangGraph Agent")
    print("=" * 60)
    
    # Initialize agent
    print("\n📦 Initializing LangGraph agent...")
    agent = LangGraphFrontendAgent(gemini_api_key)
    print("✅ Agent initialized")
    
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
    screen_names = []
    
    for idx, screen_file in enumerate(screen_files, 1):
        print(f"\n📖 Reading screen {idx}: {screen_file.name}")
        with open(screen_file, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            screen_images.append(image_data)
            # Generate screen name from filename
            screen_name = screen_file.stem.replace("Screenshot ", "").replace(" at ", "_").replace(" ", "_")
            screen_names.append(screen_name)
            print(f"   ✅ Encoded: {len(image_data)} chars")
    
    # Define routes
    screen_routes = ["/", "/torrents", "/settings"]  # Adjust based on your screens
    
    print(f"\n🔧 Generating multi-screen React app...")
    print(f"   Project: torrent-app")
    print(f"   Screens: {len(screen_images)}")
    print(f"   Names: {screen_names}")
    print(f"   Routes: {screen_routes}")
    
    try:
        # Call the agent
        result = await agent.process_multi_ui_to_react(
            screen_images=screen_images,
            screen_names=screen_names,
            screen_routes=screen_routes,
            project_name="torrent-app",
            additional_context="Generate a complete React app that matches the UI design exactly. Ensure all elements are properly aligned and the layout matches the design pixel-perfectly. This is a torrent application with multiple screens.",
            include_typescript=True,
            styling_approach="css-modules"
        )
        
        if not result.get("success"):
            print(f"\n❌ Generation failed: {result.get('error_message', 'Unknown error')}")
            return False
        
        print(f"\n✅ Multi-screen project generated successfully!")
        print(f"\n📊 Project Stats:")
        print(f"   - Project name: {result.get('project_name', 'N/A')}")
        print(f"   - Screens count: {result.get('screens_count', 0)}")
        print(f"   - Files count: {result.get('files_count', 0)}")
        
        # Check screen results
        screen_results = result.get('screen_results', [])
        if screen_results:
            print(f"\n📱 Screen Results:")
            for screen in screen_results:
                print(f"   - {screen.get('screen_name')}: {screen.get('files_count', 0)} files, route: {screen.get('screen_route', 'N/A')}")
        
        # Check for key files
        project_files = result.get('project_files', {})
        print(f"\n📁 Key Files Generated:")
        key_files = [
            "src/App.tsx",
            "package.json",
            "index.html",
            "vite.config.ts"
        ]
        for key_file in key_files:
            if key_file in project_files:
                print(f"   ✅ {key_file}")
            else:
                print(f"   ❌ {key_file} (missing)")
        
        # Check for screen components
        screen_components = [f for f in project_files.keys() if "screens/" in f]
        print(f"\n📱 Screen Components: {len(screen_components)}")
        for comp in screen_components[:10]:  # Show first 10
            print(f"   - {comp}")
        
        # Check App.tsx for React Router
        if "src/App.tsx" in project_files:
            app_content = project_files["src/App.tsx"]
            if "react-router-dom" in app_content and "BrowserRouter" in app_content:
                print(f"\n✅ React Router integration found in App.tsx")
            else:
                print(f"\n⚠️  React Router might not be properly integrated")
        
        # Check package.json for react-router-dom
        if "package.json" in project_files:
            package_json = project_files["package.json"]
            if "react-router-dom" in package_json:
                print(f"✅ react-router-dom dependency found in package.json")
            else:
                print(f"⚠️  react-router-dom dependency missing in package.json")
        
        print(f"\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error during generation:")
        print(f"   {str(e)}")
        print(f"\nTraceback:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_multi_screen_agent())
    sys.exit(0 if success else 1)

