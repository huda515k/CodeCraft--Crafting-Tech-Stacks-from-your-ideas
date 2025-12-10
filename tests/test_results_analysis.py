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
    
    # Check Gemini CLI
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
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    if not cli_available:
        print("⚠️  WARNING: Gemini CLI not available")
        print("   Install with: npm install -g @google/generative-ai-cli && gemini-cli auth login")
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
            elif 'Gemini CLI' in line or 'CLI not available' in line or 'GEMINI_API_KEY' in line or 'API key' in line:
                skip_reasons['no_gemini_cli'] = skip_reasons.get('no_gemini_cli', 0) + 1
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
            elif reason == 'no_gemini_cli':
                print(f"  - Gemini CLI not available: {count} tests")
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

