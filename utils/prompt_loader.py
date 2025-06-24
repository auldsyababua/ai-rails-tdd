#!/usr/bin/env python3
"""
Prompt Loader Utility for AI Rails TDD
Loads prompts from markdown files for use in workflows
"""

import os
from pathlib import Path
from typing import Dict, Optional


class PromptLoader:
    """Load and manage prompts for AI Rails agents"""

    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize prompt loader

        Args:
            prompts_dir: Path to prompts directory. If None, uses default location.
        """
        if prompts_dir is None:
            # Try to find prompts relative to AI Rails installation
            ai_rails_home = os.environ.get("AI_RAILS_HOME")
            if ai_rails_home:
                prompts_dir = Path(ai_rails_home) / "prompts"
            else:
                # Fallback to relative path
                prompts_dir = Path(__file__).parent.parent / "prompts"

        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, str] = {}

    def load_prompt(self, name: str) -> str:
        """
        Load a prompt by name

        Args:
            name: Name of the prompt (without .md extension)

        Returns:
            The prompt content

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        if name in self._cache:
            return self._cache[name]

        prompt_file = self.prompts_dir / f"{name}.md"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        content = prompt_file.read_text(encoding="utf-8")
        self._cache[name] = content
        return content

    def get_test_generator_prompt(self) -> str:
        """Get the test generator prompt"""
        return self.load_prompt("test_generator")

    def get_code_generator_prompt(self) -> str:
        """Get the code generator prompt"""
        return self.load_prompt("code_generator")

    def get_reviewer_prompt(self) -> str:
        """Get the code reviewer prompt"""
        try:
            return self.load_prompt("code_reviewer")
        except FileNotFoundError:
            return "You are an expert code reviewer. Review the code for quality, security, and correctness."

    def list_prompts(self) -> list[str]:
        """List all available prompts"""
        if not self.prompts_dir.exists():
            return []

        return [f.stem for f in self.prompts_dir.glob("*.md")]

    def reload(self):
        """Clear cache to reload prompts from disk"""
        self._cache.clear()


# Convenience functions for command-line usage
def main():
    """CLI for testing prompt loader"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Rails Prompt Loader")
    parser.add_argument(
        "action", choices=["list", "show", "path"], help="Action to perform"
    )
    parser.add_argument("prompt", nargs="?", help="Prompt name (for show action)")

    args = parser.parse_args()

    loader = PromptLoader()

    if args.action == "list":
        print("Available prompts:")
        for prompt in loader.list_prompts():
            print(f"  - {prompt}")

    elif args.action == "show":
        if not args.prompt:
            print("Error: prompt name required for 'show' action")
            return 1

        try:
            content = loader.load_prompt(args.prompt)
            print(content)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1

    elif args.action == "path":
        print(f"Prompts directory: {loader.prompts_dir}")

    return 0


if __name__ == "__main__":
    exit(main())
