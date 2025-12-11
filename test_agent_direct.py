#!/usr/bin/env python3
"""Test the agent directly"""
import asyncio
import base64
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from frontend_generator.langgraph_agent import LangGraphFrontendAgent

async def test_direct():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not set")
        return False
    
    print("🚀 Testing LangGraphFrontendAgent directly...")
    
    # Initialize agent
    agent = LangGraphFrontendAgent(gemini_api_key)
    print("✅ Agent initialized")
    
    # Check if method exists
    if hasattr(agent, 'process_multi_ui_to_react'):
        print("✅ process_multi_ui_to_react method exists")
    else:
        print("❌ process_multi_ui_to_react method NOT found")
        print(f"Available methods: {[m for m in dir(agent) if not m.startswith('_')]}")
        return False
    
    # Load one image for quick test
    torrent_dir = Path("sample ui images/torrent app")
    screen_files = sorted(list(torrent_dir.glob("*.png")))[:1]  # Just one for quick test
    
    if not screen_files:
        print("❌ No screens found")
        return False
    
    print(f"📱 Testing with 1 screen: {screen_files[0].name}")
    
    # Read image
    with open(screen_files[0], 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Test the method
    try:
        result = await agent.process_multi_ui_to_react(
            screen_images=[image_data],
            screen_names=["TestScreen"],
            screen_routes=["/"],
            project_name="test-direct",
            include_typescript=True,
            styling_approach="css-modules"
        )
        
        if result.get("success"):
            print("✅ Method call succeeded!")
            print(f"   Files generated: {result.get('files_count', 0)}")
            return True
        else:
            print(f"❌ Method call failed: {result.get('error_message', 'Unknown')}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_direct())

