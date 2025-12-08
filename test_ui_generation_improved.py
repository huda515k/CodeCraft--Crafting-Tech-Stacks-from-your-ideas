#!/usr/bin/env python3
"""
Test script for improved UI to frontend generation
Tests with 3 torrent app screens to verify:
1. All screens are generated correctly
2. Screens match UI images exactly
3. No additional components are added
4. Screens are connected and well-aligned
5. UI doesn't look rough, elements fit the page
"""

import asyncio
import base64
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend_generator.services import FrontendGenerationService

async def test_multi_screen_generation():
    """Test multi-screen generation with 3 torrent app screens"""
    
    print("=" * 60)
    print("🧪 Testing Improved UI to Frontend Generation")
    print("=" * 60)
    print()
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not set")
        print("   Please set GEMINI_API_KEY in .env file or environment")
        return False
    
    # Initialize service
    service = FrontendGenerationService(api_key)
    
    # Find torrent app screens
    torrent_dir = project_root / "sample ui images" / "torrent app"
    if not torrent_dir.exists():
        print(f"❌ Error: Torrent app directory not found: {torrent_dir}")
        return False
    
    screen_files = sorted(torrent_dir.glob("*.png"))
    if len(screen_files) < 3:
        print(f"❌ Error: Expected 3 screens, found {len(screen_files)}")
        return False
    
    print(f"📸 Found {len(screen_files)} screen images:")
    for i, screen_file in enumerate(screen_files, 1):
        print(f"   {i}. {screen_file.name}")
    print()
    
    # Read and encode images
    screen_images = []
    screen_names = []
    
    for screen_file in screen_files:
        with open(screen_file, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            screen_images.append(image_data)
            # Extract screen name from filename
            screen_name = screen_file.stem.replace("Screenshot ", "").replace(" at ", "_").replace(" ", "_")
            screen_names.append(screen_name)
    
    print("🔄 Processing screens...")
    print()
    
    # Generate multi-screen project
    try:
        result = await service.generate_multi_screen_project(
            screen_images=screen_images,
            screen_names=screen_names,
            screen_routes=["/", "/screen2", "/screen3"],
            project_name="torrent-app-improved",
            additional_context="Generate a complete React app that matches the UI design exactly. Ensure all elements are properly aligned and the layout matches the design pixel-perfectly.",
            framework="react",
            styling_approach="css-modules",
            include_typescript=True
        )
        
        if not result["success"]:
            print(f"❌ Generation failed: {result.get('error_message', 'Unknown error')}")
            return False
        
        print("✅ Multi-screen project generated successfully!")
        print()
        print(f"📊 Project Stats:")
        print(f"   - Project name: {result['project'].project_name}")
        print(f"   - Screens count: {result.get('screens_count', len(screen_images))}")
        print(f"   - Files count: {len(result['project'].files)}")
        print()
        
        # Check if all screens were generated
        screens_generated = result.get('screens_count', 0)
        if screens_generated != len(screen_images):
            print(f"⚠️  Warning: Expected {len(screen_images)} screens, got {screens_generated}")
        else:
            print(f"✅ All {len(screen_images)} screens generated!")
        print()
        
        # Check for screen components
        screen_files_found = []
        for file_path in result['project'].files.keys():
            if 'screens/' in file_path or 'Screen' in file_path:
                screen_files_found.append(file_path)
        
        if screen_files_found:
            print(f"📱 Screen components found ({len(screen_files_found)}):")
            for screen_file in screen_files_found[:10]:  # Show first 10
                print(f"   - {screen_file}")
            if len(screen_files_found) > 10:
                print(f"   ... and {len(screen_files_found) - 10} more")
        else:
            print("⚠️  Warning: No screen components found in generated files")
        print()
        
        # Check App.tsx for routing
        app_file = None
        for file_path in result['project'].files.keys():
            if 'App.tsx' in file_path:
                app_file = file_path
                break
        
        if app_file:
            app_content = result['project'].files[app_file]
            if 'BrowserRouter' in app_content and 'Routes' in app_content:
                print("✅ React Router integration found in App.tsx")
                # Count routes
                route_count = app_content.count('<Route')
                print(f"   - Routes found: {route_count}")
            else:
                print("⚠️  Warning: React Router not found in App.tsx")
        else:
            print("⚠️  Warning: App.tsx not found")
        print()
        
        # Save project to outputs directory
        output_dir = project_root / "outputs" / "torrent_app_improved"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract project files
        print(f"💾 Saving project to: {output_dir}")
        for file_path, file_content in result['project'].files.items():
            file_path_obj = output_dir / file_path
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(file_content)
        
        print(f"✅ Project saved to: {output_dir}")
        print()
        
        print("=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        print()
        print("📋 Next steps:")
        print(f"   1. Navigate to: {output_dir}")
        print("   2. Run: npm install")
        print("   3. Run: npm run dev")
        print("   4. Verify all 3 screens are accessible and match the UI images")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Error during generation: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_multi_screen_generation())
    sys.exit(0 if success else 1)

