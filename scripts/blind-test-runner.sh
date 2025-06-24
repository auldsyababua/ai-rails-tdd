#!/bin/bash
# Blind Test Runner - Runs hidden tests without exposing them to agents

HIDDEN_DIR="$HOME/.ai-rails-hidden-tests"
PROJECT_DIR="$(pwd)"

# Check if feature name provided
if [ -z "$1" ]; then
    echo "Usage: ./scripts/blind-test-runner.sh <feature-name>"
    echo "Example: ./scripts/blind-test-runner.sh redis-integration"
    exit 1
fi

FEATURE=$1
TEST_FILE="$HIDDEN_DIR/$FEATURE/03_test_output.py"
IMPL_FILE="$PROJECT_DIR/inputs-to-outputs/${FEATURE}-actual/05_code_output.py"

# Check if test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "❌ Hidden test file not found: $TEST_FILE"
    exit 1
fi

# Check if implementation exists
if [ ! -f "$IMPL_FILE" ]; then
    echo "❌ Implementation not found: $IMPL_FILE"
    echo "   Coder needs to create 05_code_output.py first"
    exit 1
fi

echo "🧪 Running blind tests for: $FEATURE"
echo "📁 Test location: [HIDDEN]"
echo "📁 Implementation: $IMPL_FILE"
echo ""

# Create temporary test directory
TEMP_DIR=$(mktemp -d)
cp "$TEST_FILE" "$TEMP_DIR/test_feature.py"
cp "$IMPL_FILE" "$TEMP_DIR/implementation.py"

# Run tests and capture results
cd "$TEMP_DIR"
python -m pytest test_feature.py -v --tb=short > test_results.txt 2>&1
TEST_EXIT_CODE=$?

# Parse results for categories
echo "📊 Test Results by Category:"
echo "=============================="

# Extract category results (customize based on your test naming)
grep -E "test_.*happy.*PASSED" test_results.txt > /dev/null && echo "✅ Happy Path: PASS" || echo "❌ Happy Path: FAIL"
grep -E "test_.*edge.*PASSED" test_results.txt > /dev/null && echo "✅ Edge Cases: PASS" || echo "❌ Edge Cases: FAIL"
grep -E "test_.*error.*PASSED" test_results.txt > /dev/null && echo "✅ Error Handling: PASS" || echo "❌ Error Handling: FAIL"
grep -E "test_.*concurrent.*PASSED" test_results.txt > /dev/null && echo "✅ Concurrent Access: PASS" || echo "❌ Concurrent Access: FAIL"
grep -E "test_.*property.*PASSED" test_results.txt > /dev/null && echo "✅ Property Tests: PASS" || echo "❌ Property Tests: FAIL"
grep -E "test_.*performance.*PASSED" test_results.txt > /dev/null && echo "✅ Performance: PASS" || echo "❌ Performance: FAIL"

echo ""
echo "📈 Summary:"
PASSED=$(grep -c "PASSED" test_results.txt)
FAILED=$(grep -c "FAILED" test_results.txt)
echo "   Passed: $PASSED tests"
echo "   Failed: $FAILED tests"

# Clean up
cd "$PROJECT_DIR"
rm -rf "$TEMP_DIR"

# Exit with test status
exit $TEST_EXIT_CODE