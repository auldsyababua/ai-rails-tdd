# Agent Handoff Directory

This directory contains the structured handoffs between AI agents in the TDD workflow.

## Structure

Each feature gets its own directory with numbered files showing the progression:

```
feature-name/
├── 01_planning_output.json      # Planner agent output
├── 02_for_tester.json          # Processed input for test designer
├── 03_test_output.py           # Test designer output
├── 04_for_coder.json           # Processed input for coder
├── 05_code_output.py           # Coder output
├── 06_for_reviewer.json        # Processed input for reviewer
├── 07_review_output.md         # Reviewer output
└── 08_final_approved/          # Final approved files
    ├── tests.py
    └── implementation.py
```

## Workflow

1. **Start Feature**: Create a new directory with the feature name
2. **Planner**: Reads feature request, outputs to `01_planning_output.json`
3. **Human Review**: Approves plan, creates `02_for_tester.json`
4. **Tester**: Reads input, outputs tests to `03_test_output.py`
5. **Human Review**: Approves tests, creates `04_for_coder.json`
6. **Coder**: Reads input + tests, outputs code to `05_code_output.py`
7. **Human Review**: Approves code, creates `06_for_reviewer.json`
8. **Reviewer**: Reviews all artifacts, outputs to `07_review_output.md`
9. **Final Approval**: Approved files moved to `08_final_approved/`

## File Formats

### Planning Output (JSON)
```json
{
  "feature_name": "string",
  "description": "string",
  "requirements": ["array of strings"],
  "test_categories": ["array of test types needed"],
  "complexity": "simple|medium|complex"
}
```

### For Tester (JSON)
```json
{
  "feature_name": "string",
  "requirements": ["array of strings"],
  "test_guidelines": {
    "categories": ["happy_path", "edge_cases", "error_handling"],
    "anti_gaming_measures": true
  }
}
```

### For Coder (JSON)
```json
{
  "feature_name": "string",
  "requirements": ["array of strings"],
  "test_file_path": "string",
  "implementation_guidelines": ["array of strings"]
}
```

### For Reviewer (JSON)
```json
{
  "feature_name": "string",
  "test_file_path": "string",
  "code_file_path": "string",
  "review_criteria": ["correctness", "security", "performance", "style"]
}
```

## Best Practices

1. **Naming**: Use kebab-case for feature names (e.g., `email-validator`, `user-authentication`)
2. **Atomicity**: Each file represents a complete handoff - no partial outputs
3. **Versioning**: If you need to retry, append `-v2`, `-v3` to filenames
4. **Cleanup**: Archive completed features to `archive/` subdirectory

## Example

See `redis-integration/` for a complete example workflow.