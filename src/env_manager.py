"""
Environment Manager for AI Rails TDD
Handles hierarchical .env file loading and merging
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv, dotenv_values


class EnvManager:
    """
    Manages hierarchical environment configuration for AI Rails.
    
    Loading order (later overrides earlier):
    1. Global config (~/.ai-rails/.env.global)
    2. Project defaults (.env.defaults)
    3. Project config (.env.project)
    4. Local overrides (.env.local)
    5. Main .env file (.env)
    """
    
    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.global_config_dir = Path.home() / ".ai-rails"
        self.loaded_files: List[Path] = []
        
    def load_hierarchical_env(self) -> Dict[str, str]:
        """
        Load environment variables in hierarchical order.
        Returns the final merged configuration.
        """
        # Define the hierarchy
        env_files = [
            self.global_config_dir / ".env.global",  # Global AI Rails config
            self.project_path / ".env.defaults",     # Project defaults (from template)
            self.project_path / ".env.project",      # Project-specific settings
            self.project_path / ".env.local",        # Local machine overrides
            self.project_path / ".env",              # Main env file (highest priority)
        ]
        
        merged_config = {}
        
        for env_file in env_files:
            if env_file.exists():
                # Load without overriding os.environ yet
                file_config = dotenv_values(env_file)
                merged_config.update(file_config)
                self.loaded_files.append(env_file)
                print(f"✓ Loaded: {env_file}")
        
        # Now load everything into os.environ
        for key, value in merged_config.items():
            if value is not None:  # Don't set empty values
                os.environ[key] = value
        
        return merged_config
    
    def create_global_template(self) -> Path:
        """Create the global configuration template if it doesn't exist."""
        self.global_config_dir.mkdir(exist_ok=True)
        global_env = self.global_config_dir / ".env.global"
        
        if not global_env.exists():
            template = """# AI Rails Global Configuration
# This file contains API keys and MCP configurations shared across all projects
# These settings will be automatically loaded by all AI Rails projects

# =============================================================================
# MCP API KEYS (Shared across all projects)
# =============================================================================

# Search Providers (via mcp-omnisearch)
TAVILY_API_KEY=tvly-...your-key-here...
BRAVE_API_KEY=BSA...your-key-here...
KAGI_API_KEY=...your-key-here...
PERPLEXITY_API_KEY=pplx-...your-key-here...

# Content Processing
JINA_API_KEY=jina_...your-key-here...
FIRECRAWL_API_KEY=fc-...your-key-here...

# Developer Resources  
STACK_EXCHANGE_API_KEY=...your-key-here...
GITHUB_TOKEN=ghp_...your-token-here...

# =============================================================================
# AI MODEL KEYS (Shared across all projects)
# =============================================================================
OPENAI_API_KEY=sk-...your-key-here...
ANTHROPIC_API_KEY=sk-ant-...your-key-here...

# =============================================================================
# SHARED INFRASTRUCTURE (Upstash)
# =============================================================================
UPSTASH_REDIS_URL=rediss://:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
UPSTASH_VECTOR_URL=https://YOUR_VECTOR_ENDPOINT.upstash.io
UPSTASH_VECTOR_TOKEN=YOUR_VECTOR_TOKEN

# =============================================================================
# GLOBAL DEFAULTS (Can be overridden per project)
# =============================================================================
LOG_LEVEL=INFO
ENABLE_REDIS_FALLBACK=true
ENABLE_VECTOR_SEARCH=true
REDIS_MAX_POOL_SIZE=50

# MCP Settings
MCP_ENABLED=true
"""
            global_env.write_text(template)
            print(f"✅ Created global config template at: {global_env}")
        
        return global_env
    
    def create_project_template(self) -> Path:
        """Create a project-specific template."""
        project_env = self.project_path / ".env.project"
        
        if not project_env.exists():
            template = f"""# AI Rails Project-Specific Configuration
# This file contains settings specific to this project
# It will be loaded AFTER the global config, so values here override global ones

# =============================================================================
# PROJECT IDENTIFICATION
# =============================================================================
PROJECT_NAME={self.project_path.name}
PROJECT_PATH={self.project_path}

# =============================================================================
# LOCAL SERVICES (Project-specific ports)
# =============================================================================
N8N_BASE_URL=http://localhost:5678
APPROVAL_SERVER_PORT=8000
TEST_RUNNER_PORT=8001
WEBHOOK_BASE_URL=http://localhost:8000
WEBHOOK_TIMEOUT=30

# =============================================================================
# TEST & CODE GENERATION SETTINGS
# =============================================================================
TEST_GENERATION_TEMPERATURE=0.7
CODE_GENERATION_TEMPERATURE=0.3
TEST_GENERATION_MAX_TOKENS=6000
CODE_GENERATION_MAX_TOKENS=8000
TEST_EXECUTION_TIMEOUT=30
MAX_TEST_RETRIES=3

# =============================================================================
# PROJECT-SPECIFIC PATHS
# =============================================================================
LOG_FILE=.ai-rails/logs/{self.project_path.name}.log

# =============================================================================
# PROJECT OVERRIDES
# =============================================================================
# Uncomment to override any global settings for this project
# WORKFLOW_STATE_TTL=86400
# APPROVAL_REQUEST_TTL=3600
"""
            project_env.write_text(template)
            print(f"✅ Created project template at: {project_env}")
        
        return project_env
    
    def init_project_env(self, copy_from_existing: bool = True):
        """Initialize environment for a new project."""
        # Create global template if needed
        self.create_global_template()
        
        # Create project template
        self.create_project_template()
        
        # Create .env.defaults from the example
        example_file = self.project_path / ".env.example"
        defaults_file = self.project_path / ".env.defaults"
        
        if example_file.exists() and not defaults_file.exists():
            import shutil
            shutil.copy(example_file, defaults_file)
            print(f"✅ Created .env.defaults from .env.example")
        
        # Create .gitignore entries
        gitignore = self.project_path / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            entries_to_add = []
            
            for entry in [".env", ".env.local", ".env.project"]:
                if entry not in content:
                    entries_to_add.append(entry)
            
            if entries_to_add:
                with open(gitignore, 'a') as f:
                    f.write("\n# AI Rails environment files\n")
                    for entry in entries_to_add:
                        f.write(f"{entry}\n")
                print(f"✅ Updated .gitignore with env entries")
        
        # Load the hierarchical config
        config = self.load_hierarchical_env()
        
        print(f"\n✅ Environment initialized!")
        print(f"   Loaded {len(self.loaded_files)} config files")
        print(f"   Total settings: {len(config)}")
        
        return config
    
    def show_config_info(self):
        """Display information about the current configuration."""
        print("\n🔍 AI Rails Environment Configuration")
        print("=" * 50)
        
        # Check which files exist
        files = [
            (self.global_config_dir / ".env.global", "Global Config"),
            (self.project_path / ".env.defaults", "Project Defaults"),
            (self.project_path / ".env.project", "Project Config"),
            (self.project_path / ".env.local", "Local Overrides"),
            (self.project_path / ".env", "Main Config"),
        ]
        
        for file, desc in files:
            if file.exists():
                size = file.stat().st_size
                print(f"✓ {desc:20} {file} ({size} bytes)")
            else:
                print(f"✗ {desc:20} {file} (not found)")
        
        print("\nLoading order: Global → Defaults → Project → Local → Main")
        print("Later files override earlier ones\n")


# Convenience function for use in other modules
def load_ai_rails_env(project_path: Optional[Path] = None) -> Dict[str, str]:
    """Load AI Rails environment with hierarchical configuration."""
    manager = EnvManager(project_path)
    return manager.load_hierarchical_env()