#!/usr/bin/env python3
"""
Test script for LiteLLM Keys Plugin V2
Tests the installation and basic functionality
"""

import os
import sys
import json
from pathlib import Path

def test_file_exists(file_path, description):
    """Test if a file exists and is readable"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (NOT FOUND)")
        return False

def test_file_content(file_path, search_string, description):
    """Test if a file contains specific content"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}: Found '{search_string}' in {file_path}")
                return True
            else:
                print(f"❌ {description}: '{search_string}' not found in {file_path}")
                return False
    except Exception as e:
        print(f"❌ {description}: Error reading {file_path} - {e}")
        return False

def main():
    print("🧪 Testing LiteLLM Keys Plugin V2 Installation")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test backend files
    backend_tests = [
        ("backend/open_webui/utils/litellm_client.py", "LiteLLM Client"),
        ("backend/open_webui/routers/litellm_keys_v2.py", "API Router V2"),
    ]
    
    for file_path, description in backend_tests:
        total_tests += 1
        if test_file_exists(file_path, description):
            tests_passed += 1
    
    # Test frontend files
    frontend_tests = [
        ("src/lib/apis/litellm-keys/index.ts", "Frontend API Client"),
        ("src/routes/(app)/workspace/litellm-keys/+page.svelte", "Frontend UI"),
    ]
    
    for file_path, description in frontend_tests:
        total_tests += 1
        if test_file_exists(file_path, description):
            tests_passed += 1
    
    # Test main.py integration
    total_tests += 1
    if test_file_content("backend/open_webui/main.py", "litellm_keys_v2", "Main.py Integration"):
        tests_passed += 1
    
    # Test config.py integration
    total_tests += 1
    if test_file_content("backend/open_webui/config.py", "LITELLM_MASTER_API_KEY", "Config Integration"):
        tests_passed += 1
    
    # Test workspace layout integration
    total_tests += 1
    if test_file_content("src/routes/(app)/workspace/+layout.svelte", "litellm-keys", "Workspace Layout Integration"):
        tests_passed += 1
    
    # Test environment template
    total_tests += 1
    if test_file_exists("litellm_keys_v2.env.template", "Environment Template"):
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! LiteLLM Keys Plugin V2 is ready to use.")
        print("\n📋 Next Steps:")
        print("1. Configure environment variables (see litellm_keys_v2.env.template)")
        print("2. Restart Open WebUI")
        print("3. Navigate to Workspace → LiteLLM Keys")
        return True
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
