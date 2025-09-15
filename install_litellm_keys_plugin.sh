#!/bin/bash

# LiteLLM Keys Plugin Installation Script for Open WebUI
# This script helps install the LiteLLM Keys Management Plugin

set -e

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a directory exists
directory_exists() {
    [ -d "$1" ]
}

# Function to backup existing files
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        local backup="${file}.backup.$(date +%Y%m%d_%H%M%S)"
        print_warning "Backing up existing file: $file -> $backup"
        cp "$file" "$backup"
    fi
}

# Main installation function
install_plugin() {
    print_status "Starting LiteLLM Keys Plugin installation..."
    
    # Check if we're in the right directory
    if [ ! -f "backend/open_webui/main.py" ] || [ ! -f "src/routes/(app)/+layout.svelte" ]; then
        print_error "This script must be run from the Open WebUI root directory"
        print_error "Expected files not found: backend/open_webui/main.py, src/routes/(app)/+layout.svelte"
        exit 1
    fi
    
    print_status "Open WebUI installation detected"
    
    # Backup existing files
    print_status "Creating backups of existing files..."
    backup_file "backend/open_webui/main.py"
    backup_file "backend/open_webui/models/users.py"
    backup_file "src/routes/(app)/workspace/+layout.svelte"
    
    # Install backend components
    print_status "Installing backend components..."
    
    # Copy model file
    if [ -f "backend/open_webui/models/litellm_keys.py" ]; then
        print_success "Model file already exists: backend/open_webui/models/litellm_keys.py"
    else
        print_error "Model file not found: backend/open_webui/models/litellm_keys.py"
        print_error "Please ensure you have the plugin files in the correct location"
        exit 1
    fi
    
    # Copy router file
    if [ -f "backend/open_webui/routers/litellm_keys.py" ]; then
        print_success "Router file already exists: backend/open_webui/routers/litellm_keys.py"
    else
        print_error "Router file not found: backend/open_webui/routers/litellm_keys.py"
        print_error "Please ensure you have the plugin files in the correct location"
        exit 1
    fi
    
    # Copy migration file
    if [ -f "backend/open_webui/migrations/versions/a1b2c3d4e5f6_add_litellm_keys_table.py" ]; then
        print_success "Migration file already exists"
    else
        print_error "Migration file not found"
        print_error "Please ensure you have the migration file in the correct location"
        exit 1
    fi
    
    # Update main.py
    print_status "Updating main.py..."
    if grep -q "litellm_keys" backend/open_webui/main.py; then
        print_warning "main.py already contains litellm_keys references"
    else
        # Add import
        sed -i '/from open_webui.routers import (/a\    litellm_keys,' backend/open_webui/main.py
        
        # Add router
        sed -i '/app.include_router(utils.router, prefix="\/api\/v1\/utils", tags=\["utils"\])\n/a\# LiteLLM Keys API\napp.include_router(litellm_keys.router, prefix="\/api\/v1\/litellm-keys", tags=\["litellm-keys"\])' backend/open_webui/main.py
        
        print_success "Updated main.py"
    fi
    
    # Update users.py
    print_status "Updating users.py..."
    if grep -q "litellm_keys" backend/open_webui/models/users.py; then
        print_warning "users.py already contains litellm_keys references"
    else
        # Add relationship import
        sed -i '/from sqlalchemy import BigInteger, Column, String, Text, Date/a\from sqlalchemy.orm import relationship' backend/open_webui/models/users.py
        
        # Add relationship
        sed -i '/created_at = Column(BigInteger)/a\    # Relationships\n    litellm_keys = relationship("LiteLLMKey", back_populates="user")' backend/open_webui/models/users.py
        
        print_success "Updated users.py"
    fi
    
    # Install frontend components
    print_status "Installing frontend components..."
    
    # Create API directory
    mkdir -p src/lib/apis/litellm-keys
    if [ -f "src/lib/apis/litellm-keys/index.ts" ]; then
        print_success "API client already exists"
    else
        print_error "API client not found: src/lib/apis/litellm-keys/index.ts"
        exit 1
    fi
    
    # Create page directory
    mkdir -p src/routes/\(app\)/workspace/litellm-keys
    if [ -f "src/routes/(app)/workspace/litellm-keys/+page.svelte" ]; then
        print_success "Page component already exists"
    else
        print_error "Page component not found: src/routes/(app)/workspace/litellm-keys/+page.svelte"
        exit 1
    fi
    
    # Update workspace layout
    print_status "Updating workspace layout..."
    if grep -q "litellm-keys" src/routes/\(app\)/workspace/+layout.svelte; then
        print_warning "Workspace layout already contains litellm-keys references"
    else
        # Add permission check
        sed -i '/} else if ($page.url.pathname.includes('\''\/tools'\'') && !$user?.permissions?.workspace?.tools) {/a\		} else if ($page.url.pathname.includes('\''\/litellm-keys'\'') && !$user?.permissions?.workspace?.litellm_keys) {' src/routes/\(app\)/workspace/+layout.svelte
        sed -i '/} else if ($page.url.pathname.includes('\''\/litellm-keys'\'') && !$user?.permissions?.workspace?.litellm_keys) {/a\			goto('\''\/'\'');' src/routes/\(app\)/workspace/+layout.svelte
        sed -i '/goto('\''\/'\'');/a\		}' src/routes/\(app\)/workspace/+layout.svelte
        
        # Add navigation tab
        sed -i '/{$i18n.t('\''Tools'\'')}/a\						{/if}\n\n						{#if $user?.role === '\''admin'\'' || $user?.permissions?.workspace?.litellm_keys}\n							<a\n								class="min-w-fit p-1.5 {$page.url.pathname.includes('\''\/workspace\/litellm-keys'\'')\n									? '\'''\''\n									: '\''text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'\''} transition"\n								href="\/workspace\/litellm-keys"\n							>\n								LiteLLM Keys\n							<\/a>\n						{/if}' src/routes/\(app\)/workspace/+layout.svelte
        
        print_success "Updated workspace layout"
    fi
    
    # Run database migration
    print_status "Running database migration..."
    if command_exists alembic; then
        cd backend/open_webui
        alembic upgrade head
        cd ../..
        print_success "Database migration completed"
    else
        print_warning "Alembic not found. Please run the database migration manually:"
        print_warning "cd backend/open_webui && alembic upgrade head"
    fi
    
    print_success "LiteLLM Keys Plugin installation completed!"
    print_status "Next steps:"
    echo "1. Restart your Open WebUI server"
    echo "2. Navigate to Workspace → LiteLLM Keys"
    echo "3. Configure user permissions in Open WebUI admin settings"
    echo "4. Start creating and managing your LiteLLM API keys!"
}

