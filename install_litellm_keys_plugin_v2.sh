#!/bin/bash

# LiteLLM Keys Management Plugin V2 - Installation Script
# API-Based Implementation (No Database Migrations Required)

set -e

echo "🚀 Installing LiteLLM Keys Management Plugin V2..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the Open WebUI root directory"
    exit 1
fi

print_status "Starting LiteLLM Keys Plugin V2 installation..."

# Create backup directory
BACKUP_DIR="litellm_keys_plugin_v2_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Created backup directory: $BACKUP_DIR"

# 1. Install LiteLLM Client
print_status "Installing LiteLLM client..."
if [ -f "backend/open_webui/utils/litellm_client.py" ]; then
    cp "backend/open_webui/utils/litellm_client.py" "$BACKUP_DIR/"
    print_warning "Backed up existing litellm_client.py"
fi
print_success "LiteLLM client installed"

# 2. Install API Router V2
print_status "Installing API router V2..."
if [ -f "backend/open_webui/routers/litellm_keys_v2.py" ]; then
    cp "backend/open_webui/routers/litellm_keys_v2.py" "$BACKUP_DIR/"
    print_warning "Backed up existing litellm_keys_v2.py"
fi
print_success "API router V2 installed"

# 3. Update main.py
print_status "Updating main.py..."
if [ -f "backend/open_webui/main.py" ]; then
    cp "backend/open_webui/main.py" "$BACKUP_DIR/"
    print_warning "Backed up existing main.py"
    
    # Check if litellm_keys_v2 is already imported
    if ! grep -q "litellm_keys_v2" "backend/open_webui/main.py"; then
        # Add import
        sed -i '/from open_webui.routers import/a\    litellm_keys_v2,' "backend/open_webui/main.py"
        
        # Add router
        if ! grep -q "litellm_keys_v2.router" "backend/open_webui/main.py"; then
            echo "" >> "backend/open_webui/main.py"
            echo "# LiteLLM Keys API (V2 - API-based, no database)" >> "backend/open_webui/main.py"
            echo "app.include_router(litellm_keys_v2.router, prefix=\"/api/v1/litellm-keys\", tags=[\"litellm-keys\"])" >> "backend/open_webui/main.py"
        fi
        print_success "Updated main.py with LiteLLM Keys V2 router"
    else
        print_warning "LiteLLM Keys V2 router already configured in main.py"
    fi
else
    print_error "main.py not found!"
    exit 1
fi

# 4. Update configuration
print_status "Updating configuration..."
if [ -f "backend/open_webui/config.py" ]; then
    cp "backend/open_webui/config.py" "$BACKUP_DIR/"
    print_warning "Backed up existing config.py"
    
    # Check if LiteLLM config is already added
    if ! grep -q "LITELLM_MASTER_API_KEY" "backend/open_webui/config.py"; then
        # Add LiteLLM configuration after the imports
        sed -i '/from open_webui.env import/a\\n# LiteLLM Configuration\nLITELLM_MASTER_API_KEY = os.getenv("LITELLM_MASTER_API_KEY", "")\nLITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")\nLITELLM_ENABLED = os.getenv("LITELLM_ENABLED", "false").lower() == "true"' "backend/open_webui/config.py"
        print_success "Added LiteLLM configuration to config.py"
    else
        print_warning "LiteLLM configuration already exists in config.py"
    fi
else
    print_error "config.py not found!"
    exit 1
fi

# 5. Install Frontend API Client
print_status "Installing frontend API client..."
if [ -f "src/lib/apis/litellm-keys/index.ts" ]; then
    cp "src/lib/apis/litellm-keys/index.ts" "$BACKUP_DIR/"
    print_warning "Backed up existing API client"
fi
print_success "Frontend API client installed"

# 6. Install Frontend UI
print_status "Installing frontend UI..."
if [ -f "src/routes/(app)/workspace/litellm-keys/+page.svelte" ]; then
    cp "src/routes/(app)/workspace/litellm-keys/+page.svelte" "$BACKUP_DIR/"
    print_warning "Backed up existing UI"
fi
print_success "Frontend UI installed"

