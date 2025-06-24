#!/usr/bin/env python3
"""
AI Rails TDD - OpenRouter CLI

A command-line interface for using OpenRouter with AI Rails TDD.
This script provides easy access to multiple AI models for test generation,
code implementation, and code review.
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from utils.openrouter_client import OpenRouterClient, AVAILABLE_MODELS

def check_api_key():
    """Check if OpenRouter API key is set."""
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY='sk-or-v1-your-api-key-here'")
        return False
    return True

async def list_models():
    """List all available models."""
    print("📚 Available Models by Provider:")
    print("=" * 50)
    
    for provider, models in AVAILABLE_MODELS.items():
        print(f"\n{provider.upper()}:")
        for model in models:
            print(f"  - {model}")

async def generate_tests(
    planning_doc: str,
    model: str = "openai/gpt-4-turbo-preview",
    output_file: Optional[str] = None
):
    """Generate tests using the specified model."""
    if not check_api_key():
        return
    
    client = OpenRouterClient()
    
    try:
        print(f"🧪 Generating tests with {model}...")
        tests = await client.generate_tests(planning_doc, model)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(tests)
            print(f"✅ Tests saved to {output_file}")
        else:
            print("\nGenerated Tests:")
            print("=" * 50)
            print(tests)
            
    except Exception as e:
        print(f"❌ Error generating tests: {e}")
    finally:
        await client.close()

async def generate_code(
    tests: str,
    planning_doc: str,
    model: str = "anthropic/claude-3.5-sonnet",
    output_file: Optional[str] = None
):
    """Generate implementation code using the specified model."""
    if not check_api_key():
        return
    
    client = OpenRouterClient()
    
    try:
        print(f"💻 Generating code with {model}...")
        code = await client.generate_code(tests, planning_doc, model)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(code)
            print(f"✅ Code saved to {output_file}")
        else:
            print("\nGenerated Code:")
            print("=" * 50)
            print(code)
            
    except Exception as e:
        print(f"❌ Error generating code: {e}")
    finally:
        await client.close()

async def review_code(
    tests: str,
    implementation: str,
    model: str = "perplexity/pplx-70b-online"
):
    """Review code using the specified model."""
    if not check_api_key():
        return
    
    client = OpenRouterClient()
    
    try:
        print(f"🔍 Reviewing code with {model}...")
        review = await client.review_code(tests, implementation, model)
        
        print("\nCode Review:")
        print("=" * 50)
        print(review)
        
    except Exception as e:
        print(f"❌ Error reviewing code: {e}")
    finally:
        await client.close()

async def full_workflow(
    planning_doc: str,
    test_model: str = "openai/gpt-4-turbo-preview",
    code_model: str = "anthropic/claude-3.5-sonnet",
    review_model: str = "perplexity/pplx-70b-online",
    output_dir: Optional[str] = None
):
    """Run the full TDD workflow."""
    if not check_api_key():
        return
    
    client = OpenRouterClient()
    
    try:
        print("🚀 Starting AI Rails TDD Workflow with OpenRouter")
        print("=" * 60)
        
        # Step 1: Generate tests
        print(f"🧪 Step 1: Generating tests with {test_model}...")
        tests = await client.generate_tests(planning_doc, test_model)
        print("✅ Tests generated!")
        
        # Step 2: Generate code
        print(f"💻 Step 2: Generating code with {code_model}...")
        code = await client.generate_code(tests, planning_doc, code_model)
        print("✅ Code generated!")
        
        # Step 3: Review code
        print(f"🔍 Step 3: Reviewing code with {review_model}...")
        review = await client.review_code(tests, code, review_model)
        print("✅ Code review completed!")
        
        # Output results
        print("\n" + "=" * 60)
        print("📋 Results:")
        print("=" * 60)
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save tests
            test_file = os.path.join(output_dir, "generated_tests.py")
            with open(test_file, 'w') as f:
                f.write(tests)
            print(f"📄 Tests saved to: {test_file}")
            
            # Save code
            code_file = os.path.join(output_dir, "generated_code.py")
            with open(code_file, 'w') as f:
                f.write(code)
            print(f"📄 Code saved to: {code_file}")
            
            # Save review
            review_file = os.path.join(output_dir, "code_review.md")
            with open(review_file, 'w') as f:
                f.write(f"# Code Review\n\n{review}")
            print(f"📄 Review saved to: {review_file}")
        else:
            print("\n🧪 Generated Tests:")
            print("-" * 30)
            print(tests)
            
            print("\n💻 Generated Code:")
            print("-" * 30)
            print(code)
            
            print("\n🔍 Code Review:")
            print("-" * 30)
            print(review)
        
        print("\n🎉 Workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
    finally:
        await client.close()

def read_file_content(file_path: str) -> str:
    """Read content from a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="AI Rails TDD - OpenRouter CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available models
  python ai-rails-openrouter.py list-models

  # Generate tests from a planning document
  python ai-rails-openrouter.py generate-tests --planning-doc "planning.txt" --model "openai/gpt-4-turbo-preview"

  # Generate code from tests
  python ai-rails-openrouter.py generate-code --tests "tests.py" --planning-doc "planning.txt" --model "anthropic/claude-3.5-sonnet"

  # Review code
  python ai-rails-openrouter.py review-code --tests "tests.py" --implementation "code.py" --model "perplexity/pplx-70b-online"

  # Run full workflow
  python ai-rails-openrouter.py workflow --planning-doc "planning.txt" --output-dir "output"

  # Run full workflow with custom models
  python ai-rails-openrouter.py workflow --planning-doc "planning.txt" --test-model "openai/gpt-4" --code-model "anthropic/claude-3-opus" --review-model "perplexity/pplx-7b-online"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List models command
    subparsers.add_parser('list-models', help='List all available models')
    
    # Generate tests command
    test_parser = subparsers.add_parser('generate-tests', help='Generate tests from planning document')
    test_parser.add_argument('--planning-doc', required=True, help='Planning document content or file path')
    test_parser.add_argument('--model', default='openai/gpt-4-turbo-preview', help='Model to use for test generation')
    test_parser.add_argument('--output-file', help='Output file for generated tests')
    
    # Generate code command
    code_parser = subparsers.add_parser('generate-code', help='Generate implementation code from tests')
    code_parser.add_argument('--tests', required=True, help='Test content or file path')
    code_parser.add_argument('--planning-doc', required=True, help='Planning document content or file path')
    code_parser.add_argument('--model', default='anthropic/claude-3.5-sonnet', help='Model to use for code generation')
    code_parser.add_argument('--output-file', help='Output file for generated code')
    
    # Review code command
    review_parser = subparsers.add_parser('review-code', help='Review code using AI')
    review_parser.add_argument('--tests', required=True, help='Test content or file path')
    review_parser.add_argument('--implementation', required=True, help='Implementation content or file path')
    review_parser.add_argument('--model', default='perplexity/pplx-70b-online', help='Model to use for code review')
    
    # Full workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run the full TDD workflow')
    workflow_parser.add_argument('--planning-doc', required=True, help='Planning document content or file path')
    workflow_parser.add_argument('--test-model', default='openai/gpt-4-turbo-preview', help='Model for test generation')
    workflow_parser.add_argument('--code-model', default='anthropic/claude-3.5-sonnet', help='Model for code generation')
    workflow_parser.add_argument('--review-model', default='perplexity/pplx-70b-online', help='Model for code review')
    workflow_parser.add_argument('--output-dir', help='Output directory for generated files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle file inputs
    if hasattr(args, 'planning_doc') and os.path.isfile(args.planning_doc):
        args.planning_doc = read_file_content(args.planning_doc)
    
    if hasattr(args, 'tests') and os.path.isfile(args.tests):
        args.tests = read_file_content(args.tests)
    
    if hasattr(args, 'implementation') and os.path.isfile(args.implementation):
        args.implementation = read_file_content(args.implementation)
    
    # Execute commands
    if args.command == 'list-models':
        asyncio.run(list_models())
    elif args.command == 'generate-tests':
        asyncio.run(generate_tests(args.planning_doc, args.model, args.output_file))
    elif args.command == 'generate-code':
        asyncio.run(generate_code(args.tests, args.planning_doc, args.model, args.output_file))
    elif args.command == 'review-code':
        asyncio.run(review_code(args.tests, args.implementation, args.model))
    elif args.command == 'workflow':
        asyncio.run(full_workflow(
            args.planning_doc, 
            args.test_model, 
            args.code_model, 
            args.review_model, 
            args.output_dir
        ))

if __name__ == "__main__":
    main() 