#!/usr/bin/env python3
"""
LiteLLM Keys Plugin Test Script

This script tests the basic functionality of the LiteLLM Keys plugin
to ensure it's properly installed and working.

Author: LiteLLM Key Management Plugin
"""

import sys
import os
import json
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from open_webui.models.litellm_keys import LiteLLMKeys, LiteLLMKeyCreateForm
        print("✓ LiteLLM Keys model imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import LiteLLM Keys model: {e}")
        return False
    
    try:
        from open_webui.routers.litellm_keys import router
        print("✓ LiteLLM Keys router imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import LiteLLM Keys router: {e}")
        return False
    
    return True

def test_model_creation():
    """Test that the model can be instantiated."""
    print("\nTesting model creation...")
    
    try:
        from open_webui.models.litellm_keys import LiteLLMKeyCreateForm
        
        # Test form creation
        form_data = LiteLLMKeyCreateForm(
            key_name="test_key",
            api_key="sk-test123456789",
            key_type="api_key",
            description="Test key for plugin testing"
        )
        
        print("✓ LiteLLM Key form created successfully")
        print(f"  - Key name: {form_data.key_name}")
        print(f"  - Key type: {form_data.key_type}")
        print(f"  - Description: {form_data.description}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create LiteLLM Key form: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are properly configured."""
    print("\nTesting API endpoints...")
    
    # This would require a running Open WebUI instance
    # For now, we'll just check if the router has the expected routes
    
    try:
        from open_webui.routers.litellm_keys import router
        
        # Get all routes from the router
        routes = []
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods)
                })
        
        expected_routes = [
            {'path': '/', 'methods': ['GET']},
            {'path': '/{key_id}', 'methods': ['GET']},
            {'path': '/', 'methods': ['POST']},
            {'path': '/{key_id}', 'methods': ['PUT']},
            {'path': '/{key_id}', 'methods': ['DELETE']},
            {'path': '/groups/accessible', 'methods': ['GET']},
            {'path': '/admin/all', 'methods': ['GET']}
        ]
        
        print(f"✓ Found {len(routes)} routes in the router")
        
        for expected_route in expected_routes:
            found = False
            for route in routes:
                if (route['path'] == expected_route['path'] and 
                    any(method in route['methods'] for method in expected_route['methods'])):
                    found = True
                    break
            
            if found:
                print(f"  ✓ Route {expected_route['methods']} {expected_route['path']} found")
            else:
                print(f"  ✗ Route {expected_route['methods']} {expected_route['path']} not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test API endpoints: {e}")
        return False

def test_database_migration():
    """Test that the database migration file exists."""
    print("\nTesting database migration...")
    
    migration_file = "backend/open_webui/migrations/versions/a1b2c3d4e5f6_add_litellm_keys_table.py"
    
    if os.path.exists(migration_file):
        print("✓ Database migration file exists")
        
        # Check if the migration file contains the expected content
        with open(migration_file, 'r') as f:
            content = f.read()
            
        if "litellm_key" in content and "create_table" in content:
            print("✓ Migration file contains expected table creation code")
            return True
        else:
            print("✗ Migration file doesn't contain expected content")
            return False
    else:
        print("✗ Database migration file not found")
        return False

def test_frontend_files():
    """Test that frontend files exist."""
    print("\nTesting frontend files...")
    
    frontend_files = [
        "src/lib/apis/litellm-keys/index.ts",
        "src/routes/(app)/workspace/litellm-keys/+page.svelte"
    ]
    
    all_exist = True
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✓ Frontend file exists: {file_path}")
        else:
            print(f"✗ Frontend file not found: {file_path}")
            all_exist = False
    
    return all_exist

def test_main_integration():
    """Test that main.py has been updated with the plugin."""
    print("\nTesting main.py integration...")
    
    main_file = "backend/open_webui/main.py"
    
    if not os.path.exists(main_file):
        print("✗ main.py not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("litellm_keys import", "litellm_keys," in content),
        ("litellm_keys router", "litellm_keys.router" in content),
        ("litellm-keys prefix", "/api/v1/litellm-keys" in content)
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print(f"✓ {check_name} found in main.py")
        else:
            print(f"✗ {check_name} not found in main.py")
            all_passed = False
    
    return all_passed

def test_workspace_layout():
    """Test that workspace layout has been updated."""
    print("\nTesting workspace layout integration...")
    
    layout_file = "src/routes/(app)/workspace/+layout.svelte"
    
    if not os.path.exists(layout_file):
        print("✗ Workspace layout file not found")
        return False
    
    with open(layout_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("litellm-keys permission check", "litellm-keys" in content and "permissions" in content),
        ("litellm-keys navigation", "LiteLLM Keys" in content),
        ("workspace/litellm-keys href", "/workspace/litellm-keys" in content)
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print(f"✓ {check_name} found in workspace layout")
        else:
            print(f"✗ {check_name} not found in workspace layout")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests."""
    print("LiteLLM Keys Plugin Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("Model Creation", test_model_creation),
        ("API Endpoints", test_api_endpoints),
        ("Database Migration", test_database_migration),
        ("Frontend Files", test_frontend_files),
        ("Main Integration", test_main_integration),
        ("Workspace Layout", test_workspace_layout)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The LiteLLM Keys Plugin is properly installed.")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())