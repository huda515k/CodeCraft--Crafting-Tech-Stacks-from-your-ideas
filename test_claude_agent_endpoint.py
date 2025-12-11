"""
Test script for the new /frontend/claudeAgent/Multiple_ui_to_React endpoint
"""
import requests
import os
from pathlib import Path

def test_claude_agent_endpoint():
    """Test the new Claude Agent multi-screen endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/frontend/claudeAgent/Multiple_ui_to_React"
    
    # Check if sample UI images exist
    sample_dir = Path("sample ui images/torrent app")
    if not sample_dir.exists():
        print(f"❌ Sample UI directory not found: {sample_dir}")
        print("   Please ensure sample UI images are available for testing")
        return False
    
    # Find image files
    image_files = list(sample_dir.glob("*.png")) + list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.jpeg"))
    
    if len(image_files) == 0:
        print(f"❌ No image files found in {sample_dir}")
        return False
    
    # Use first 3 images for testing
    test_images = image_files[:3]
    print(f"📸 Found {len(test_images)} test images: {[img.name for img in test_images]}")
    
    # Prepare form data
    files = []
    for img_file in test_images:
        files.append(('files', (img_file.name, open(img_file, 'rb'), 'image/png')))
    
    data = {
        'screen_names': ','.join([f"Screen{i+1}" for i in range(len(test_images))]),
        'project_name': 'test-claude-agent-app',
        'include_typescript': True,
        'styling_approach': 'css-modules'
    }
    
    print(f"\n🚀 Testing endpoint: {endpoint}")
    print(f"   Files: {len(files)} images")
    print(f"   Project: {data['project_name']}")
    
    try:
        response = requests.post(endpoint, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            # Check if it's a ZIP file
            content_type = response.headers.get('content-type', '')
            if 'zip' in content_type:
                output_file = f"test_output_{data['project_name']}.zip"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                file_size = os.path.getsize(output_file)
                print(f"\n✅ Success! ZIP file received: {output_file} ({file_size} bytes)")
                return True
            else:
                print(f"⚠️  Response is not a ZIP file. Content-Type: {content_type}")
                print(f"   Response preview: {response.text[:200]}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("   Make sure the server is running: python3 main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close file handles
        for _, file_tuple in files:
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

if __name__ == "__main__":
    print("=" * 60)
    print("Testing /frontend/claudeAgent/Multiple_ui_to_React endpoint")
    print("=" * 60)
    
    success = test_claude_agent_endpoint()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed. Check the errors above.")

