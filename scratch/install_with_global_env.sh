#!/bin/bash
# Enhanced AI Rails installation script with global environment support

set -e

echo "🚀 AI Rails TDD Installation with Global Environment Support"
echo "=========================================================="

# Function to install AI Rails in a project
install_ai_rails() {
    local TARGET_DIR="$1"
    local AI_RAILS_SOURCE="${2:-/Users/colinaulds/Desktop/projects/ai-rails-tdd}"
    
    echo "📍 Installing in: $TARGET_DIR"
    cd "$TARGET_DIR"
    
    # Check for existing installation
    if [ -d "ai-rails-tdd" ]; then
        echo "⚠️  Found existing ai-rails-tdd directory"
        
        # Backup important files
        if [ -f "ai-rails-tdd/.env" ]; then
            cp ai-rails-tdd/.env .env.ai-rails.backup.$(date +%Y%m%d_%H%M%S)
            echo "💾 Backed up existing .env"
        fi
        if [ -f "ai-rails-tdd/.env.project" ]; then
            cp ai-rails-tdd/.env.project .env.project.backup.$(date +%Y%m%d_%H%M%S)
            echo "💾 Backed up existing .env.project"
        fi
        
        echo "🗑️  Removing old installation..."
        rm -rf ai-rails-tdd
    fi
    
    # Copy AI Rails
    echo "📋 Copying AI Rails from $AI_RAILS_SOURCE..."
    cp -r "$AI_RAILS_SOURCE" ai-rails-tdd
    
    # Remove git history
    rm -rf ai-rails-tdd/.git
    
    # Enter the directory
    cd ai-rails-tdd
    
    # Set up Python environment
    echo "🐍 Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Initialize environment configuration
    echo "🔧 Setting up environment configuration..."
    python3 -c "
from src.env_manager import EnvManager
import sys

manager = EnvManager()
print('\\n📝 Initializing hierarchical environment configuration...')

# This will create templates and set up the structure
config = manager.init_project_env()

# Show what was set up
manager.show_config_info()

# Check for critical missing keys
missing_critical = []
critical_keys = ['OPENAI_API_KEY', 'UPSTASH_REDIS_URL']
for key in critical_keys:
    if not config.get(key) or config[key].startswith('sk-...'):
        missing_critical.append(key)

if missing_critical:
    print('\\n⚠️  Missing critical configuration:')
    for key in missing_critical:
        print(f'   - {key}')
    print('\\nPlease update your configuration files!')
    sys.exit(1)
else:
    print('\\n✅ All critical configurations found!')
"
    
    # Run verification
    echo -e "\n🔍 Running setup verification..."
    python scratch/verify_setup.py || echo "⚠️  Some checks failed - please review"
    
    echo -e "\n✨ Installation complete!"
}

# Function to set up global configuration
setup_global_config() {
    echo "🌍 Setting up global AI Rails configuration..."
    
    GLOBAL_DIR="$HOME/.ai-rails"
    mkdir -p "$GLOBAL_DIR"
    
    if [ ! -f "$GLOBAL_DIR/.env.global" ]; then
        echo "📝 Creating global configuration template..."
        cat > "$GLOBAL_DIR/.env.global" << 'EOF'
# AI Rails Global Configuration
# Store your API keys here - they'll be available to all projects

# =============================================================================
# Copy your MCP API keys from your main .env file
# =============================================================================

# These are the keys you'll want to share across projects:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY  
# - TAVILY_API_KEY
# - BRAVE_API_KEY
# - JINA_API_KEY
# - GITHUB_TOKEN
# - UPSTASH_REDIS_URL
# - UPSTASH_VECTOR_URL
# - UPSTASH_VECTOR_TOKEN

EOF
        echo "✅ Created $GLOBAL_DIR/.env.global"
        echo "📌 Please copy your API keys to this file!"
    else
        echo "✅ Global config already exists"
    fi
}

# Main execution
if [ "$1" == "--help" ]; then
    echo "Usage: $0 [TARGET_DIRECTORY]"
    echo "       $0 --setup-global    # Just set up global config"
    exit 0
fi

if [ "$1" == "--setup-global" ]; then
    setup_global_config
    exit 0
fi

# Set up global config first
setup_global_config

# Install in target directory
TARGET="${1:-$(pwd)}"
install_ai_rails "$TARGET"

echo -e "\n📋 Next Steps:"
echo "1. Edit ~/.ai-rails/.env.global with your API keys"
echo "2. Edit ai-rails-tdd/.env.project for project-specific settings"
echo "3. Activate virtualenv: source ai-rails-tdd/venv/bin/activate"
echo "4. Start using AI Rails TDD!"
echo ""
echo "Environment loading order:"
echo "  ~/.ai-rails/.env.global → .env.defaults → .env.project → .env.local → .env"
echo "  (Later files override earlier ones)"