# AI Rails Global Environment Setup

This guide explains how to set up a global environment configuration that will be shared across all your AI Rails TDD projects.

## Overview

The hierarchical environment system allows you to:
- 🌍 **Global Config**: Store API keys once, use everywhere
- 📁 **Project Config**: Override settings per project
- 🔒 **Local Config**: Machine-specific settings (git-ignored)
- 🎯 **Smart Merging**: Later files override earlier ones

## Environment Loading Order

```
~/.ai-rails/.env.global     # Your API keys (shared)
    ↓
.env.defaults               # Project template defaults
    ↓
.env.project               # Project-specific settings
    ↓
.env.local                 # Local machine overrides
    ↓
.env                       # Final override (optional)
```

## Quick Setup

### 1. Install in Your Project

From your AI Rails TDD directory, run:

```bash
# For auto-report-tdd project
./scratch/install_with_global_env.sh /Users/colinaulds/Desktop/projects/auto-report-tdd
```

Or create an alias for easy use:
```bash
# Add to ~/.zshrc or ~/.bashrc
alias install-ai-rails="/Users/colinaulds/Desktop/projects/ai-rails-tdd/scratch/install_with_global_env.sh"

# Then use it anywhere
cd ~/projects/my-new-project
install-ai-rails .
```

### 2. Set Up Global Config (One Time)

Edit `~/.ai-rails/.env.global` and add your API keys:

```bash
# Edit the global config
nano ~/.ai-rails/.env.global

# Or open in your editor
code ~/.ai-rails/.env.global
```

Add your keys:
```env
# MCP API Keys
OPENAI_API_KEY=sk-...your-actual-key...
TAVILY_API_KEY=tvly-...your-actual-key...
BRAVE_API_KEY=BSA...your-actual-key...
GITHUB_TOKEN=ghp_...your-actual-token...

# Infrastructure
UPSTASH_REDIS_URL=rediss://...your-url...
UPSTASH_VECTOR_URL=https://...your-url...
UPSTASH_VECTOR_TOKEN=...your-token...
```

### 3. Configure Project Settings

Edit `.env.project` in your project:

```bash
cd your-project/ai-rails-tdd
nano .env.project
```

Set project-specific values:
```env
PROJECT_NAME=auto-report-tdd
N8N_BASE_URL=http://localhost:5678
APPROVAL_SERVER_PORT=8000
TEST_RUNNER_PORT=8001
```

## File Purposes

| File | Purpose | Git Status | When to Edit |
|------|---------|------------|--------------|
| `~/.ai-rails/.env.global` | API keys & shared config | N/A (home dir) | Once, when you get new keys |
| `.env.defaults` | Template from .env.example | ✓ Committed | Rarely, for new defaults |
| `.env.project` | Project-specific settings | ✓ Committed | Per project setup |
| `.env.local` | Your machine overrides | ✗ Ignored | Local preferences |
| `.env` | Final overrides | ✗ Ignored | Testing/debugging |

## Benefits

1. **🔑 Single Key Management**: Update API keys in one place
2. **🚀 Fast Project Setup**: New projects get keys automatically  
3. **👥 Team Friendly**: Share .env.project, keep keys private
4. **🔄 Easy Updates**: Change keys globally without touching projects
5. **🎛️ Flexible**: Override anything at any level

## Example Workflow

1. **New Project Setup**:
   ```bash
   cd ~/projects/new-feature
   install-ai-rails .
   cd ai-rails-tdd
   source venv/bin/activate
   # Ready to go with all your API keys!
   ```

2. **Update an API Key**:
   ```bash
   # Edit global config
   nano ~/.ai-rails/.env.global
   # All projects get the new key automatically
   ```

3. **Project-Specific Override**:
   ```bash
   # In .env.project
   LOG_LEVEL=DEBUG  # Just for this project
   ```

4. **Local Testing**:
   ```bash
   # In .env.local (git-ignored)
   OPENAI_MODEL=gpt-4-turbo  # Test with different model
   ```

## Troubleshooting

**Missing Keys?**
```bash
# Check which files are loaded
cd your-project/ai-rails-tdd
python -c "from src.env_manager import EnvManager; EnvManager().show_config_info()"
```

**See Merged Config**:
```bash
python -c "
from src.env_manager import load_ai_rails_env
config = load_ai_rails_env()
for k, v in sorted(config.items()):
    print(f'{k}={v[:20]}...' if len(v) > 20 else f'{k}={v}')
"
```

## Security Notes

- ✅ Global config is in your home directory (not in any git repo)
- ✅ .env.local and .env are git-ignored by default
- ✅ .env.project can be committed (no secrets, just settings)
- ⚠️ Never commit files with actual API keys

## Next Steps

1. Run the installation script for your project
2. Copy your API keys to `~/.ai-rails/.env.global`
3. Configure project-specific settings in `.env.project`
4. Start building with AI Rails TDD!

Need help? Check the verification:
```bash
cd your-project/ai-rails-tdd
python scratch/verify_setup.py
```