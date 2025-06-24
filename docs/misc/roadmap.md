# AI Rails TDD Roadmap

This document outlines the planned features and improvements for AI Rails TDD.

## Current MVP

The current MVP focuses on proving the core TDD pattern works:
- ✅ n8n workflow for test generation → human approval → code generation
- ✅ Command-line tools for project initialization
- ✅ Basic webhook servers for approval and test running
- ✅ Integration with Ollama/OpenAI for AI generation
- ✅ Anti-mesa-optimization measures in prompts

## Future Features

### Simple UI / Dashboard (App-like Web Controller)

**Goal:** A beautiful, simple, app-like experience to manage the AI Rails TDD workflow, eliminating manual copy-pasting.

**Technology:** A Python web application (e.g., Flask, FastAPI with a lightweight frontend framework like HTMX, Alpine.js, or vanilla JS) running in a Docker container, accessible via web browser.

**Features:**
- **Planning Document Editor:** Edit and preview planning documents with syntax highlighting
- **Test Output Display:** Show generated tests clearly, rendered with syntax highlighting
- **"Send to Next Step" Buttons:** Automate the progression through the TDD workflow
- **Approval Interface:** Integrated approval UI instead of separate approval server
- **Diff Viewer:** View test changes and code implementations side-by-side
- **Test Results Display:** Show real pytest output with pass/fail status
- **Commit/Push Integration:** Buttons to save approved tests and code to the project
- **Log Viewer:** Real-time display of `.ai-rails/logs/` with filtering
- **Prompt Template Manager:** UI to view, edit, and manage agent prompts in `prompts/`

### CLI Workflow Automation

**Goal:** Execute n8n workflows directly from the command line without manual browser interaction.

**Features:**
- `ai-rails run planning-doc-feature.md` - Automatically trigger n8n workflow
- Read configuration from `.ai-rails/config.json` and `.env`
- Stream progress to terminal
- Open approval URL automatically when needed
- Return to terminal after completion

### Redis Support for Workflow State Management

**Goal:** Maintain workflow state and history across multiple TDD cycles without re-entering data.

**Mechanism:** 
- Utilize a Redis instance (local or remote)
- Store planning documents, generated tests, and implementations
- Enable quick re-runs with modifications
- Track approval history and feedback

### Automated Test Execution Pipeline

**Goal:** Seamless integration of actual test execution into the workflow.

**Features:**
- Automatic pytest execution after code generation
- Support for multiple test frameworks (pytest, jest, go test)
- Docker container isolation for safe test execution
- Coverage report generation and display
- Automatic re-generation on test failures

### Enhanced n8n Integration

**Goal:** Make n8n workflows more powerful and flexible.

**Features:**
- **Dynamic Model Selection:** Choose between Ollama, OpenAI, Anthropic at runtime
- **Webhook Security:** Add authentication to approval webhooks
- **Parallel Processing:** Generate multiple test variations simultaneously
- **Workflow Templates:** Pre-built workflows for different project types

### Project-Specific Configuration

**Goal:** Allow per-project customization without modifying global settings.

**Mechanism:**
- `.ai-rails/config.yaml` for project-specific settings
- Override global prompts with project-specific versions
- Custom test patterns and conventions
- Language-specific configurations

### Centralized Prompt Management

**Goal:** Single source of truth for all AI prompts and instructions.

**Features:**
- **Prompt Versioning:** Track changes to prompts over time
- **A/B Testing:** Compare different prompt strategies
- **Role-Based Prompts:** Different instructions for different project types
- **Dynamic Injection:** Load only relevant prompts based on project context

### Integration with External Services

**Goal:** Connect AI Rails TDD with existing development tools.

**Planned Integrations:**
- **GitHub/GitLab:** Automatic PR creation with tests and implementation
- **CI/CD Systems:** Trigger AI Rails on PR creation
- **Code Review Tools:** Send generated code for automated review
- **Issue Trackers:** Create issues from failed test scenarios

### Local Model Management

**Goal:** Simplify the use of local models via Ollama.

**Features:**
- Model download automation
- Model performance comparison
- Automatic model selection based on task
- Resource usage monitoring

### Security Enhancements

**Goal:** Ensure safe operation in production environments.

**Features:**
- **Sandboxed Execution:** Run all generated code in isolated containers
- **Secret Management:** Never expose API keys in logs or UI
- **Audit Logging:** Track all approvals and generations
- **Rate Limiting:** Prevent abuse of API endpoints

### Monitoring and Analytics

**Goal:** Understand how AI Rails TDD is being used and improve it.

**Features:**
- Test generation success rates
- Common failure patterns
- Time saved metrics
- Model performance comparison
- Usage dashboards

---

*Note: These features are adapted from the original AI Rails agent-based system to fit the TDD workflow paradigm. Priority will be given to features that enhance the core TDD experience.*