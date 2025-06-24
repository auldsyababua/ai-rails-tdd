# Agent Handoff Organization System

## Problem Statement

Currently, there's no structured way to manage handoffs between AI agents in the TDD workflow. Each agent needs to:
1. Receive input from the previous agent
2. Process it according to their role
3. Output in a format the next agent expects

Without proper organization, this leads to:
- Lost context between agents
- Inconsistent output formats
- Difficulty tracking the progress of a feature
- Manual copy-pasting between stages

## Proposed Solution

### Phase 1: Simple Folder-Based Handoff System

Create a folder structure that mirrors the agent workflow:

```
inputs-to-outputs/
└── feature-name/
    ├── 00_planning_doc.md          # Planner human-readable design doc
    ├── 01_planning_output.json     # Planner machine-readable output
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

**Benefits:**
- Clear progression through the workflow
- Each agent knows where to find their input
- Outputs are preserved for debugging
- Easy to see the status of any feature

**Implementation:**
1. Create the folder structure when starting a new feature
2. Each agent reads from their designated input file
3. Each agent writes to their designated output file
4. Human approval steps can review the entire folder

### Phase 2: Automated Router System

Build a "dumb" router that enforces contracts between agents:

```python
class AgentRouter:
    def __init__(self, feature_name: str):
        self.feature_name = feature_name
        self.contracts = {
            'planner': PlannerContract(),
            'tester': TesterContract(),
            'coder': CoderContract(),
            'reviewer': ReviewerContract()
        }
    
    def validate_output(self, agent_name: str, output: dict) -> bool:
        """Validate that agent output matches expected schema"""
        return self.contracts[agent_name].validate(output)
    
    def validate_planner_outputs(self, doc_path: str, json_path: str) -> bool:
        """Special validation for planner's dual outputs"""
        # Validate markdown document exists and has required sections
        # Validate JSON matches schema and aligns with doc
        return True
    
    def route(self, from_agent: str, to_agent: str, data: dict):
        """Route data from one agent to another with validation"""
        if not self.validate_output(from_agent, data):
            raise ValidationError(f"{from_agent} output doesn't match contract")
        
        processed_data = self.contracts[to_agent].prepare_input(data)
        return processed_data
```

**Features:**
- JSON Schema validation for each agent's output
- Automatic transformation between agent formats
- Error handling for malformed outputs
- Logging and audit trail
- Support for retry/rollback

**Benefits:**
- Enforces consistent interfaces between agents
- Catches errors early
- Enables parallel agent execution
- Makes the system more modular

## Implementation Plan

### Phase 1 Tasks:
1. Create folder structure utilities
2. Update agent prompts to specify input/output locations
3. Create example workflows using the folder system
4. Document the convention

### Phase 2 Tasks:
1. Define JSON schemas for each agent's output
   - Planner: Dual output validation (MD + JSON)
   - Tester: Python test file validation
   - Coder: Implementation file validation
   - Reviewer: Review report validation
2. Implement validation logic
   - Schema validation for JSON outputs
   - Syntax validation for Python files
   - Cross-validation between planner outputs
3. Create router service
4. Integrate with n8n workflows
5. Add monitoring and error handling

## Success Criteria

### Phase 1:
- [ ] Can run complete TDD workflow using folder handoffs
- [ ] No manual copy-pasting between agents
- [ ] Clear visibility into feature progress
- [ ] Easy to debug failed handoffs

### Phase 2:
- [ ] Automatic validation catches 95% of format errors
- [ ] Router handles all agent transitions
- [ ] Support for workflow branching/merging
- [ ] Performance monitoring and optimization

## Related Issues
- Enhances #6 (Enhanced n8n Integration)
- Supports #8 (Centralized Prompt Management)
- Enables #12 (Monitoring and Analytics)