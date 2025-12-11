#!/usr/bin/env python3
"""Test the endpoint directly"""
import requests
import base64
from pathlib import Path

def test_endpoint():
    url = "http://localhost:8000/frontend/agent/generate-multi-screen"
    
    # Load torrent screens
    torrent_dir = Path("sample ui images/torrent app")
    screen_files = sorted(list(torrent_dir.glob("*.png")))
    
    if not screen_files:
        print("❌ No screens found")
        return
    
    print(f"📱 Found {len(screen_files)} screens")
    
    # Prepare files
    files = []
    for screen_file in screen_files:
        files.append(('files', (screen_file.name, open(screen_file, 'rb'), 'image/png')))
    
    # Test with only 1 screen name (should auto-generate)
    data = {
        'screen_names': 'Home',  # Only 1 name for 3 files
        'screen_routes': '/,/torrents,/settings',
        'project_name': 'torrent-test',
        'additional_context': 'Generate exact UI matching code',
        'framework': 'react',
        'styling_approach': 'css-modules',
        'include_typescript': 'true'
    }
    
    print(f"\n🧪 Testing endpoint with 1 screen name for {len(screen_files)} files...")
    print(f"   Expected: Should auto-generate Screen2, Screen3")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=300)
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Generating ZIP...")
            # Save ZIP
            zip_path = Path("outputs/test_multi_screen.zip")
            zip_path.parent.mkdir(exist_ok=True)
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ ZIP saved to: {zip_path}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            # Check if it's the screen names error
            if "Number of screen names" in response.text:
                print("\n❌ Still getting screen names validation error!")
                print("   Server might be running old code")
            else:
                print(f"\n⚠️  Different error (might be API quota or other issue)")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
    finally:
        # Close files
        for _, file_tuple in files:
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

if __name__ == "__main__":
    test_endpoint()