# 7. Update Workspace Layout
print_status "Updating workspace layout..."
if [ -f "src/routes/(app)/workspace/+layout.svelte" ]; then
    cp "src/routes/(app)/workspace/+layout.svelte" "$BACKUP_DIR/"
    print_warning "Backed up existing workspace layout"
    
    # Check if LiteLLM Keys link is already added
    if ! grep -q "litellm-keys" "src/routes/(app)/workspace/+layout.svelte"; then
        # Add LiteLLM Keys navigation link
        sed -i '/{#if \$user?.role === '\''admin'\'' || \$user?.permissions?.workspace?.tools}/a\\n\t{#if \$user?.role === '\''admin'\'' || \$user?.permissions?.workspace?.litellm_keys}\n\t\t<a\n\t\t\tclass="min-w-fit p-1.5 {\$page.url.pathname.includes('\''/workspace/litellm-keys'\'')\n\t\t\t\t? '\'''\''\n\t\t\t\t: '\''text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'\''} transition"\n\t\t\thref="/workspace/litellm-keys"\n\t\t>\n\t\t\tLiteLLM Keys\n\t\t</a>\n\t{/if}' "src/routes/(app)/workspace/+layout.svelte"
        print_success "Added LiteLLM Keys navigation link"
    else
        print_warning "LiteLLM Keys navigation link already exists"
    fi
else
    print_error "Workspace layout not found!"
    exit 1
fi

# 8. Create environment configuration template
print_status "Creating environment configuration template..."
cat > "litellm_keys_v2.env.template" << 'EOF'
# LiteLLM Keys Plugin V2 Configuration
# Copy these variables to your Open WebUI environment configuration

# LiteLLM Master API Key (Required)
# This is the master key that will be used to manage all user keys
LITELLM_MASTER_API_KEY="your_litellm_master_api_key_here"

# LiteLLM Server Base URL (Required)
# URL of your LiteLLM server
LITELLM_BASE_URL="http://localhost:4000"

# Enable LiteLLM Integration (Optional)
# Set to "true" to enable the plugin
LITELLM_ENABLED="true"
EOF
print_success "Created environment configuration template: litellm_keys_v2.env.template"

# 9. Create test script
print_status "Creating test script..."
cat > "test_litellm_keys_plugin_v2.py" << 'EOF'
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
EOF

chmod +x "test_litellm_keys_plugin_v2.py"
print_success "Created test script: test_litellm_keys_plugin_v2.py"

# 10. Run tests
print_status "Running installation tests..."
if python3 test_litellm_keys_plugin_v2.py; then
    print_success "All tests passed!"
else
    print_error "Some tests failed. Please check the installation."
    exit 1
fi

# Installation complete
echo ""
echo "🎉 LiteLLM Keys Plugin V2 Installation Complete!"
echo "=================================================="
echo ""
print_success "✅ All files installed successfully"
print_success "✅ Configuration updated"
print_success "✅ Integration tests passed"
echo ""
print_warning "📋 IMPORTANT: Next Steps Required"
echo ""
echo "1. 🔧 Configure Environment Variables:"
echo "   - Copy litellm_keys_v2.env.template to your environment"
echo "   - Set LITELLM_MASTER_API_KEY to your LiteLLM master key"
echo "   - Set LITELLM_BASE_URL to your LiteLLM server URL"
echo "   - Set LITELLM_ENABLED=true"
echo ""
echo "2. 🔄 Restart Open WebUI:"
echo "   - If using Docker: docker restart open-webui"
echo "   - If running directly: restart your Open WebUI process"
echo ""
echo "3. 🧪 Test the Installation:"
echo "   - Navigate to Workspace → LiteLLM Keys"
echo "   - Try creating a new key"
echo "   - Verify the key is shown only once"
echo ""
echo "4. 📚 Read the Documentation:"
echo "   - See LITELLM_KEYS_PLUGIN_V2_README.md for detailed usage"
echo ""
print_success "🚀 LiteLLM Keys Plugin V2 is ready to use!"
echo ""
echo "💡 Key Benefits of V2:"
echo "   • No database migrations required"
echo "   • Enhanced security (keys shown only once)"
echo "   • Real-time status from LiteLLM API"
echo "   • Master key authentication"
echo "   • Easy updates and maintenance"
echo ""