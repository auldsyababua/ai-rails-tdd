# AI Rails TDD - MVP Scope & n8n Integration

## What This MVP Does

This MVP implements a **single n8n workflow** that demonstrates the core TDD pattern:

1. **Input**: Use the You provide a feature description using the planning template
   - **Highly Recommended MCP Servers**:
     - [**mcp-sequential-thinking**](https://github.com/jlowin/mcp-sequential-thinking): Enables dynamic, reflective problem-solving through flexible thinking processes that can adapt and evolve. Essential for breaking down complex features into testable components.
     - [**context7**](https://github.com/dawsonbooth/mcp-context7): Provides up-to-date documentation for libraries and frameworks. Critical for ensuring generated tests and code use current best practices and version-specific up-to-date context on documentation.
     - [**brave-search**](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search): Web search capability for researching implementation patterns, common pitfalls, and security considerations.
   - **Untested but Potentially Useful MCP Servers**:
     - [**stackoverflow-mcp**](https://github.com/gscalzo/stackoverflow-mcp): Enables dynamic, reflective problem-solving through flexible thinking processes that can adapt and evolve. Essential for breaking down complex features into testable components.
2. **Test Generation**: Ollama generates comprehensive tests with anti-gaming measures
3. **Human Review**: You review/approve tests via web interface
4. **Code Generation**: Ollama writes code to pass the approved tests
5. **Output**: Validated code that passes all tests

## How n8n Fits In

The ENTIRE system runs as an n8n workflow:

```
[Manual Trigger] → [Generate Tests] → [Human Approval] → [Generate Code] → [Validate]
     ↓                    ↓                  ↓                  ↓              ↓
  Feature Doc      Ollama API Call    Webhook Wait      Ollama API Call   Success
```

### n8n Nodes Used:
- **Manual Trigger**: Start with planning document
- **HTTP Request**: Call Ollama for test/code generation
- **Webhook**: Wait for human approval
- **Code Node**: Validate schemas and results
- **If Node**: Route based on approval

## What's NOT in This MVP

This MVP does NOT:
- Save files automatically (outputs to n8n)
- Run actual pytest (simulates validation)
- Connect to GitHub or other services
- Use multiple AI agents (just prompts)
- Integrate with existing codebases

## How to Use It

### Step 1: Fill Out Planning Document

Use `docs/PLANNING_TEMPLATE.md` to describe your feature:
```markdown
**Feature Name**: Email Validator
**Feature Description**: Validates email addresses using regex
**Complexity**: simple
...
```

### Step 2: Import & Configure n8n Workflow

1. Import `workflows/tdd-basic-workflow.json` into n8n
2. Configure the Ollama endpoint in the workflow

### Step 3: Run the Workflow

1. Click "Execute Workflow" 
2. Paste your planning document content
3. Review generated tests at approval URL
4. Approve/reject
5. Get generated code

### Step 4: Use the Output

The workflow outputs:
- Generated tests (Python code)
- Generated implementation (Python code)
- Validation results

You manually save these to your project.

## Future Expansions

After MVP works, we can add:
- **File Management Node**: Auto-save to project
- **Test Runner Node**: Actually run pytest
- **Multiple Agents**: Planner → Coder → Reviewer
- **MCP Integration**: Use CodebaseSummaryMCP
- **Project Templates**: Different languages/frameworks

## Why This Approach?

1. **Proves the Core Pattern**: TDD with human approval works
2. **Visual & Debuggable**: See every step in n8n
3. **No Code Required**: Non-coders can use it
4. **Extensible**: Easy to add more nodes/features

## Environment Setup

The workflow expects these services:
- Ollama at `http://localhost:11434` (with qwen2.5-coder:32b) or your configured Ollama URL
- Approval server at `http://localhost:8000`
- MCP servers at `http://localhost:8003` and `:8005` (future use)

## Success Metrics

MVP is successful if:
- ✅ Generates diverse test categories
- ✅ Human can approve/reject tests
- ✅ Generated code attempts to pass tests
- ✅ No obvious test gaming
- ✅ Non-coder can understand and use it

## ⚠️ MCP Security Considerations

**CRITICAL**: Model Context Protocol (MCP) servers provide powerful capabilities but must be properly secured:

### Prompt Injection Risks
- MCP servers execute based on LLM instructions, making them vulnerable to prompt injection attacks
- Malicious actors could potentially:
  - Access sensitive files through filesystem MCPs
  - Make unauthorized API calls through service MCPs
  - Exfiltrate data through search/web MCPs

### Security Best Practices

1. **Container Isolation**
   - Run each MCP server in a separate container with minimal permissions
   - Use read-only filesystem mounts where possible
   - Implement network segmentation between MCP servers

2. **Access Control**
   - Limit MCP filesystem access to specific project directories
   - Use API key rotation for external service MCPs
   - Implement request logging and monitoring

3. **Input Validation**
   - Validate all inputs before passing to MCP servers
   - Implement rate limiting on MCP requests
   - Monitor for suspicious patterns in MCP usage

4. **Environment Variables**
   - Never hardcode API keys in MCP configurations
   - Use secure secret management (e.g., 1Password integration)
   - Rotate credentials regularly

### Recommended MCP Security Setup

```bash
# Example Docker Compose for isolated MCP servers
services:
  mcp-filesystem:
    image: mcp-filesystem:latest
    volumes:
      - ./project:/workspace:ro  # Read-only mount
    environment:
      - MCP_ALLOWED_PATHS=/workspace
    networks:
      - mcp-internal
    
  mcp-web-search:
    image: mcp-brave-search:latest
    environment:
      - BRAVE_API_KEY_FILE=/run/secrets/brave_key
    secrets:
      - brave_key
    networks:
      - mcp-external
```

For production deployments, consider using a dedicated MCP gateway with authentication and audit logging.