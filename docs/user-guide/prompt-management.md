# AI Rails Prompt Management Guide

## Overview

AI Rails uses a flexible prompt management system that allows you to customize how the AI agents behave without modifying workflow files.

## Prompt Locations

Prompts are stored as markdown files in the `prompts/` directory:

```
ai-rails-tdd/
└── prompts/
    ├── test_generator.md    # Instructions for test generation
    ├── code_generator.md    # Instructions for code generation
    └── code_reviewer.md     # Instructions for code review (optional)
```

## Editing Prompts

### Method 1: Direct File Editing (Simplest)

1. Navigate to the prompts directory:
   ```bash
   cd /path/to/ai-rails-tdd/prompts
   ```

2. Edit the prompt file:
   ```bash
   # Using your favorite editor
   vim test_generator.md
   # or
   code test_generator.md
   ```

3. Save your changes - they'll be used immediately

### Method 2: Project-Specific Prompts (Most Flexible)

Create custom prompts for a specific project:

1. In your project's `.ai-rails/` directory:
   ```bash
   mkdir .ai-rails/prompts
   ```

2. Copy and customize prompts:
   ```bash
   cp /path/to/ai-rails-tdd/prompts/test_generator.md .ai-rails/prompts/
   # Edit the local copy
   ```

3. The system will use project prompts if they exist, otherwise fall back to defaults

### Method 3: Environment Variable Override

Set prompt content via environment variables:

```bash
export AI_RAILS_TEST_PROMPT="Your custom test generation instructions..."
export AI_RAILS_CODE_PROMPT="Your custom code generation instructions..."
```

## Prompt Structure

Each prompt should follow this structure:

```markdown
# Agent Name Prompt

Brief description of the agent's role.

## Your Task
What the agent should accomplish.

## Requirements
### Category 1
- Requirement 1
- Requirement 2

### Category 2
- Requirement 3
- Requirement 4

## Output Format
How the output should be structured.
```

## Using Custom Prompts in Workflows

### For n8n Workflows

The portable workflows now support loading prompts dynamically. In the workflow:

1. Add a Code node to load prompts:
   ```javascript
   const fs = require('fs');
   const promptPath = process.env.AI_RAILS_HOME + '/prompts/test_generator.md';
   const prompt = fs.readFileSync(promptPath, 'utf8');
   ```

2. Use the loaded prompt in your API calls

### For Command Line

Use the prompt loader utility:

```bash
# List available prompts
python -m utils.prompt_loader list

# Show a specific prompt
python -m utils.prompt_loader show test_generator

# Get prompts directory path
python -m utils.prompt_loader path
```

## Best Practices

### 1. Version Control
- Keep default prompts in the AI Rails repo
- Store project-specific prompts in the project repo
- Use git to track prompt changes

### 2. Testing Prompts
- Test prompts with small examples first
- Keep a test suite to validate prompt effectiveness
- Document what works and what doesn't

### 3. Prompt Engineering Tips
- Be specific about output format
- Include examples when helpful
- Add constraints to prevent unwanted behavior
- Use anti-gaming measures for test generation

### 4. Maintenance
- Review prompts periodically
- Update based on AI model changes
- Share effective prompts with the community

## Examples

### Customizing Test Generation

To make tests more comprehensive, edit `test_generator.md`:

```markdown
### Additional Test Categories
- **Performance Tests**: Add timing assertions
- **Security Tests**: Include input validation checks
- **Concurrency Tests**: Test thread safety
```

### Language-Specific Prompts

Create `test_generator_javascript.md` for JavaScript projects:

```markdown
# JavaScript Test Generator Prompt

Generate tests using Jest framework...
```

### Domain-Specific Prompts

Create `test_generator_web_api.md` for API projects:

```markdown
# Web API Test Generator Prompt

Generate tests for REST endpoints including:
- Status code validation
- Response schema validation
- Authentication tests
- Rate limiting tests
```

## Troubleshooting

### Prompts Not Loading
1. Check `AI_RAILS_HOME` environment variable
2. Verify prompt files exist and are readable
3. Check file permissions

### Prompt Changes Not Taking Effect
1. Clear any caches
2. Restart the workflow
3. Check for syntax errors in prompt files

### Performance Issues
1. Keep prompts concise
2. Avoid unnecessary examples
3. Use specific instructions rather than general guidance