# Uninstall function
uninstall_plugin() {
    print_status "Starting LiteLLM Keys Plugin uninstallation..."
    
    # Remove backend components
    print_status "Removing backend components..."
    
    # Remove model file
    if [ -f "backend/open_webui/models/litellm_keys.py" ]; then
        rm "backend/open_webui/models/litellm_keys.py"
        print_success "Removed model file"
    fi
    
    # Remove router file
    if [ -f "backend/open_webui/routers/litellm_keys.py" ]; then
        rm "backend/open_webui/routers/litellm_keys.py"
        print_success "Removed router file"
    fi
    
    # Remove migration file
    if [ -f "backend/open_webui/migrations/versions/a1b2c3d4e5f6_add_litellm_keys_table.py" ]; then
        rm "backend/open_webui/migrations/versions/a1b2c3d4e5f6_add_litellm_keys_table.py"
        print_success "Removed migration file"
    fi
    
    # Restore main.py from backup
    if [ -f "backend/open_webui/main.py.backup"* ]; then
        local backup_file=$(ls backend/open_webui/main.py.backup* | head -1)
        cp "$backup_file" "backend/open_webui/main.py"
        print_success "Restored main.py from backup"
    fi
    
    # Restore users.py from backup
    if [ -f "backend/open_webui/models/users.py.backup"* ]; then
        local backup_file=$(ls backend/open_webui/models/users.py.backup* | head -1)
        cp "$backup_file" "backend/open_webui/models/users.py"
        print_success "Restored users.py from backup"
    fi
    
    # Remove frontend components
    print_status "Removing frontend components..."
    
    # Remove API directory
    if [ -d "src/lib/apis/litellm-keys" ]; then
        rm -rf "src/lib/apis/litellm-keys"
        print_success "Removed API client"
    fi
    
    # Remove page directory
    if [ -d "src/routes/(app)/workspace/litellm-keys" ]; then
        rm -rf "src/routes/(app)/workspace/litellm-keys"
        print_success "Removed page component"
    fi
    
    # Restore workspace layout from backup
    if [ -f "src/routes/(app)/workspace/+layout.svelte.backup"* ]; then
        local backup_file=$(ls src/routes/\(app\)/workspace/+layout.svelte.backup* | head -1)
        cp "$backup_file" "src/routes/(app)/workspace/+layout.svelte"
        print_success "Restored workspace layout from backup"
    fi
    
    print_success "LiteLLM Keys Plugin uninstallation completed!"
    print_status "Please restart your Open WebUI server to complete the uninstallation."
}

# Main script logic
case "${1:-install}" in
    install)
        install_plugin
        ;;
    uninstall)
        uninstall_plugin
        ;;
    *)
        echo "Usage: $0 [install|uninstall]"
        echo ""
        echo "Commands:"
        echo "  install   - Install the LiteLLM Keys Plugin (default)"
        echo "  uninstall - Uninstall the LiteLLM Keys Plugin"
        echo ""
        echo "This script must be run from the Open WebUI root directory."
        exit 1
        ;;
esac