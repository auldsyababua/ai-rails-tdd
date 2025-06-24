# Agent Access Control Policy

## Purpose
This document defines access restrictions for AI agents working in this codebase. It ensures that certain directories remain isolated for blind testing scenarios where agents should not have access to implementation details or test results.

## Restricted Directories

The following directories are **OFF-LIMITS** to all AI agents unless explicitly provided in the conversation:

### 1. Test Isolation Folders
```
/inputs-to-outputs/redis-integration-actual/
/inputs-to-outputs/blind-test-scenarios/
/inputs-to-outputs/*-actual/
/inputs-to-outputs/*-blind/
```

### 2. Agent Sandbox Areas
```
/test-isolation/
/agent-sandbox/
/blind-tests/
```

## Access Rules

### For AI Agents (Claude, GPT, etc.):
1. **DO NOT** use any file reading tools (Read, Glob, Grep, LS) on restricted directories
2. **DO NOT** attempt to access or reference files in these directories
3. **ONLY** work with content that is explicitly pasted into the conversation
4. If asked to read from a restricted directory, respond: "This directory is marked as restricted for blind testing. Please paste the specific content you'd like me to review."

### For Humans:
1. You maintain full access to all directories
2. You can copy/paste content from restricted directories into conversations
3. You control what agents can see by what you share

## Implementation Strategies

### Option 1: Honor System (Current)
Agents are instructed via this policy document to avoid accessing restricted directories.

### Option 2: Wrapper Script
Create a wrapper around file operations that checks against the restriction list:

```python
# utils/agent_file_access.py
import os
from pathlib import Path

RESTRICTED_PATHS = [
    "inputs-to-outputs/redis-integration-actual",
    "inputs-to-outputs/blind-test-scenarios",
    "test-isolation",
    "agent-sandbox"
]

def is_restricted(file_path: str) -> bool:
    """Check if a path is in a restricted directory"""
    path = Path(file_path).resolve()
    for restricted in RESTRICTED_PATHS:
        if restricted in str(path):
            return True
    return False

def safe_read(file_path: str) -> str:
    """Read file only if not in restricted directory"""
    if is_restricted(file_path):
        raise PermissionError(f"Access denied: {file_path} is in a restricted directory for blind testing")
    with open(file_path, 'r') as f:
        return f.read()
```

### Option 3: .gitignore-style Configuration
Use the `.agent-restrictions` file with glob patterns:

```
# .agent-restrictions
/inputs-to-outputs/*-actual/
/inputs-to-outputs/*-blind/
/test-isolation/**
/agent-sandbox/**
*.secret
.env.production
```

## Testing Workflow

### For Blind Testing:
1. Create test scenarios in restricted directories
2. Run agents without giving them access to these directories
3. Manually copy relevant portions into the conversation when needed
4. Agents work only with what you explicitly provide

### Example:
```bash
# Human creates test in restricted area
mkdir inputs-to-outputs/feature-x-actual
echo "test content" > inputs-to-outputs/feature-x-actual/test.py

# Agent is asked to implement feature
# Agent CANNOT read the test directly
# Human copies test content and pastes it into chat
# Agent works only with pasted content
```

## Enforcement

### Current Status: ACTIVE
This policy is now active. All agents should respect these restrictions immediately.

### Verification:
- Agents should refuse to access restricted directories
- Agents should acknowledge when a path is restricted
- Humans can test by asking agents to read from restricted paths

## Updates
Last Updated: 2024-12-24
Policy Version: 1.0