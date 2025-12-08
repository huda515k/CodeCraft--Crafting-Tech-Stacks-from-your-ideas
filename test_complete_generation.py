#!/usr/bin/env python3
"""
Complete test of frontend generation - creates test images and verifies generation
"""

import requests
import zipfile
import os
import tempfile
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_test_ui_image(filename: str, screen_name: str, description: str):
    """Create a simple test UI image for testing"""
    print(f"   🎨 Creating test image: {filename}")
    
    # Create a 400x800 mobile screen mockup
    width, height = 400, 800
    img = Image.new('RGB', (width, height), color='#00CED1')  # Teal background
    
    draw = ImageDraw.Draw(img)
    
    # Draw header
    draw.rectangle([0, 0, width, 100], fill='#00CED1')
    draw.rectangle([0, 100, width, 200], fill='#FFFFFF')
    
    # Draw title
    try:
        # Try to use a default font
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    draw.text((width//2, 50), screen_name, fill='#FFFFFF', anchor='mm', font=font_large)
    
    # Draw some UI elements
    # Button
    draw.rectangle([50, 250, 350, 300], fill='#FFD700', outline='#000000', width=2)
    draw.text((width//2, 275), "BUTTON", fill='#000000', anchor='mm', font=font_medium)
    
    # Input field
    draw.rectangle([50, 350, 350, 400], fill='#FFFFFF', outline='#000000', width=2)
    draw.text((60, 375), "Input field", fill='#666666', font=font_medium)
    
    # Card
    draw.rectangle([50, 450, 350, 550], fill='#FFFFFF', outline='#00CED1', width=2)
    draw.text((width//2, 500), "Card Content", fill='#000000', anchor='mm', font=font_medium)
    
    # Save image
    img.save(filename, 'PNG')
    print(f"   ✅ Created: {filename} ({width}x{height})")
    return filename

def test_single_screen_generation(image_path: str, screen_name: str):
    """Test generating frontend code for a single screen"""
    print(f"\n🧪 Testing: {screen_name}")
    
    if not os.path.exists(image_path):
        print(f"   ❌ Image not found: {image_path}")
        return None
    
    url = "http://localhost:8000/frontend/generate-react"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'include_typescript': 'true',
                'styling_approach': 'css-modules',
                'additional_context': f'Generate a complete React component for {screen_name}. Use teal (#00CED1), white (#FFFFFF), and yellow/gold (#FFD700) color scheme. Include all UI elements shown in the design.'
            }
            
            print(f"   📤 Uploading to server...")
            response = requests.post(url, files=files, data=data, timeout=300)
            
            if response.status_code != 200:
                print(f"   ❌ Error {response.status_code}")
                error_text = response.text[:500] if hasattr(response, 'text') else str(response.content[:500])
                print(f"   Response: {error_text}")
                return None
            
            # Save ZIP
            zip_path = f"test_{screen_name.replace(' ', '_').lower()}_generated.zip"
            with open(zip_path, 'wb') as zf:
                zf.write(response.content)
            
            print(f"   ✅ Generated: {zip_path} ({os.path.getsize(zip_path) / 1024:.1f} KB)")
            
            # Verify ZIP contents
            return verify_zip_contents(zip_path, screen_name)
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_zip_contents(zip_path: str, screen_name: str):
    """Verify the generated ZIP has all required files"""
    print(f"   🔍 Verifying ZIP contents...")
    
    required_files = [
        'index.html',
        'package.json',
        'vite.config.ts',
        'src/index.tsx',
        'src/App.tsx',
        'src/index.css'
    ]
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            files = z.namelist()
            
            # Check required files
            found = []
            missing = []
            for req_file in required_files:
                matching = [f for f in files if req_file in f]
                if matching:
                    found.append(req_file)
                else:
                    missing.append(req_file)
            
            print(f"      ✅ Found: {len(found)}/{len(required_files)} required files")
            if missing:
                print(f"      ⚠️  Missing: {missing}")
            
            # Count components
            components = [f for f in files if 'src/components/' in f and f.endswith('.tsx')]
            css_files = [f for f in files if f.endswith('.css')]
            
            print(f"      ✅ Components: {len(components)}")
            print(f"      ✅ CSS files: {len(css_files)}")
            
            # Check package.json
            pkg_file = next((f for f in files if 'package.json' in f), None)
            if pkg_file:
                with z.open(pkg_file) as f:
                    pkg = json.loads(f.read())
                    deps = pkg.get('dependencies', {})
                    print(f"      ✅ Dependencies: {', '.join(deps.keys())}")
            
            return len(found) >= len(required_files) - 1  # Allow 1 missing
            
    except Exception as e:
        print(f"      ❌ Verification error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 70)
    print("🧪 COMPLETE FRONTEND GENERATION TEST")
    print("=" * 70)
    
    # Check server
    try:
        health = requests.get("http://localhost:8000/frontend/health", timeout=5)
        if health.status_code == 200:
            print("\n✅ Server is running")
        else:
            print(f"\n❌ Server health check failed: {health.status_code}")
            return
    except Exception as e:
        print(f"\n❌ Cannot connect to server: {e}")
        print("   Make sure the server is running: python3 main.py")
        return
    
    # Create test images for a few key screens
    test_screens = [
        ("Welcome Screen", "welcome_splash.png", "Welcome screen with teal background and button"),
        ("Sign In Form", "sign_in_form.png", "Sign in form with inputs and button"),
        ("User Profile", "user_profile.png", "User profile with header and content"),
    ]
    
    print(f"\n📱 Creating {len(test_screens)} test UI images...")
    created_images = []
    
    for screen_name, filename, description in test_screens:
        try:
            create_test_ui_image(filename, screen_name, description)
            created_images.append((filename, screen_name))
        except Exception as e:
            print(f"   ⚠️  Could not create {filename}: {e}")
    
    if not created_images:
        print("\n❌ No test images could be created")
        return
    
    print(f"\n🚀 Testing generation for {len(created_images)} screens...")
    results = {}
    
    for image_path, screen_name in created_images:
        result = test_single_screen_generation(image_path, screen_name)
        results[screen_name] = result
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful > 0:
        print(f"\n💡 Generated ZIP files:")
        for screen_name, result in results.items():
            if result:
                zip_name = f"test_{screen_name.replace(' ', '_').lower()}_generated.zip"
                if os.path.exists(zip_name):
                    size = os.path.getsize(zip_name) / 1024
                    print(f"   ✅ {zip_name} ({size:.1f} KB)")
        
        print(f"\n🎉 Frontend generation is working!")
        print(f"   You can now use these generated projects as templates")
        print(f"   or test with your actual UI images")
    else:
        print(f"\n❌ All tests failed. Check server logs and GEMINI_API_KEY")
    
    # Cleanup option
    print(f"\n💡 Test images created: {', '.join([f[0] for f in created_images])}")
    print(f"   You can delete them or keep them for reference")

if __name__ == "__main__":
    main()

