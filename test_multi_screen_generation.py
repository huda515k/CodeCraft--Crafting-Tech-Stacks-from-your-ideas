#!/usr/bin/env python3
"""
Test script for multi-screen frontend generation with torrent app screenshots
"""
import os
import sys
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app

# Load environment variables from .env file (override any existing env vars)
load_dotenv(override=True)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Get torrent app screenshots directory
TORRENT_APP_DIR = Path(__file__).parent / "sample ui images" / "torrent app"

async def test_multi_screen_generation():
    """Test multi-screen generation with torrent app screenshots"""
    
    # Check if screenshots exist
    if not TORRENT_APP_DIR.exists():
        print(f"❌ Torrent app directory not found: {TORRENT_APP_DIR}")
        return
    
    # Find all PNG files
    screenshot_files = sorted(list(TORRENT_APP_DIR.glob("*.png")))
    
    if not screenshot_files:
        print(f"❌ No PNG screenshots found in {TORRENT_APP_DIR}")
        return
    
    print(f"✅ Found {len(screenshot_files)} screenshots:")
    for i, file in enumerate(screenshot_files, 1):
        print(f"   {i}. {file.name}")
    
    # Create test client
    client = TestClient(app)
    
    # Prepare files for upload
    files = []
    screen_names = []
    screen_routes = []
    
    for i, screenshot_file in enumerate(screenshot_files, 1):
        # Generate screen name from filename
        screen_name = screenshot_file.stem.replace("Screenshot ", "").replace(" at ", "_").replace(" ", "_")
        # Clean up the name
        screen_name = "".join(c for c in screen_name if c.isalnum() or c in "_-")
        # Ensure it doesn't start with a number
        if screen_name and screen_name[0].isdigit():
            screen_name = f"Screen{screen_name}"
        if not screen_name:
            screen_name = f"Screen{i}"
        
        screen_names.append(screen_name)
        screen_routes.append(f"/{screen_name.lower()}")
        
        # Read file
        with open(screenshot_file, "rb") as f:
            files.append(("files", (screenshot_file.name, f.read(), "image/png")))
    
    print(f"\n📤 Uploading {len(files)} screenshots...")
    print(f"   Screen names: {screen_names}")
    print(f"   Routes: {screen_routes}")
    
    # Prepare form data
    form_data = {
        "screen_names": ",".join(screen_names),
        "screen_routes": ",".join(screen_routes),
        "project_name": "torrent-app",
        "additional_context": "This is a torrent application. Generate React components that match the exact colors, positioning, and layout of the provided screenshots. All screens should be connected via React Router.",
        "framework": "react",
        "styling_approach": "css-modules",
        "include_typescript": "true"
    }
    
    try:
        print("\n🚀 Calling /frontend/generate-multi-screen endpoint...")
        response = client.post(
            "/frontend/generate-multi-screen",
            files=files,
            data=form_data,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            # Save the ZIP file
            output_dir = Path(__file__).parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / "torrent_app_multi_screen.zip"
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            print(f"\n✅ Success! Generated ZIP file saved to: {output_file}")
            print(f"   File size: {len(response.content) / 1024 / 1024:.2f} MB")
            
            # Extract and show structure
            import zipfile
            with zipfile.ZipFile(output_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"\n📦 Generated project contains {len(file_list)} files:")
                print("   Key files:")
                for file in sorted(file_list)[:20]:  # Show first 20 files
                    print(f"      - {file}")
                if len(file_list) > 20:
                    print(f"      ... and {len(file_list) - 20} more files")
            
            print(f"\n📝 To test the generated app:")
            print(f"   1. Extract {output_file}")
            print(f"   2. cd into the extracted directory")
            print(f"   3. Run: npm install")
            print(f"   4. Run: npm run dev")
            print(f"   5. Open http://localhost:3000 in your browser")
            
        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Multi-Screen Frontend Generation")
    print("=" * 60)
    
    # Check for GEMINI_API_KEY
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not set in environment")
        print("   Please set it before running this test")
        sys.exit(1)
    
    asyncio.run(test_multi_screen_generation())

