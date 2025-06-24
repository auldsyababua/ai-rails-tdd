"""
OpenRouter Client for AI Rails TDD

This module provides a client for making calls to various AI models through OpenRouter,
including OpenAI, Anthropic, Perplexity, and many others.
"""

import os
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter client."""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-4-turbo-preview"
    timeout: int = 60

@dataclass
class Message:
    """Chat message for OpenRouter API."""
    role: str  # "system", "user", "assistant"
    content: str

class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self, config: Optional[OpenRouterConfig] = None):
        """Initialize the OpenRouter client."""
        if config is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required")
            config = OpenRouterConfig(api_key=api_key)
        
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    async def chat_completion(
        self, 
        model: str,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make a chat completion request to OpenRouter."""
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-rails-tdd.com",
            "X-Title": "AI Rails TDD"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        response = await self.client.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    async def generate_tests(
        self, 
        planning_doc: str, 
        model: str = "openai/gpt-4-turbo-preview"
    ) -> str:
        """Generate tests using the specified model."""
        
        messages = [
            Message(
                role="system",
                content="""You are an expert test engineer specializing in Test-Driven Development (TDD). 
                Generate comprehensive Python tests using pytest. Follow TDD principles:
                1. Test behavior, not implementation
                2. Include edge cases and error handling
                3. Use descriptive test names: test_{what}_when_{condition}_then_{result}
                4. Add docstrings to explain each test
                5. Include all necessary imports
                
                Output ONLY the test code, no explanations."""
            ),
            Message(
                role="user",
                content=f"Planning Document:\n{planning_doc}\n\nGenerate comprehensive tests for this feature."
            )
        ]
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )
        
        return response["choices"][0]["message"]["content"]
    
    async def generate_code(
        self, 
        tests: str, 
        planning_doc: str, 
        model: str = "anthropic/claude-3.5-sonnet"
    ) -> str:
        """Generate implementation code using the specified model."""
        
        messages = [
            Message(
                role="system",
                content="""You are an expert Python developer implementing code using Test-Driven Development. 
                Write clean, efficient code that passes all provided tests. Requirements:
                1. Make ALL tests pass
                2. Use type hints
                3. Include docstrings
                4. Handle all edge cases
                5. Follow PEP 8
                6. No test-specific hacks
                
                Output ONLY the implementation code."""
            ),
            Message(
                role="user",
                content=f"Tests to pass:\n{tests}\n\nPlanning Document:\n{planning_doc}\n\nWrite the implementation."
            )
        ]
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=4000
        )
        
        return response["choices"][0]["message"]["content"]
    
    async def review_code(
        self, 
        tests: str, 
        implementation: str, 
        model: str = "perplexity/pplx-70b-online"
    ) -> str:
        """Review code using the specified model."""
        
        messages = [
            Message(
                role="system",
                content="You are an expert code reviewer. Analyze the implementation code for quality, security, and adherence to best practices. Provide a brief assessment."
            ),
            Message(
                role="user",
                content=f"Review this implementation:\n\nTests:\n{tests}\n\nImplementation:\n{implementation}\n\nProvide a brief code review focusing on quality and potential issues."
            )
        ]
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        return response["choices"][0]["message"]["content"]
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Available models for different providers
AVAILABLE_MODELS = {
    "openai": [
        "openai/gpt-4-turbo-preview",
        "openai/gpt-4",
        "openai/gpt-3.5-turbo",
        "openai/gpt-4o",
        "openai/gpt-4o-mini"
    ],
    "anthropic": [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3.5-haiku"
    ],
    "perplexity": [
        "perplexity/pplx-7b-online",
        "perplexity/pplx-70b-online",
        "perplexity/pplx-7b-chat",
        "perplexity/pplx-70b-chat",
        "perplexity/llama-3.1-8b-instruct",
        "perplexity/llama-3.1-70b-instruct"
    ],
    "google": [
        "google/gemini-pro",
        "google/gemini-flash-1.5"
    ],
    "meta": [
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.1-70b-instruct"
    ]
}

# Example usage
async def example_usage():
    """Example of how to use the OpenRouter client."""
    
    # Initialize client
    client = OpenRouterClient()
    
    try:
        # Example planning document
        planning_doc = """
        **Feature Name**: Calculator
        
        **Feature Description**: A simple calculator that can perform basic arithmetic operations.
        
        **Requirements**:
        - Add two numbers
        - Subtract two numbers
        - Multiply two numbers
        - Divide two numbers (handle division by zero)
        """
        
        # Generate tests using OpenAI
        tests = await client.generate_tests(
            planning_doc, 
            model="openai/gpt-4-turbo-preview"
        )
        print("Generated Tests:")
        print(tests)
        print("\n" + "="*50 + "\n")
        
        # Generate code using Anthropic
        code = await client.generate_code(
            tests, 
            planning_doc, 
            model="anthropic/claude-3.5-sonnet"
        )
        print("Generated Code:")
        print(code)
        print("\n" + "="*50 + "\n")
        
        # Review code using Perplexity
        review = await client.review_code(
            tests, 
            code, 
            model="perplexity/pplx-70b-online"
        )
        print("Code Review:")
        print(review)
        
    finally:
        await client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 