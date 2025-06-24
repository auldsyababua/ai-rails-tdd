# CLAUDE.md - AI Rails TDD Project Configuration

## Access Restrictions for Blind Testing

### Restricted Directories
The following directories are **OFF-LIMITS** for all AI agents unless content is explicitly provided in the conversation:

```
/inputs-to-outputs/redis-integration-actual/
/inputs-to-outputs/*-actual/
/inputs-to-outputs/*-blind/
/inputs-to-outputs/blind-test-scenarios/
/test-isolation/
/agent-sandbox/
/blind-tests/
```

### Access Policy
1. **DO NOT** use Read, Glob, Grep, or LS tools on restricted directories
2. **DO NOT** attempt to access files in these directories
3. **ONLY** work with content explicitly pasted into the conversation
4. If asked to read from a restricted directory, respond: "This directory is marked as restricted for blind testing. Please paste the specific content you'd like me to review."

### Rationale
These restrictions enable true blind testing where agents work without seeing implementation details or expected outputs, simulating real-world scenarios where requirements come before implementation.

## General Project Guidelines

### File Operations
- You have normal read/write access to all non-restricted directories
- Always check if a path contains restricted directory names before accessing
- When in doubt, ask for clarification

### Testing Workflow
1. Human creates test scenarios in restricted directories
2. Human provides requirements to agents (not the actual tests)
3. Agents generate tests/code based only on requirements
4. Human validates against hidden test cases
5. Results are compared for accuracy

### Example Restricted Path Check
```python
restricted_patterns = [
    "inputs-to-outputs/redis-integration-actual",
    "inputs-to-outputs/*-actual",
    "inputs-to-outputs/*-blind",
    "test-isolation",
    "agent-sandbox",
    "blind-tests"
]

# Before accessing any file, check:
if any(pattern in file_path for pattern in restricted_patterns):
    return "Access restricted for blind testing"
```

## Enforcement
This policy is **ACTIVE** as of 2024-12-24. All Claude instances and other AI agents must respect these restrictions.