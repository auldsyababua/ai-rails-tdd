#!/usr/bin/env python3
"""
Example usage of OpenRouter client for AI Rails TDD

This script demonstrates how to use OpenRouter to access multiple AI models
including OpenAI, Anthropic, and Perplexity for test generation and code implementation.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our utils
sys.path.append(str(Path(__file__).parent.parent))

from utils.openrouter_client import OpenRouterClient, Message, AVAILABLE_MODELS

async def main():
    """Main example function."""
    
    # Check if API key is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY='sk-or-v1-your-api-key-here'")
        return
    
    # Initialize the client
    client = OpenRouterClient()
    
    try:
        print("🚀 AI Rails TDD - OpenRouter Example")
        print("=" * 50)
        
        # Example planning document
        planning_doc = """
        **Feature Name**: Calculator
        
        **Feature Description**: A simple calculator that can perform basic arithmetic operations.
        
        **Requirements**:
        - Add two numbers
        - Subtract two numbers  
        - Multiply two numbers
        - Divide two numbers (handle division by zero)
        - Support decimal numbers
        - Return float results for division, int for other operations
        """
        
        print("📋 Planning Document:")
        print(planning_doc.strip())
        print("\n" + "=" * 50)
        
        # Step 1: Generate tests using OpenAI GPT-4
        print("🧪 Step 1: Generating tests with OpenAI GPT-4...")
        tests = await client.generate_tests(
            planning_doc, 
            model="openai/gpt-4-turbo-preview"
        )
        print("✅ Tests generated!")
        print("\nGenerated Tests:")
        print(tests)
        print("\n" + "=" * 50)
        
        # Step 2: Generate code using Anthropic Claude
        print("💻 Step 2: Generating implementation with Anthropic Claude...")
        code = await client.generate_code(
            tests, 
            planning_doc, 
            model="anthropic/claude-3.5-sonnet"
        )
        print("✅ Code generated!")
        print("\nGenerated Code:")
        print(code)
        print("\n" + "=" * 50)
        
        # Step 3: Review code using Perplexity
        print("🔍 Step 3: Reviewing code with Perplexity...")
        review = await client.review_code(
            tests, 
            code, 
            model="perplexity/pplx-70b-online"
        )
        print("✅ Code review completed!")
        print("\nCode Review:")
        print(review)
        print("\n" + "=" * 50)
        
        # Step 4: Show available models
        print("📚 Available Models by Provider:")
        for provider, models in AVAILABLE_MODELS.items():
            print(f"\n{provider.upper()}:")
            for model in models:
                print(f"  - {model}")
        
        print("\n" + "=" * 50)
        print("🎉 Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 