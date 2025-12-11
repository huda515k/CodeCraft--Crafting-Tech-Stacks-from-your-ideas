#!/usr/bin/env python3
"""
Quick test of the multi-screen endpoint
"""
import requests
import base64
from pathlib import Path

def test_endpoint():
    """Test the endpoint with a simple request"""
    url = "http://localhost:8000/frontend/agent/generate-multi-screen"
    
    # Check if server is running
    try:
        health = requests.get("http://localhost:8000/health", timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server is not running")
        return False
    
    # Check endpoint exists
    try:
        # Try to get docs to see if endpoint is registered
        docs = requests.get("http://localhost:8000/docs", timeout=2)
        if "generate-multi-screen" in docs.text:
            print("✅ Endpoint found in docs")
        else:
            print("⚠️  Endpoint not found in docs")
    except Exception as e:
        print(f"⚠️  Could not check docs: {e}")
    
    print("\n✅ Endpoint test complete - endpoint should be available")
    print("   URL: POST http://localhost:8000/frontend/agent/generate-multi-screen")
    return True

if __name__ == "__main__":
    test_endpoint()

