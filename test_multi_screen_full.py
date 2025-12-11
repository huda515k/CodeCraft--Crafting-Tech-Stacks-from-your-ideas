#!/usr/bin/env python3
"""Test multi-screen generation with all screen names provided"""
import requests
import zipfile
import io
from pathlib import Path

def test_with_all_names():
    url = "http://localhost:8000/frontend/agent/generate-multi-screen"
    
    # Load torrent screens
    torrent_dir = Path("sample ui images/torrent app")
    screen_files = sorted(list(torrent_dir.glob("*.png")))
    
    if not screen_files:
        print("❌ No screens found")
        return False
    
    print(f"📱 Found {len(screen_files)} screens")
    
    # Prepare files and names
    files = []
    screen_names = []
    for idx, screen_file in enumerate(screen_files, 1):
        files.append(('files', (screen_file.name, open(screen_file, 'rb'), 'image/png')))
        screen_names.append(f"Screen{idx}")
    
    # Provide all screen names
    data = {
        'screen_names': ','.join(screen_names),
        'screen_routes': '/,/screen2,/screen3',
        'project_name': 'torrent-test-full',
        'additional_context': 'Generate exact UI matching code',
        'framework': 'react',
        'styling_approach': 'css-modules',
        'include_typescript': 'true'
    }
    
    print(f"\n🧪 Testing with all {len(screen_names)} screen names provided...")
    print(f"   Names: {screen_names}")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=600)
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Saving ZIP...")
            zip_path = Path("outputs/torrent_test_full.zip")
            zip_path.parent.mkdir(exist_ok=True)
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ ZIP saved to: {zip_path}")
            
            # Extract and test
            print(f"\n📦 Extracting ZIP...")
            extract_dir = Path("outputs/torrent_test_full")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"✅ Extracted to: {extract_dir}")
            
            # Check for key files
            key_files = ['package.json', 'src/App.tsx', 'index.html']
            print(f"\n📁 Checking key files...")
            for key_file in key_files:
                file_path = extract_dir / key_file
                if file_path.exists():
                    print(f"   ✅ {key_file}")
                else:
                    print(f"   ❌ {key_file} missing")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close files
        for _, file_tuple in files:
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

if __name__ == "__main__":
    test_with_all_names()

