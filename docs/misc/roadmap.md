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

### Simple UI / Dashboard (App-like Web Controller) [#2](https://github.com/auldsyababua/ai-rails-tdd/issues/2)

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

### CLI Workflow Automation [#3](https://github.com/auldsyababua/ai-rails-tdd/issues/3)

**Goal:** Execute n8n workflows directly from the command line without manual browser interaction.

**Features:**
- `ai-rails run planning-doc-feature.md` - Automatically trigger n8n workflow
- Read configuration from `.ai-rails/config.json` and `.env`
- Stream progress to terminal
- Open approval URL automatically when needed
- Return to terminal after completion

### Redis Support for Workflow State Management [#4](https://github.com/auldsyababua/ai-rails-tdd/issues/4)

**Goal:** Maintain workflow state and history across multiple TDD cycles without re-entering data.

**Mechanism:** 
- Utilize a Redis instance (local or remote)
- Store planning documents, generated tests, and implementations
- Enable quick re-runs with modifications
- Track approval history and feedback

### Automated Test Execution Pipeline [#5](https://github.com/auldsyababua/ai-rails-tdd/issues/5)

**Goal:** Seamless integration of actual test execution into the workflow.

**Features:**
- Automatic pytest execution after code generation
- Support for multiple test frameworks (pytest, jest, go test)
- Docker container isolation for safe test execution
- Coverage report generation and display
- Automatic re-generation on test failures

### Enhanced n8n Integration [#6](https://github.com/auldsyababua/ai-rails-tdd/issues/6)

**Goal:** Make n8n workflows more powerful and flexible.

**Features:**
- **Dynamic Model Selection:** Choose between Ollama, OpenAI, Anthropic at runtime
- **Webhook Security:** Add authentication to approval webhooks
- **Parallel Processing:** Generate multiple test variations simultaneously
- **Workflow Templates:** Pre-built workflows for different project types

### Project-Specific Configuration [#7](https://github.com/auldsyababua/ai-rails-tdd/issues/7)

**Goal:** Allow per-project customization without modifying global settings.

**Mechanism:**
- `.ai-rails/config.yaml` for project-specific settings
- Override global prompts with project-specific versions
- Custom test patterns and conventions
- Language-specific configurations

### Centralized Prompt Management [#8](https://github.com/auldsyababua/ai-rails-tdd/issues/8)

**Goal:** Single source of truth for all AI prompts and instructions.

**Features:**
- **Prompt Versioning:** Track changes to prompts over time
- **A/B Testing:** Compare different prompt strategies
- **Role-Based Prompts:** Different instructions for different project types
- **Dynamic Injection:** Load only relevant prompts based on project context

### Integration with External Services [#9](https://github.com/auldsyababua/ai-rails-tdd/issues/9)

**Goal:** Connect AI Rails TDD with existing development tools.

**Planned Integrations:**
- **GitHub/GitLab:** Automatic PR creation with tests and implementation
- **CI/CD Systems:** Trigger AI Rails on PR creation
- **Code Review Tools:** Send generated code for automated review
- **Issue Trackers:** Create issues from failed test scenarios

### Local Model Management [#10](https://github.com/auldsyababua/ai-rails-tdd/issues/10)

**Goal:** Simplify the use of local models via Ollama.

**Features:**
- Model download automation
- Model performance comparison
- Automatic model selection based on task
- Resource usage monitoring

### Security Enhancements [#11](https://github.com/auldsyababua/ai-rails-tdd/issues/11)

**Goal:** Ensure safe operation in production environments.

**Features:**
- **Sandboxed Execution:** Run all generated code in isolated containers
- **Secret Management:** Never expose API keys in logs or UI
- **Audit Logging:** Track all approvals and generations
- **Rate Limiting:** Prevent abuse of API endpoints

### Monitoring and Analytics [#12](https://github.com/auldsyababua/ai-rails-tdd/issues/12)

**Goal:** Understand how AI Rails TDD is being used and improve it.

**Features:**
- Test generation success rates
- Common failure patterns
- Time saved metrics
- Model performance comparison
- Usage dashboards

### Specialized Hugging Face Models for Each Agent [#13](https://github.com/auldsyababua/ai-rails-tdd/issues/13)

**Goal:** Implement a hybrid LLM strategy using specialized self-hosted models for each agent type, maximizing performance while minimizing costs.

**Features:**
- **Model Allocation Strategy:** Pair each agent with models optimized for their specific tasks
  - Planning Agent: WizardLM-2-8x22B-GGUF (Q4_K_M) for complex reasoning
  - Coder Agent: DeepSeek-Coder-33B-Instruct for code generation
  - Unit Tester Agent: StarCoder2-15B-Instruct for test generation
  - Debugger Agent: WizardCoder-33B-V1.1 for error analysis
  - Documentation Agent: OpenHermes-2.5-Mistral-7B for natural writing
  - Code Review Agent: CodeLlama-34B-Instruct for security analysis
  - Refactor Agent: Refact-1.6B for code refactoring
  - n8n Flow Creator Agent: Mistral-7B-OpenOrca for JSON generation
  - Overseer Agent: TinyLlama-1.1B for anomaly detection
- **Local-First Deployment:** Maximize RTX 5090 GPU usage, eliminate API costs
- **Quantization Support:** Optimal quantization (Q4_K_M for 70B models, FP16 for 34B)
- **Hybrid Approach:** Claude 4 Opus as strategic cloud fallback for complex planning
- **Flexible Deployment:** Support for Ollama, llama.cpp, and vLLM
- **VRAM Management:** Intelligent model loading based on available GPU memory
- **Model Performance Monitoring:** Track inference times and quality metrics

---

*Note: These features are adapted from the original AI Rails agent-based system to fit the TDD workflow paradigm. Priority will be given to features that enhance the core TDD experience.*