#!/usr/bin/env python3
"""
AI Rails Global Environment Setup
Creates a global configuration that can be imported into any project
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Set
import argparse

# Global config location
GLOBAL_CONFIG_DIR = Path.home() / ".ai-rails"
GLOBAL_ENV_FILE = GLOBAL_CONFIG_DIR / ".env.global"

# Keys that should always come from global config
GLOBAL_KEYS = {
    # MCP API Keys
    "TAVILY_API_KEY",
    "BRAVE_API_KEY", 
    "KAGI_API_KEY",
    "PERPLEXITY_API_KEY",
    "JINA_API_KEY",
    "FIRECRAWL_API_KEY",
    "STACK_EXCHANGE_API_KEY",
    
    # AI Model Keys
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    
    # MCP Services
    "GITHUB_TOKEN",
    
    # Vector/Redis (shared infrastructure)
    "UPSTASH_REDIS_URL",
    "UPSTASH_VECTOR_URL",
    "UPSTASH_VECTOR_TOKEN",
}

# Keys that are typically project-specific
PROJECT_KEYS = {
    "PROJECT_PATH",
    "N8N_BASE_URL",
    "APPROVAL_SERVER_PORT",
    "TEST_RUNNER_PORT",
    "LOG_FILE",
    "WORKFLOW_STATE_TTL",
}


def create_global_config():
    """Create the global configuration directory and template."""
    GLOBAL_CONFIG_DIR.mkdir(exist_ok=True)
    
    if not GLOBAL_ENV_FILE.exists():
        print(f"Creating global config template at {GLOBAL_ENV_FILE}")
        
        template = """# AI Rails Global Configuration
# This file contains API keys and MCP configurations shared across all projects
# Store this in ~/.ai-rails/.env.global

# =============================================================================
# MCP API KEYS (Shared across all projects)
# =============================================================================

# Search Providers
TAVILY_API_KEY=
BRAVE_API_KEY=
KAGI_API_KEY=
PERPLEXITY_API_KEY=

# Content Processing
JINA_API_KEY=
FIRECRAWL_API_KEY=

# Developer Resources
STACK_EXCHANGE_API_KEY=
GITHUB_TOKEN=

# =============================================================================
# AI MODEL KEYS (Shared across all projects)
# =============================================================================
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# =============================================================================
# SHARED INFRASTRUCTURE
# =============================================================================
UPSTASH_REDIS_URL=
UPSTASH_VECTOR_URL=
UPSTASH_VECTOR_TOKEN=

# =============================================================================
# GLOBAL DEFAULTS (Can be overridden per project)
# =============================================================================
LOG_LEVEL=INFO
ENABLE_REDIS_FALLBACK=true
ENABLE_VECTOR_SEARCH=true
"""
        
        GLOBAL_ENV_FILE.write_text(template)
        print(f"✅ Created global config template. Please edit: {GLOBAL_ENV_FILE}")
    else:
        print(f"✅ Global config already exists at: {GLOBAL_ENV_FILE}")


def merge_env_files(global_env: Path, project_env: Path, output_env: Path) -> Dict[str, str]:
    """
    Merge global and project env files, with project taking precedence.
    """
    merged = {}
    
    # Load global config
    if global_env.exists():
        with open(global_env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    merged[key.strip()] = value.strip()
    
    # Load project config (overrides global)
    if project_env.exists():
        with open(project_env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    merged[key.strip()] = value.strip()
    
    # Write merged config
    with open(output_env, 'w') as f:
        f.write("# AI Rails Merged Configuration\n")
        f.write("# Generated from global + project configs\n")
        f.write("# DO NOT EDIT - Edit .env.project or ~/.ai-rails/.env.global instead\n\n")
        
        # Write global keys first
        f.write("# =============================================================================\n")
        f.write("# GLOBAL CONFIGURATION (from ~/.ai-rails/.env.global)\n")
        f.write("# =============================================================================\n")
        for key in sorted(GLOBAL_KEYS):
            if key in merged:
                f.write(f"{key}={merged[key]}\n")
        
        f.write("\n# =============================================================================\n")
        f.write("# PROJECT CONFIGURATION (from .env.project)\n")
        f.write("# =============================================================================\n")
        for key in sorted(merged.keys()):
            if key not in GLOBAL_KEYS:
                f.write(f"{key}={merged[key]}\n")
    
    return merged


def setup_project_env(project_path: Path):
    """Set up environment for a specific project."""
    project_env = project_path / ".env.project"
    final_env = project_path / ".env"
    
    # Create project template if doesn't exist
    if not project_env.exists():
        print(f"Creating project env template at {project_env}")
        
        template = """# AI Rails Project-Specific Configuration
# This file contains settings specific to this project

# =============================================================================
# PROJECT SETTINGS
# =============================================================================
PROJECT_NAME=my-project
PROJECT_PATH=.

# =============================================================================
# LOCAL SERVICES
# =============================================================================
N8N_BASE_URL=http://localhost:5678
APPROVAL_SERVER_PORT=8000
TEST_RUNNER_PORT=8001
WEBHOOK_BASE_URL=http://localhost:8000

# =============================================================================
# PROJECT-SPECIFIC OVERRIDES
# =============================================================================
# Override any global settings here
LOG_FILE=.ai-rails/logs/project.log
WORKFLOW_STATE_TTL=86400
"""
        
        project_env.write_text(template)
        print(f"✅ Created project template. Please edit: {project_env}")
    
    # Merge configurations
    print(f"Merging global and project configurations...")
    merge_env_files(GLOBAL_ENV_FILE, project_env, final_env)
    print(f"✅ Created merged .env file at: {final_env}")


def main():
    parser = argparse.ArgumentParser(description="AI Rails Environment Manager")
    parser.add_argument("command", choices=["init-global", "setup-project", "update"])
    parser.add_argument("--project", help="Project path for setup-project command")
    
    args = parser.parse_args()
    
    if args.command == "init-global":
        create_global_config()
    
    elif args.command == "setup-project":
        project_path = Path(args.project) if args.project else Path.cwd()
        setup_project_env(project_path)
    
    elif args.command == "update":
        # Update all projects with latest global config
        print("Updating all projects with latest global configuration...")
        # Implementation would scan for projects and update them


if __name__ == "__main__":
    main()