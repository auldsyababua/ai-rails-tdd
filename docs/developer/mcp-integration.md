# MCP Integration for AI Rails TDD

## Available MCP Services

Based on your environment, you have these MCPs available:

### 1. **Local MCPs** (When Running)
- **CodebaseSummaryMCP** (`http://localhost:8003`) - Analyze existing codebases
- **SecretsMCP** (`http://localhost:8005`) - Secure API key management

### 2. **Global MCPs**
- **mcp-omnisearch** - Multi-source web search and content extraction
- **context7** - Documentation retrieval
- **mcp-sequentialthinking-tools** - Advanced reasoning
- **github** - Code repository operations
- **memory** - Knowledge graph storage
- **todoist** - Task management

## How to Pull Ollama Model

If `ollama` command isn't in PATH on your server, use the full path or Docker:

```bash
# Option 1: Find ollama installation
ssh your-server
which ollama || find / -name ollama 2>/dev/null | grep -E "bin/ollama$"

# Option 2: Use systemctl (if running as service)
sudo systemctl status ollama

# Option 3: Use Docker (if containerized)
docker ps | grep ollama
docker exec -it [ollama-container] ollama pull qwen2.5-coder:32b

# Option 4: Use the API directly
curl -X POST http://localhost:11434/api/pull -d '{
  "name": "qwen2.5-coder:32b"
}'
```

## Enhanced n8n Workflow Ideas

### 1. **Research-Enhanced TDD**
Add a research step before test generation:
- Use **mcp-omnisearch** to find best practices
- Use **context7** to get framework documentation
- Feed research into test generation

### 2. **Codebase-Aware TDD**
For existing projects:
- Use **CodebaseSummaryMCP** to understand current code
- Generate tests that fit existing patterns
- Ensure compatibility with project structure

### 3. **Multi-Agent Review**
After code generation:
- Use **mcp-sequentialthinking-tools** for deep analysis
- Store results in **memory** MCP for learning
- Track tasks in **todoist**

## n8n Workflow with MCP Integration

Here's how to add MCP calls to your n8n workflow:

### HTTP Request Node for CodebaseSummaryMCP
```json
{
  "method": "POST",
  "url": "http://localhost:8003/analyze",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "path": "/path/to/project",
    "query": "existing validation functions"
  }
}
```

### HTTP Request Node for SecretsMCP
```json
{
  "method": "POST",
  "url": "http://localhost:8005/get_secret",
  "headers": {
    "Content-Type": "application/json",
    "X-API-Key": "{{ $env.SECRETS_MCP_AUTH_TOKEN }}"
  },
  "body": {
    "key": "OPENAI_API_KEY"
  }
}
```

## Future Enhancements

1. **Pre-Test Research Node**: 
   - Query mcp-omnisearch for "email validation best practices"
   - Get testing patterns from context7
   - Include findings in test generation prompt

2. **Code Pattern Analysis Node**:
   - Use CodebaseSummaryMCP to find similar functions
   - Ensure generated code matches project style

3. **Knowledge Storage Node**:
   - Store successful patterns in memory MCP
   - Build up library of test/code pairs

4. **Task Tracking Node**:
   - Create todoist tasks for manual review items
   - Track which features have been TDD'd

## Environment Variables Needed

Add to your `.env`:

```bash
# MCP Authentication
MCP_AUTH_TOKEN=your-auth-token-here

# MCP API Keys for Planning Template
# See .env.example for comprehensive list with links to get keys
TAVILY_API_KEY=tvly-...your-key-here...
BRAVE_API_KEY=BSA...your-key-here...
# Add more as needed from .env.example

# Optional: External API Keys (if using other services)
# GITHUB_TOKEN=your-github-token
# OPENAI_API_KEY=your-openai-key
```

**Note**: The planning template requires several MCP API keys for optimal research capabilities. See `.env.example` for a complete list with links to obtain each key.

## Quick Test Commands

Test MCP connectivity:

```bash
# Test CodebaseSummaryMCP
curl http://localhost:8003/health

# Test SecretsMCP (requires auth token)
curl -H "X-API-Key: your-token" http://localhost:8005/health

# Test Ollama API
curl http://localhost:11434/api/tags
```