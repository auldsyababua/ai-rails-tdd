# ⚠️ DEPRECATED - Moved to Context Engineer CLI Tool

This repository has been deprecated and its TDD workflow has been integrated into the new **Context Engineer CLI Tool**.

## 🚀 New Repository

Please use the new Context Engineer CLI Tool instead:
- **Repository**: [context-engineer-cli-tool](https://github.com/yourusername/context-engineer-cli-tool)

## What's Included?

All TDD features from ai-rails-tdd have been preserved and enhanced:

### Core TDD Workflow
- ✅ Test-first development approach
- ✅ Agent handoff mechanism (Issue #17)
- ✅ Specialized agents for each phase
- ✅ n8n workflow automation support

### Enhanced Features
- 🎯 Auto-pilot mode that handles the entire TDD cycle
- 📝 Structured project phases (Planning → Testing → Implementation → Review)
- 🔄 Automatic git commits at each phase
- 🤖 Specialized agent models for optimal performance
- 📊 Task tracking and accountability

## Migration Guide

1. **Install Context Engineer CLI Tool**:
   ```bash
   git clone https://github.com/yourusername/context-engineer-cli-tool
   cd context-engineer-cli-tool
   ./setup.sh
   ```

2. **Create a TDD project**:
   ```bash
   # Interactive setup
   ce
   
   # Choose "New Project" → "API/Microservice" (or your project type)
   # The TDD workflow is built into the phases
   ```

3. **Use Auto-pilot for TDD**:
   ```bash
   # Automatically progresses through TDD phases
   cea
   
   # Phases include:
   # - Planning (requirements)
   # - Testing (test generation)
   # - Implementation (code to pass tests)
   # - Review & Refactoring
   ```

## Where Are the Agents?

All specialized agents from ai-rails-tdd are documented as enhancement issues:

- **Debugger Agent**: Issue #11
- **Documentation Agent**: Issue #12
- **Refactor Agent**: Issue #13
- **n8n Flow Creator**: Issue #14
- **Task Tracker MCP**: Issue #15
- **Overseer Agent**: Issue #16
- **Agent Handoff**: Issue #17

## Key Improvements

1. **Integrated Workflow**: No need for separate n8n setup - it's all in the CLI
2. **Better Handoffs**: Automatic context passing between phases
3. **Session Persistence**: Resume where you left off
4. **Local-First**: Works with local LLMs via Ollama
5. **Safety Rails**: Built-in mesa-optimization prevention

## n8n Integration

If you still want to use n8n workflows:
- Issue #14 covers the n8n Flow Creator Agent
- Issue #18 includes local n8n as an optional service bundle
- The system can generate n8n workflows for your projects

## Questions?

Please open issues in the new repository. All future development will happen there.

---

Thank you for using ai-rails-tdd! The Context Engineer CLI Tool carries forward all its best features with a more streamlined experience. 🚀