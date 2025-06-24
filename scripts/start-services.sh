#!/bin/bash
# Start all AI Rails TDD services

echo "🚀 Starting AI Rails TDD Services..."
echo "=================================="

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Get ports from environment or use defaults
APPROVAL_PORT=${APPROVAL_SERVER_PORT:-8000}
TEST_RUNNER_PORT=${TEST_RUNNER_PORT:-8001}

# Start approval server if not running
if check_port $APPROVAL_PORT; then
    echo "✅ Approval server already running on port $APPROVAL_PORT"
else
    echo "Starting approval server on port $APPROVAL_PORT..."
    python webhooks/approval_server.py &
    APPROVAL_PID=$!
    echo "✅ Approval server started (PID: $APPROVAL_PID)"
fi

# Start test runner if not running
if check_port $TEST_RUNNER_PORT; then
    echo "✅ Test runner already running on port $TEST_RUNNER_PORT"
else
    echo "Starting test runner on port $TEST_RUNNER_PORT..."
    python webhooks/test_runner.py &
    TEST_RUNNER_PID=$!
    echo "✅ Test runner started (PID: $TEST_RUNNER_PID)"
fi

echo ""
echo "📋 Service Status:"
echo "- Approval Server: http://localhost:$APPROVAL_PORT"
echo "- Test Runner: http://localhost:$TEST_RUNNER_PORT"
echo ""
echo "🎯 Next Steps:"
echo "1. Open n8n at: ${N8N_BASE_URL:-http://localhost:5678}"
echo "2. Import a workflow from the workflows/ directory:"
echo "   - ai-rails-portable.json (for local Ollama)"
echo "   - ai-rails-portable-openai.json (for OpenAI API)"
echo "3. Configure the workflow with your project path"
echo "4. Execute the workflow"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "Stopping services..."; kill $APPROVAL_PID $TEST_RUNNER_PID 2>/dev/null; exit' INT
wait