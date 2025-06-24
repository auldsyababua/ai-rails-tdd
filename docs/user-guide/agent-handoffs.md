# Agent Handoff System Guide

## Overview

The AI Rails TDD system uses a structured folder-based approach to manage handoffs between AI agents. This ensures smooth transitions, preserves context, and enables debugging of the entire workflow.

## Folder Structure

All agent handoffs are stored in the `inputs-to-outputs/` directory:

```
inputs-to-outputs/
├── README.md                    # Documentation
├── feature-name-1/             # Each feature gets its own folder
│   ├── 01_planning_output.json
│   ├── 02_for_tester.json
│   ├── 03_test_output.py
│   ├── 04_for_coder.json
│   ├── 05_code_output.py
│   ├── 06_for_reviewer.json
│   ├── 07_review_output.md
│   └── 08_final_approved/
│       ├── test_feature.py
│       └── feature.py
└── feature-name-2/
    └── ...
```

## Workflow Steps

### 1. Starting a New Feature

Create a new directory with your feature name (use kebab-case):

```bash
mkdir inputs-to-outputs/my-new-feature
```

### 2. Planning Phase

The **Planner Agent** creates `01_planning_output.json`:

```json
{
  "feature_name": "my-new-feature",
  "description": "Clear description of what needs to be built",
  "requirements": [
    "List of specific requirements",
    "Extracted from planning document"
  ],
  "test_categories": ["suggested test types"],
  "complexity": "simple|medium|complex"
}
```

### 3. Human Review → Test Preparation

After approving the plan, create `02_for_tester.json`:

```json
{
  "feature_name": "my-new-feature",
  "requirements": ["from planning output"],
  "test_guidelines": {
    "categories": ["happy_path", "edge_cases", "error_handling"],
    "anti_gaming_measures": true,
    "focus_areas": ["specific concerns"]
  }
}
```

### 4. Test Generation

The **Tester Agent** reads `02_for_tester.json` and creates `03_test_output.py` with comprehensive tests.

### 5. Human Review → Code Preparation

After approving tests, create `04_for_coder.json`:

```json
{
  "feature_name": "my-new-feature",
  "requirements": ["from planning"],
  "test_file_path": "03_test_output.py",
  "implementation_guidelines": [
    "Make all tests pass",
    "Follow project conventions"
  ]
}
```

### 6. Code Generation

The **Coder Agent** reads the requirements and tests, then creates `05_code_output.py`.

### 7. Human Review → Review Preparation

After verifying the code works, create `06_for_reviewer.json`:

```json
{
  "feature_name": "my-new-feature",
  "test_file_path": "03_test_output.py",
  "code_file_path": "05_code_output.py",
  "review_criteria": ["correctness", "security", "performance", "style"]
}
```

### 8. Code Review

The **Reviewer Agent** analyzes both files and creates `07_review_output.md` with detailed feedback.

### 9. Final Approval

Once approved, copy the final files to `08_final_approved/`:

```bash
cp 03_test_output.py 08_final_approved/test_feature.py
cp 05_code_output.py 08_final_approved/feature.py
```

## Best Practices

### Naming Conventions
- Features: `user-authentication`, `email-validator`, `redis-integration`
- Files: Follow the numbered convention strictly
- Python files: Use descriptive names in final approved folder

### File Integrity
- Each JSON file must be valid and complete
- No partial outputs - wait until the agent is fully done
- Preserve all intermediate files for debugging

### Version Control
- Commit the entire feature folder after completion
- Use git to track changes during development
- Archive old features to `inputs-to-outputs/archive/`

### Error Recovery
- If an agent fails, check the last successful output
- You can restart from any step by creating the appropriate input file
- Keep failed attempts with `-failed` suffix for analysis

## Integration with n8n

The folder structure integrates seamlessly with n8n workflows:

1. **Webhook nodes** can read from specific file paths
2. **File nodes** can write agent outputs
3. **Conditional nodes** can check for file existence
4. **Human approval** can review the entire folder

## Debugging Tips

### Common Issues

1. **Missing Input File**
   - Check the file naming (must match exactly)
   - Verify JSON is valid with `jq` or online validator

2. **Agent Can't Parse Input**
   - Review the expected schema in README
   - Check for required fields

3. **Output Doesn't Match Expectations**
   - Review the agent's prompt
   - Check the input preparation step

### Useful Commands

```bash
# Validate JSON files
jq . inputs-to-outputs/feature-name/*.json

# Check workflow progress
ls -la inputs-to-outputs/feature-name/

# Compare outputs across features
diff inputs-to-outputs/feature-1/03_test_output.py \
     inputs-to-outputs/feature-2/03_test_output.py
```

## Example: Redis Integration

See `inputs-to-outputs/redis-integration/` for a complete example showing:
- Comprehensive planning output
- Well-structured test requirements
- Generated tests with all categories
- Implementation that passes tests
- Detailed code review
- Final approved files

This example demonstrates the ideal flow and file formats for each step.

## Future Enhancements

The current system will evolve to include:
- Automated validation of handoff files
- Schema enforcement with JSON Schema
- Automatic routing between agents
- Parallel processing of independent steps
- Web UI for managing handoffs

For now, the folder-based system provides clear visibility and control over the entire TDD workflow.