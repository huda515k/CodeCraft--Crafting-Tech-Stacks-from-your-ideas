#!/usr/bin/env python3
"""
Test script to verify frontend generation accuracy
Tests on sample UI image and checks generated code
"""

import requests
import os
import zipfile
import io
import json
import tempfile
import shutil

BASE_URL = "http://localhost:8000"
SAMPLE_IMAGE = "sample ui images/screencapture-localhost-3002-chat-2025-12-03-23_12_57.png"

def test_frontend_generation():
    """Test frontend generation with sample UI image"""
    print("🧪 Testing Frontend Generation with Sample UI Image")
    print("=" * 60)
    
    # Check if image exists
    if not os.path.exists(SAMPLE_IMAGE):
        print(f"❌ Sample image not found: {SAMPLE_IMAGE}")
        return
    
    print(f"📸 Using image: {SAMPLE_IMAGE}")
    print(f"📏 Image size: {os.path.getsize(SAMPLE_IMAGE)} bytes")
    
    # Step 1: Analyze UI first
    print("\n📊 Step 1: Analyzing UI structure...")
    try:
        with open(SAMPLE_IMAGE, 'rb') as f:
            files = {'file': (os.path.basename(SAMPLE_IMAGE), f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=120
            )
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ UI Analysis successful!")
            print(f"   Project name: {analysis.get('ui_analysis', {}).get('project_name', 'N/A')}")
            print(f"   Components found: {analysis.get('components_count', 0)}")
            
            # Show component structure
            if 'ui_analysis' in analysis and 'components' in analysis['ui_analysis']:
                components = analysis['ui_analysis']['components']
                print(f"\n📋 Component Structure:")
                root_components = [c for c in components if not c.get('parent_id')]
                print(f"   Root components: {len(root_components)}")
                for comp in root_components[:5]:  # Show first 5
                    print(f"     - {comp.get('name')} ({comp.get('type')})")
                    if comp.get('children'):
                        print(f"       Children: {len(comp.get('children', []))}")
                
                # Check for key components
                component_names = [c.get('name', '').lower() for c in components]
                has_sidebar = any('sidebar' in name for name in component_names)
                has_chat = any('chat' in name for name in component_names)
                has_button = any('button' in name for name in component_names)
                has_input = any('input' in name for name in component_names)
                
                print(f"\n🔍 Key Components Detected:")
                print(f"   Sidebar: {'✅' if has_sidebar else '❌'}")
                print(f"   Chat area: {'✅' if has_chat else '❌'}")
                print(f"   Buttons: {'✅' if has_button else '❌'}")
                print(f"   Inputs: {'✅' if has_input else '❌'}")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   {response.text[:500]}")
            return
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return
    
    # Step 2: Generate React code
    print("\n🚀 Step 2: Generating React code...")
    try:
        with open(SAMPLE_IMAGE, 'rb') as f:
            files = {'file': (os.path.basename(SAMPLE_IMAGE), f, 'image/png')}
            data = {
                'framework': 'react',
                'styling_approach': 'css-modules',
                'include_typescript': 'true'
            }
            response = requests.post(
                f"{BASE_URL}/frontend/generate-react",
                files=files,
                data=data,
                timeout=180
            )
        
        if response.status_code == 200:
            print("✅ React code generation successful!")
            print(f"📦 ZIP size: {len(response.content)} bytes")
            
            # Extract and analyze generated code
            print("\n📂 Step 3: Analyzing generated code...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                file_list = zip_file.namelist()
                print(f"   Files generated: {len(file_list)}")
                
                # Check for key files
                has_app = any('App.tsx' in f or 'App.jsx' in f for f in file_list)
                has_components = any('components/' in f for f in file_list)
                has_css = any('.css' in f for f in file_list)
                has_package = 'package.json' in file_list
                
                print(f"\n📄 Key Files:")
                print(f"   App component: {'✅' if has_app else '❌'}")
                print(f"   Components folder: {'✅' if has_components else '❌'}")
                print(f"   CSS files: {'✅' if has_css else '❌'}")
                print(f"   package.json: {'✅' if has_package else '❌'}")
                
                # Extract and examine App.tsx
                app_file = None
                for f in file_list:
                    if 'App.tsx' in f or 'App.jsx' in f:
                        app_file = f
                        break
                
                if app_file:
                    print(f"\n📝 Examining {app_file}...")
                    app_content = zip_file.read(app_file).decode('utf-8')
                    print(f"   Lines: {len(app_content.splitlines())}")
                    
                    # Check for component imports
                    import_count = app_content.count('import')
                    component_imports = [line for line in app_content.split('\n') if 'import' in line and 'components' in line]
                    print(f"   Component imports: {len(component_imports)}")
                    for imp in component_imports[:5]:
                        print(f"     {imp.strip()}")
                
                # Examine component files
                component_files = [f for f in file_list if 'components/' in f and ('.tsx' in f or '.jsx' in f)]
                print(f"\n🧩 Component Files: {len(component_files)}")
                for comp_file in component_files[:10]:
                    comp_name = comp_file.split('/')[-1]
                    print(f"   - {comp_name}")
                
                # Examine CSS files
                css_files = [f for f in file_list if '.css' in f]
                print(f"\n🎨 CSS Files: {len(css_files)}")
                for css_file in css_files[:5]:
                    css_content = zip_file.read(css_file).decode('utf-8')
                    # Check for key CSS properties
                    has_flex = 'display: flex' in css_content
                    has_colors = any(prop in css_content for prop in ['background-color', 'color:'])
                    has_dimensions = any(prop in css_content for prop in ['width:', 'height:'])
                    print(f"   - {css_file.split('/')[-1]}")
                    print(f"     Flex: {'✅' if has_flex else '❌'}, Colors: {'✅' if has_colors else '❌'}, Dimensions: {'✅' if has_dimensions else '❌'}")
                
                # Save to temp directory for inspection
                temp_dir = tempfile.mkdtemp(prefix="codecraft_test_")
                zip_file.extractall(temp_dir)
                print(f"\n💾 Extracted to: {temp_dir}")
                print(f"   You can inspect the generated code there")
                
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   {response.text[:1000]}")
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_generation()

