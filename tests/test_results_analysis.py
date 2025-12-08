#!/usr/bin/env python3
"""
Test Results Analysis Script
Analyzes test results and generates a comprehensive report
"""
import subprocess
import sys
import re
from pathlib import Path

def run_tests():
    """Run all tests and capture output"""
    print("=" * 70)
    print("Running All 108 Test Cases")
    print("=" * 70)
    print()
    
    # Check server status
    import requests
    server_running = False
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        server_running = response.status_code == 200
    except:
        pass
    
    if not server_running:
        print("⚠️  WARNING: Server is not running on localhost:8000")
        print("   Tests will be skipped. Start server with: python3 main.py")
        print()
    
    # Check API key
    import os
    api_key_set = os.getenv("GEMINI_API_KEY") is not None
    if not api_key_set:
        print("⚠️  WARNING: GEMINI_API_KEY not set")
        print("   Some tests will be skipped")
        print()
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-rs"],
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    
    # Parse results
    passed = len(re.findall(r'PASSED', output))
    failed = len(re.findall(r'FAILED', output))
    skipped = len(re.findall(r'SKIPPED', output))
    errors = len(re.findall(r'ERROR', output))
    
    # Extract skip reasons
    skip_reasons = {}
    for line in output.split('\n'):
        if 'SKIPPED' in line:
            if 'Server is not running' in line:
                skip_reasons['server_down'] = skip_reasons.get('server_down', 0) + 1
            elif 'GEMINI_API_KEY' in line or 'API key' in line:
                skip_reasons['no_api_key'] = skip_reasons.get('no_api_key', 0) + 1
            else:
                skip_reasons['other'] = skip_reasons.get('other', 0) + 1
    
    # Print summary
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"Total Tests: 108")
    print(f"✅ Passed:   {passed}")
    print(f"❌ Failed:   {failed}")
    print(f"⏭️  Skipped:  {skipped}")
    print(f"⚠️  Errors:   {errors}")
    print()
    
    if skip_reasons:
        print("Skip Reasons:")
        for reason, count in skip_reasons.items():
            if reason == 'server_down':
                print(f"  - Server not running: {count} tests")
            elif reason == 'no_api_key':
                print(f"  - API key not set: {count} tests")
            else:
                print(f"  - Other: {count} tests")
        print()
    
    # Print detailed output
    print("=" * 70)
    print("DETAILED OUTPUT")
    print("=" * 70)
    print(output)
    
    # Save to file
    with open("test_results_detailed.log", "w") as f:
        f.write(output)
    
    print()
    print("=" * 70)
    print(f"Detailed results saved to: test_results_detailed.log")
    print("=" * 70)
    
    return {
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'errors': errors,
        'skip_reasons': skip_reasons
    }

if __name__ == "__main__":
    results = run_tests()
    sys.exit(0 if results['failed'] == 0 and results['errors'] == 0 else 1)

