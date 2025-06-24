# Getting Started with AI Rails TDD

This guide covers installation, configuration, and your first TDD workflow.

## Prerequisites

Before installing AI Rails TDD, ensure you have:

- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **n8n** (workflow automation) - [Installation Guide](https://docs.n8n.io/hosting/installation/)
- **Git** (for cloning the repository)
- **16GB+ RAM** (if using local models with Ollama)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Auldsyababua/ai-rails-tdd.git
cd ai-rails-tdd
```

### 2. Install the CLI Tool

```bash
sudo ./install.sh
```

This installs the `ai-rails` command globally on your system.

### 3. Set Up Your Language Model

You have two options:

#### Option A: Use OpenAI (Easiest)

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   USE_OPENAI=true
   OPENAI_API_KEY=sk-your-key-here
   ```

#### Option B: Use Ollama (Local, Free)

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Download a model:
   ```bash
   ollama pull qwen2.5-coder:32b
   ```
3. Configure `.env`:
   ```
   USE_OLLAMA=true
   OLLAMA_BASE_URL=http://localhost:11434
   ```

### 4. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Set Up n8n

1. Install n8n locally:
   ```bash
   npm install -g n8n
   n8n start
   ```
   
2. Or use Docker:
   ```bash
   docker run -it --rm \
     --name n8n \
     -p 5678:5678 \
     n8nio/n8n
   ```

3. Access n8n at http://localhost:5678

## Quick Start

### 1. Initialize Your Project

Navigate to any project directory and run:

```bash
cd /path/to/your/project
ai-rails init
```

This creates a `.ai-rails/` directory in your project for all TDD workflows.

### 2. Create a Planning Document

The planning document is created through an interactive conversation with an AI assistant:

1. **Open your AI assistant** (one of these recommended tools):
   - Claude Code (Opus 4) - Recommended, especially with MCP tools
   - GPT-4 Turbo or GPT-o3
   - Gemini 2.5 Pro
   - Other advanced reasoning models

2. **Start the conversation** by copying the planning template:
   ```bash
   cat planning-doc-template.md
   ```

3. **Paste the template** into your AI assistant and describe your feature or app idea:
   ```
   "I'm using the AI Rails TDD system. Here's my planning template. 
   I want to build [describe your feature/app here]. Please help me 
   complete this planning document by asking me any questions you need 
   to fully understand the requirements."
   ```

4. **Have a conversation** where the AI will:
   - Ask clarifying questions about your requirements
   - Probe for edge cases you might not have considered
   - Research best practices and common pitfalls
   - Help you identify technical risks
   - Ensure all sections are thoroughly completed

5. **Save the completed document**:
   ```bash
   # Save the AI's final output as:
   planning-doc-[feature-name].md
   ```

**Example conversation starter:**
```
"I want to build an email validator function that checks if email 
addresses are valid. It should handle common formats but also edge 
cases like international domains."
```

The AI will then help you build a comprehensive planning document that covers all aspects needed for successful TDD implementation.

### 3. Start AI Rails Services

From the ai-rails-tdd directory:

```bash
cd /path/to/ai-rails-tdd
./scripts/start-services.sh
```

### 4. Run the TDD Workflow

1. Open n8n in your browser: http://localhost:5678

2. Import the appropriate workflow:
   - For OpenAI: `workflows/ai-rails-portable-openai.json`
   - For Ollama: `workflows/ai-rails-portable.json`
   
   The workflow automatically:
   - Reads API keys from your `.env` file
   - Uses the project path from `.ai-rails/config.json`
   - Configures all service endpoints

3. Execute the workflow:
   - Click "Execute Workflow"
   - Paste your completed planning document when prompted
   - The workflow will:
     - Generate comprehensive tests
     - Present them for your approval at http://localhost:8000
     - Generate implementation code after approval
     - Run the tests and show results

### 5. Use the Generated Code

After successful execution:

1. Find your generated files in `.ai-rails/`:
   ```
   your-project/.ai-rails/
   ├── tests/
   │   ├── generated.py    # AI-generated tests
   │   └── approved.py     # Your approved version
   └── implementation/
       └── generated.py    # AI-generated code
   ```

2. Copy to your project:
   ```bash
   cp .ai-rails/tests/approved.py tests/test_email_validator.py
   cp .ai-rails/implementation/generated.py src/email_validator.py
   ```

3. Run the tests locally:
   ```bash
   pytest tests/test_email_validator.py
   ```

## Configuration

The system can be configured through environment variables in your `.env` file:

### Model Configuration

```bash
# OpenAI Configuration
USE_OPENAI=true
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# OR Ollama Configuration
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:32b

# OR Custom Model Server
USE_CUSTOM_MODEL=true
CUSTOM_MODEL_URL=http://your-server:8080
CUSTOM_MODEL_NAME=your-model
CUSTOM_MODEL_AUTH_HEADER=Authorization
CUSTOM_MODEL_AUTH_TOKEN=Bearer your-token
```

### Service Configuration

```bash
# Service URLs (defaults shown)
N8N_BASE_URL=http://localhost:5678
APPROVAL_SERVER_URL=http://localhost:8000
TEST_RUNNER_URL=http://localhost:8001

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=.ai-rails/logs/ai-rails.log
```

### Test Generation Settings

```bash
# Temperature settings
TEST_GENERATION_TEMPERATURE=0.7
CODE_GENERATION_TEMPERATURE=0.3

# Timeout settings (in seconds)
TEST_GENERATION_TIMEOUT=120
CODE_GENERATION_TIMEOUT=180
TEST_EXECUTION_TIMEOUT=60
```

### Project-Specific Overrides

Create a `.ai-rails/config.json` in your project to override settings:

```json
{
  "model": {
    "temperature": 0.5,
    "max_tokens": 4000
  },
  "testing": {
    "framework": "pytest",
    "coverage_threshold": 80
  }
}
```

## Troubleshooting

### Permission Denied
If you get permission errors during installation:
```bash
chmod +x install.sh
sudo ./install.sh
```

### Port Already in Use
If ports 8000 or 8001 are already in use:
1. Edit `.env` to change the ports:
   ```
   APPROVAL_SERVER_PORT=8080
   TEST_RUNNER_PORT=8081
   ```
2. Update your n8n workflow accordingly

### Python Version Issues
If you have multiple Python versions:
```bash
python3.8 -m venv venv
# or
python3.9 -m venv venv
```

### Verify Installation

Run the following to verify everything is installed correctly:

```bash
# Check CLI installation
ai-rails --help

# Start services
cd ai-rails-tdd
./scripts/start-services.sh
```

You should see:
- Approval server running on port 8000
- Test runner running on port 8001

## Next Steps

- Learn about [Workflows](user-guide/workflows.md)
- Customize [Prompts](user-guide/prompt-management.md)
- Read the [Architecture](developer/architecture.md)

## Need Help?

- Check [Troubleshooting](user-guide/troubleshooting.md)
- Read the [FAQ](misc/faq.md)
- Open an [Issue](https://github.com/Auldsyababua/ai-rails-tdd/issues)