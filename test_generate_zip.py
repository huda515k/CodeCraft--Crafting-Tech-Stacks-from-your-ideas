#!/usr/bin/env python3
"""Test generating zip using the non-agent endpoint"""
import requests
import zipfile
from pathlib import Path

def test_generate_zip():
    url = "http://localhost:8000/frontend/generate-multi-screen"
    
    # Load torrent screens
    torrent_dir = Path("sample ui images/torrent app")
    screen_files = sorted(list(torrent_dir.glob("*.png")))
    
    if not screen_files:
        print("❌ No screens found")
        return False
    
    print(f"📱 Found {len(screen_files)} screens")
    
    # Prepare files
    files = []
    screen_names = []
    for idx, screen_file in enumerate(screen_files, 1):
        files.append(('files', (screen_file.name, open(screen_file, 'rb'), 'image/png')))
        screen_names.append(f"Screen{idx}")
    
    # Use AI generation
    data = {
        'screen_names': ','.join(screen_names),
        'screen_routes': '/,/screen2,/screen3',
        'project_name': 'torrent-app-test',
        'additional_context': 'Generate exact UI matching code',
        'framework': 'react',
        'styling_approach': 'css-modules',
        'include_typescript': 'true',
        'use_ai': 'false'  # Don't use AI for now
    }
    
    print(f"\n🧪 Testing /frontend/generate-multi-screen with AI...")
    print(f"   Names: {screen_names}")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=600)
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Saving ZIP...")
            zip_path = Path("outputs/torrent_app_test_new.zip")
            zip_path.parent.mkdir(exist_ok=True)
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ ZIP saved to: {zip_path} ({len(response.content)} bytes)")
            
            # Extract and check
            print(f"\n📦 Extracting ZIP...")
            extract_dir = Path("outputs/torrent_app_test_new")
            if extract_dir.exists():
                import shutil
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"✅ Extracted to: {extract_dir}")
            
            # Check for key files
            key_files = ['package.json', 'src/App.tsx', 'index.html', 'vite.config.ts']
            print(f"\n📁 Checking key files...")
            all_exist = True
            for key_file in key_files:
                file_path = extract_dir / key_file
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"   ✅ {key_file} ({size} bytes)")
                else:
                    print(f"   ❌ {key_file} missing")
                    all_exist = False
            
            # List all files
            print(f"\n📂 All files in ZIP:")
            for file_path in sorted(extract_dir.rglob('*')):
                if file_path.is_file():
                    rel_path = file_path.relative_to(extract_dir)
                    print(f"   {rel_path}")
            
            if all_exist:
                print(f"\n✅ All key files present! Ready to test.")
                return extract_dir
            else:
                print(f"\n⚠️  Some files missing")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Close files
        for _, file_tuple in files:
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

if __name__ == "__main__":
    result = test_generate_zip()
    if result:
        print(f"\n✅ ZIP generated and extracted successfully!")
        print(f"   Location: {result}")
        print(f"\n🚀 To test, run:")
        print(f"   cd {result}")
        print(f"   npm install")
        print(f"   npm run dev")

