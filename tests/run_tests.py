#!/usr/bin/env python3
"""
Test runner script for CodeCraft test suite
Runs all 108 test cases and generates a summary report
"""
import sys
import subprocess
import os
from pathlib import Path

def main():
    """Run all tests and generate report"""
    print("=" * 70)
    print("CodeCraft Test Suite - Running All 108 Test Cases")
    print("=" * 70)
    print()
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  Warning: Server health check failed")
            print("   Make sure the server is running on localhost:8000")
            print()
    except:
        print("⚠️  Warning: Cannot connect to server")
        print("   Make sure the server is running: python3 main.py")
        print()
    
    # Check for Gemini CLI
    import subprocess
    cli_available = False
    for cmd in ["gemini", "gemini-cli"]:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                cli_available = True
                print(f"✅ Found Gemini CLI: {cmd}")
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    if not cli_available:
        print("⚠️  Warning: Gemini CLI not available")
        print("   Install with: npm install -g @google/generative-ai-cli && gemini-cli auth login")
        print("   Some tests may be skipped")
        print()
    
    # Run pytest
    test_dir = Path(__file__).parent
    os.chdir(test_dir.parent)
    
    print("Running tests...")
    print()
    
    # Run with verbose output and coverage
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes",
            "-x",  # Stop on first failure (remove for full run)
        ],
        cwd=test_dir.parent
    )
    
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Some tests failed (exit code: {result.returncode})")
    print("=" * 70)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

