#!/usr/bin/env python3
"""
Quick test script - Simple health check and basic endpoint test
"""

import requests
import json

def quick_test():
    """Quick health check"""
    print("🔍 Quick Health Check\n")
    
    # Test FastAPI
    try:
        r = requests.get("http://localhost:8002/", timeout=5)
        print(f"✅ FastAPI (8002): {r.status_code} - {r.json()['message']}")
    except Exception as e:
        print(f"❌ FastAPI (8002): {e}")
    
    # Test Proxy
    try:
        r = requests.get("http://localhost:4002/", timeout=5)
        print(f"✅ Proxy (4002): {r.status_code}")
    except requests.exceptions.HTTPError:
        print("⚠️  Proxy (4002): No root endpoint (expected)")
    except Exception as e:
        print(f"❌ Proxy (4002): {e}")
    
    # Test Ollama
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = r.json().get("models", [])
        qwen_models = [m["name"] for m in models if "qwen" in m["name"].lower()]
        print(f"✅ Ollama (11434): Running - Found {len(qwen_models)} Qwen model(s)")
        if qwen_models:
            print(f"   Models: {', '.join(qwen_models)}")
    except Exception as e:
        print(f"❌ Ollama (11434): {e}")
    
    print("\n💡 To run full tests: python3 test_codecraft_api.py")

if __name__ == "__main__":
    quick_test()
