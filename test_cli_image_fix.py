#!/usr/bin/env python3
"""
Quick test to verify CLI image processing fix
"""
import requests
import os
import sys

BASE_URL = "http://localhost:8000"

def create_test_image():
    """Create a simple test PNG image"""
    try:
        from PIL import Image
        import io
        
        # Create a simple 100x100 red image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    except ImportError:
        print("⚠️  PIL not available, using dummy image data")
        # Return minimal PNG header
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'

def test_cli_image_processing():
    """Test CLI image processing endpoint"""
    print("🧪 Testing CLI Image Processing Fix")
    print("=" * 60)
    
    # Create test image
    print("\n📸 Creating test image...")
    image_data = create_test_image()
    
    # Test the analyze-ui-only endpoint (uses image processing)
    print("\n🔍 Testing /frontend/analyze-ui-only endpoint...")
    print("   (This will use CLI if API quota is exhausted)")
    
    files = {
        'file': ('test.png', image_data, 'image/png')
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/frontend/analyze-ui-only",
            files=files,
            timeout=60
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! CLI image processing is working!")
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            
            # Check if it's a model not found error
            if "404" in response.text or "not found" in response.text.lower():
                print("\n⚠️  Model not found error detected!")
                print("   This suggests the model mapping needs to be fixed.")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CLI Image Processing Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"⚠️  Server health check failed: {health.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Is it running on http://localhost:8000?")
        sys.exit(1)
    
    success = test_cli_image_processing()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test PASSED - CLI image processing is working!")
    else:
        print("❌ Test FAILED - Check the error messages above")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
