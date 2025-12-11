#!/usr/bin/env python3
"""
Test script for CodeCraft API endpoints
Tests both direct FastAPI backend (port 8002) and Node.js proxy (port 4002)
"""

import requests
import json
import time
import sys
from typing import Optional


# Configuration
FASTAPI_URL = "http://localhost:8002"
PROXY_URL = "http://localhost:4002"


def test_health_check():
    """Test root endpoint health check"""
    print("\n" + "="*60)
    print("🔍 Testing Health Check Endpoints")
    print("="*60)
    
    try:
        # Test FastAPI root
        print("\n1. Testing FastAPI root (port 8002)...")
        response = requests.get(f"{FASTAPI_URL}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200, "FastAPI health check failed"
        print("   ✅ FastAPI is healthy")
        
        # Test FastAPI docs
        print("\n2. Testing FastAPI docs endpoint...")
        response = requests.get(f"{FASTAPI_URL}/docs", timeout=5)
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200, "FastAPI docs not accessible"
        print("   ✅ FastAPI docs accessible")
        
        return True
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False


def test_streaming_endpoint(mode: str = "frontend", arch_type: str = "Monolith", use_proxy: bool = False):
    """
    Test the streaming generation endpoint
    
    Args:
        mode: "frontend", "backend", or "integration"
        arch_type: "Monolith" or "Microservices" (for backend mode)
        use_proxy: If True, use Node.js proxy (port 4002), else use FastAPI directly (port 8002)
    """
    print("\n" + "="*60)
    print(f"🔍 Testing Streaming Endpoint: mode={mode}, arch={arch_type}")
    print(f"   Using: {'Node.js Proxy (4002)' if use_proxy else 'FastAPI Direct (8002)'}")
    print("="*60)
    
    base_url = PROXY_URL if use_proxy else FASTAPI_URL
    endpoint = "/api/codecraft/stream" if use_proxy else "/api/generate/stream"
    
    # Simple test specs
    test_specs = {
        "frontend": "Create a simple React todo app with add, delete, and mark complete functionality",
        "backend": "Create a REST API for a blog with posts, comments, and user authentication",
        "integration": "Create a full-stack e-commerce app with product listing and cart"
    }
    
    specs = test_specs.get(mode, test_specs["frontend"])
    
    try:
        print(f"\n📤 Sending request to {base_url}{endpoint}")
        print(f"   Specs: {specs[:50]}...")
        
        # Prepare form data
        data = {
            "specs": specs,
            "mode": mode,
            "arch_type": arch_type
        }
        
        # Make streaming request
        response = requests.post(
            f"{base_url}{endpoint}",
            data=data,
            stream=True,
            timeout=120  # 2 minutes timeout for generation
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Request failed: {response.text[:200]}")
            return False
        
        print("\n📥 Streaming response:")
        print("-" * 60)
        
        chunk_count = 0
        total_chars = 0
        stream_end = False
        zip_link = None
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                chunk_count += 1
                total_chars += len(line)
                
                # Check for special markers
                if "__STREAM_END__" in line:
                    stream_end = True
                    print("\n✅ Stream completed successfully")
                    break
                
                if "__ZIP_LINK__" in line:
                    # Extract ZIP link JSON
                    try:
                        json_str = line.split("__ZIP_LINK__")[1].strip()
                        zip_data = json.loads(json_str)
                        zip_link = zip_data.get("download_url")
                        print(f"\n📦 ZIP Download Link: {zip_link}")
                    except:
                        pass
                
                # Print first 10 chunks, then show progress
                if chunk_count <= 10:
                    print(line[:100] + ("..." if len(line) > 100 else ""))
                elif chunk_count == 11:
                    print("   ... (streaming continues) ...")
        
        print("-" * 60)
        print(f"\n📊 Stream Statistics:")
        print(f"   Chunks received: {chunk_count}")
        print(f"   Total characters: {total_chars}")
        print(f"   Stream ended: {stream_end}")
        
        if zip_link:
            print(f"   ✅ ZIP file available at: {zip_link}")
        
        return stream_end and chunk_count > 0
        
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out (generation may take longer)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_download_endpoint(filename: Optional[str] = None):
    """Test ZIP download endpoint (requires a valid filename from a previous generation)"""
    print("\n" + "="*60)
    print("🔍 Testing Download Endpoint")
    print("="*60)
    
    if not filename:
        print("   ⚠️  No filename provided. Skipping download test.")
        print("   💡 Run a generation test first to get a ZIP filename")
        return True
    
    try:
        print(f"\n📥 Testing download: {filename}")
        
        # Test both endpoints
        for base_url, name in [(FASTAPI_URL, "FastAPI"), (PROXY_URL, "Proxy")]:
            endpoint = f"{base_url}/api/download/{filename}"
            print(f"\n   Testing {name} endpoint: {endpoint}")
            
            response = requests.get(endpoint, stream=True, timeout=30)
            
            if response.status_code == 200:
                content_length = response.headers.get('Content-Length', 'unknown')
                print(f"   ✅ Download successful (Size: {content_length} bytes)")
                return True
            elif response.status_code == 404:
                print(f"   ⚠️  File not found (this is expected if no generation has run)")
            else:
                print(f"   ❌ Download failed: {response.status_code}")
        
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def run_all_tests():
    """Run comprehensive test suite"""
    print("\n" + "🚀"*30)
    print("CodeCraft API Test Suite")
    print("🚀"*30)
    
    results = {
        "health_check": False,
        "frontend_stream": False,
        "backend_stream": False,
        "integration_stream": False,
    }
    
    # 1. Health checks
    results["health_check"] = test_health_check()
    
    if not results["health_check"]:
        print("\n❌ Health checks failed. Please ensure services are running:")
        print("   - FastAPI: http://localhost:8002")
        print("   - Node.js Proxy: http://localhost:4002")
        print("   - Ollama: http://localhost:11434")
        return results
    
    # 2. Test streaming endpoints (using proxy)
    print("\n\n" + "⚠️ " * 20)
    print("NOTE: Streaming tests will make actual API calls to Ollama")
    print("      This may take several minutes and consume resources")
    print("⚠️ " * 20)
    
    user_input = input("\nContinue with streaming tests? (y/n): ").strip().lower()
    if user_input != 'y':
        print("Skipping streaming tests")
        return results
    
    # Test frontend generation
    print("\n\n🧪 Testing Frontend Generation...")
    results["frontend_stream"] = test_streaming_endpoint(
        mode="frontend",
        use_proxy=True  # Test through proxy
    )
    time.sleep(2)  # Brief pause between tests
    
    # Test backend generation
    print("\n\n🧪 Testing Backend Generation...")
    results["backend_stream"] = test_streaming_endpoint(
        mode="backend",
        arch_type="Monolith",
        use_proxy=True
    )
    time.sleep(2)
    
    # Test integration (optional - can be slow)
    print("\n\n🧪 Testing Integration Generation...")
    user_input = input("Test integration mode? (y/n): ").strip().lower()
    if user_input == 'y':
        results["integration_stream"] = test_streaming_endpoint(
            mode="integration",
            use_proxy=True
        )
    
    # Summary
    print("\n\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name:30s} {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n   Total: {passed}/{total} tests passed")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CodeCraft API endpoints")
    parser.add_argument("--mode", choices=["frontend", "backend", "integration"], 
                       help="Test specific mode only")
    parser.add_argument("--arch", choices=["Monolith", "Microservices"], 
                       default="Monolith", help="Architecture type (for backend)")
    parser.add_argument("--direct", action="store_true", 
                       help="Use FastAPI directly instead of proxy")
    parser.add_argument("--health-only", action="store_true",
                       help="Only run health checks")
    
    args = parser.parse_args()
    
    if args.health_only:
        test_health_check()
    elif args.mode:
        test_streaming_endpoint(mode=args.mode, arch_type=args.arch, use_proxy=not args.direct)
    else:
        run_all_tests()
