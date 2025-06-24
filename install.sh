#!/bin/bash
# Install AI Rails CLI globally

echo "🚀 Installing AI Rails CLI..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create symlink in /usr/local/bin
if [ -w /usr/local/bin ]; then
    ln -sf "$SCRIPT_DIR/ai-rails-cli.py" /usr/local/bin/ai-rails
    echo "✅ Installed ai-rails command"
else
    echo "❌ Cannot write to /usr/local/bin. Try with sudo:"
    echo "   sudo $0"
    exit 1
fi

# Create a wrapper script that knows where AI Rails home is
cat > /usr/local/bin/ai-rails-start << EOF
#!/bin/bash
# Start AI Rails services from the main directory
export AI_RAILS_HOME="$SCRIPT_DIR"
cd "\$AI_RAILS_HOME" && ./scripts/start-services.sh
EOF

chmod +x /usr/local/bin/ai-rails-start

echo "✅ AI Rails CLI installed successfully!"
echo ""
echo "📋 Available commands:"
echo "   ai-rails init         - Initialize AI Rails in a project"
echo "   ai-rails start        - Start AI Rails services"
echo "   ai-rails status       - Check current project status"
echo "   ai-rails archive      - Archive current feature"
echo "   ai-rails-start        - Start services from anywhere"
echo ""
echo "🎯 Next steps:"
echo "1. Go to any project: cd /path/to/your/project"
echo "2. Initialize: ai-rails init"
echo "3. Start services: ai-rails-start"
echo "4. Import workflow in n8n: $SCRIPT_DIR/workflows/ai-rails-portable.json"