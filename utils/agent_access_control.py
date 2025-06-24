"""
Agent Access Control Module

Enforces access restrictions for AI agents to enable blind testing scenarios.
Prevents agents from accessing test implementation details unless explicitly provided.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Union
import json


class AgentAccessControl:
    """Controls file access for AI agents based on restriction rules."""
    
    def __init__(self, config_file: str = ".agent-restrictions"):
        """Initialize with restriction configuration."""
        self.restricted_folders = [
            "inputs-to-outputs/redis-integration-actual",
            "inputs-to-outputs/*-actual",
            "inputs-to-outputs/*-blind", 
            "inputs-to-outputs/blind-test-scenarios",
            "test-isolation",
            "agent-sandbox",
            "blind-tests"
        ]
        self.restricted_files = [
            "*.secret",
            ".env.production",
            "secrets.json"
        ]
        self.restricted_patterns = [
            "**/blind-test-*",
            "**/isolated-*",
            "**/sandbox-*"
        ]
        
        # Load additional restrictions from config file if exists
        self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> None:
        """Load additional restrictions from configuration file."""
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    # Parse YAML-like format
                    content = f.read()
                    # Simple parsing logic here
                    # In production, use proper YAML parser
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
    
    def is_path_restricted(self, file_path: Union[str, Path]) -> bool:
        """Check if a given path is restricted."""
        path = Path(file_path).resolve()
        path_str = str(path)
        
        # Check against restricted folders
        for folder_pattern in self.restricted_folders:
            if self._matches_pattern(path_str, folder_pattern):
                return True
        
        # Check against restricted files
        filename = path.name
        for file_pattern in self.restricted_files:
            if fnmatch.fnmatch(filename, file_pattern):
                return True
        
        # Check against restricted patterns
        for pattern in self.restricted_patterns:
            if self._matches_pattern(path_str, pattern):
                return True
        
        return False
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches a glob pattern."""
        # Handle different pattern types
        if '*' in pattern or '?' in pattern:
            # It's a glob pattern
            return fnmatch.fnmatch(path, pattern) or pattern.replace('/', os.sep) in path
        else:
            # It's a literal path
            return pattern in path or pattern.replace('/', os.sep) in path
    
    def validate_access(self, file_path: Union[str, Path], operation: str = "read") -> tuple[bool, str]:
        """
        Validate if access to a file is allowed.
        
        Returns:
            Tuple of (is_allowed, reason_if_denied)
        """
        if self.is_path_restricted(file_path):
            return False, f"Access denied: {file_path} is in a restricted directory for blind testing. Please paste the content directly into the conversation."
        
        return True, "Access allowed"
    
    def safe_read(self, file_path: Union[str, Path]) -> str:
        """Read file content only if access is allowed."""
        is_allowed, reason = self.validate_access(file_path, "read")
        
        if not is_allowed:
            raise PermissionError(reason)
        
        with open(file_path, 'r') as f:
            return f.read()
    
    def safe_write(self, file_path: Union[str, Path], content: str) -> None:
        """Write file content only if access is allowed."""
        is_allowed, reason = self.validate_access(file_path, "write")
        
        if not is_allowed:
            raise PermissionError(reason)
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def safe_list_dir(self, dir_path: Union[str, Path]) -> List[str]:
        """List directory contents only if access is allowed."""
        is_allowed, reason = self.validate_access(dir_path, "list")
        
        if not is_allowed:
            raise PermissionError(reason)
        
        return os.listdir(dir_path)
    
    def get_restriction_message(self) -> str:
        """Get a friendly message about access restrictions."""
        return (
            "Access Restriction Notice:\n"
            "Certain directories are restricted for blind testing purposes.\n"
            "If you need to work with content from these directories,\n"
            "please paste the specific content directly into our conversation.\n"
            "Restricted patterns include: *-actual/, *-blind/, test-isolation/, etc."
        )


# Singleton instance for easy import
access_control = AgentAccessControl()


# Convenience functions
def is_restricted(file_path: Union[str, Path]) -> bool:
    """Check if a path is restricted."""
    return access_control.is_path_restricted(file_path)


def safe_read(file_path: Union[str, Path]) -> str:
    """Read file with access control."""
    return access_control.safe_read(file_path)


def safe_write(file_path: Union[str, Path], content: str) -> None:
    """Write file with access control."""
    access_control.safe_write(file_path, content)


# Example usage and testing
if __name__ == "__main__":
    # Test the access control
    test_paths = [
        "/Users/colinaulds/Desktop/projects/ai-rails-tdd/inputs-to-outputs/redis-integration-actual/test.py",
        "/Users/colinaulds/Desktop/projects/ai-rails-tdd/inputs-to-outputs/feature-blind/data.json",
        "/Users/colinaulds/Desktop/projects/ai-rails-tdd/src/main.py",
        "/Users/colinaulds/Desktop/projects/ai-rails-tdd/test-isolation/scenario1.py",
        "/Users/colinaulds/Desktop/projects/ai-rails-tdd/README.md"
    ]
    
    print("Testing Agent Access Control:\n")
    for path in test_paths:
        is_allowed, reason = access_control.validate_access(path)
        status = "✅ ALLOWED" if is_allowed else "❌ RESTRICTED"
        print(f"{status}: {path}")
        if not is_allowed:
            print(f"   Reason: {reason}\n")