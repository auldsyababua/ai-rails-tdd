# OpenRouter Integration Guide

This guide explains how to use OpenRouter with AI Rails TDD to access multiple AI models including OpenAI, Anthropic, Perplexity, and many others through a single API.

## What is OpenRouter?

OpenRouter is a unified API that provides access to hundreds of AI models from various providers. With a single API key, you can use models from:

- **OpenAI**: GPT-4, GPT-3.5-turbo, GPT-4o
- **Anthropic**: Claude-3.5-sonnet, Claude-3-opus, Claude-3-haiku
- **Perplexity**: pplx-7b-online, pplx-70b-online, llama-3.1 models
- **Google**: Gemini Pro, Gemini Flash
- **Meta**: Llama models
- **And many more!**

## Getting Started

### 1. Get an OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to your API keys section
4. Create a new API key (starts with `sk-or-v1-`)

### 2. Set Up Environment Variables

```bash
export OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
```

Or add to your `.env` file:
```
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

### 3. Install Dependencies

The OpenRouter client requires `httpx` for async HTTP requests:

```bash
pip install httpx
```

## Available Models

### OpenAI Models
- `openai/gpt-4-turbo-preview` - Latest GPT-4 model
- `openai/gpt-4` - Standard GPT-4
- `openai/gpt-3.5-turbo` - Fast and cost-effective
- `openai/gpt-4o` - GPT-4 Omni
- `openai/gpt-4o-mini` - Smaller, faster GPT-4

### Anthropic Models
- `anthropic/claude-3.5-sonnet` - Balanced performance and speed
- `anthropic/claude-3-opus` - Most capable Claude model
- `anthropic/claude-3-haiku` - Fastest Claude model
- `anthropic/claude-3.5-haiku` - Latest fast Claude

### Perplexity Models
- `perplexity/pplx-7b-online` - Fast online model
- `perplexity/pplx-70b-online` - More capable online model
- `perplexity/pplx-7b-chat` - Chat-optimized 7B model
- `perplexity/pplx-70b-chat` - Chat-optimized 70B model
- `perplexity/llama-3.1-8b-instruct` - Llama 3.1 8B
- `perplexity/llama-3.1-70b-instruct` - Llama 3.1 70B

### Google Models
- `google/gemini-pro` - Google's Gemini Pro
- `google/gemini-flash-1.5` - Fast Gemini model

### Meta Models
- `meta-llama/llama-3.1-8b-instruct` - Meta's Llama 3.1 8B
- `meta-llama/llama-3.1-70b-instruct` - Meta's Llama 3.1 70B

## Usage Methods

### Method 1: Using the n8n Workflow

1. Import the `ai-rails-openrouter.json` workflow into n8n
2. Configure your OpenRouter API key in the Configuration node
3. Choose your preferred models for each step:
   - **Test Generation**: `openai/gpt-4-turbo-preview`
   - **Code Generation**: `anthropic/claude-3.5-sonnet`
   - **Code Review**: `perplexity/pplx-70b-online`
4. Paste your planning document and execute

### Method 2: Using the Python Client

```python
import asyncio
from utils.openrouter_client import OpenRouterClient

async def main():
    # Initialize client
    client = OpenRouterClient()
    
    try:
        # Generate tests with OpenAI
        tests = await client.generate_tests(
            planning_doc="Your planning document here",
            model="openai/gpt-4-turbo-preview"
        )
        
        # Generate code with Anthropic
        code = await client.generate_code(
            tests=tests,
            planning_doc="Your planning document here",
            model="anthropic/claude-3.5-sonnet"
        )
        
        # Review code with Perplexity
        review = await client.review_code(
            tests=tests,
            implementation=code,
            model="perplexity/pplx-70b-online"
        )
        
        print(f"Tests: {tests}")
        print(f"Code: {code}")
        print(f"Review: {review}")
        
    finally:
        await client.close()

asyncio.run(main())
```

### Method 3: Running the Example

```bash
# Make sure your API key is set
export OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"

# Run the example
python examples/openrouter_example.py
```

## Model Selection Strategy

### For Test Generation
- **Best for complex logic**: `openai/gpt-4-turbo-preview`
- **Cost-effective**: `openai/gpt-3.5-turbo`
- **Fast**: `anthropic/claude-3.5-haiku`

### For Code Generation
- **Best quality**: `anthropic/claude-3.5-sonnet`
- **Most capable**: `anthropic/claude-3-opus`
- **Fast**: `openai/gpt-4o-mini`

### For Code Review
- **Comprehensive**: `perplexity/pplx-70b-online`
- **Fast**: `perplexity/pplx-7b-online`
- **Alternative**: `openai/gpt-4-turbo-preview`

## Pricing

OpenRouter uses a credit-based system. Each model has different pricing:

- **OpenAI GPT-4**: ~$0.03 per 1K tokens
- **Anthropic Claude**: ~$0.015 per 1K tokens
- **Perplexity**: ~$0.001 per 1K tokens
- **Google Gemini**: ~$0.0025 per 1K tokens

You can monitor your usage in the OpenRouter dashboard.

## Advanced Configuration

### Custom Model Selection

You can use any model available on OpenRouter by specifying the full model identifier:

```python
# Use a specific model
tests = await client.generate_tests(
    planning_doc,
    model="anthropic/claude-3-opus"  # Most capable Claude
)
```

### Temperature and Token Control

```python
# Custom chat completion with specific parameters
messages = [
    Message(role="system", content="You are a helpful assistant"),
    Message(role="user", content="Hello!")
]

response = await client.chat_completion(
    model="openai/gpt-4-turbo-preview",
    messages=messages,
    temperature=0.3,  # Lower = more focused
    max_tokens=1000   # Limit response length
)
```

### Error Handling

```python
try:
    response = await client.generate_tests(planning_doc)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Troubleshooting

### Common Issues

1. **Invalid API Key**
   - Ensure your API key starts with `sk-or-v1-`
   - Check that the key is correctly set in environment variables

2. **Rate Limits**
   - OpenRouter has rate limits per model
   - Consider using different models or implementing retry logic

3. **Model Not Available**
   - Some models may be temporarily unavailable
   - Check the OpenRouter status page for model availability

4. **Timeout Issues**
   - Increase the timeout in the client configuration
   - Some models (especially larger ones) take longer to respond

### Getting Help

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Discord](https://discord.gg/openrouter)
- [AI Rails TDD Issues](https://github.com/Auldsyababua/ai-rails-tdd/issues)

## Best Practices

1. **Model Diversity**: Use different models for different tasks to leverage their strengths
2. **Cost Management**: Monitor your usage and choose cost-effective models for simple tasks
3. **Error Handling**: Always implement proper error handling for API calls
4. **Rate Limiting**: Implement retry logic with exponential backoff
5. **Testing**: Test your workflows with different models to find the best combinations

## Example Workflow

Here's a complete example of using OpenRouter with AI Rails TDD:

```python
import asyncio
from utils.openrouter_client import OpenRouterClient

async def tdd_workflow():
    client = OpenRouterClient()
    
    planning_doc = """
    **Feature Name**: Email Validator
    
    **Feature Description**: A utility to validate email addresses.
    
    **Requirements**:
    - Check basic email format (user@domain.com)
    - Validate domain has valid TLD
    - Support international domains
    - Return detailed validation results
    """
    
    try:
        # Step 1: Generate tests with GPT-4
        print("Generating tests...")
        tests = await client.generate_tests(
            planning_doc, 
            model="openai/gpt-4-turbo-preview"
        )
        
        # Step 2: Generate implementation with Claude
        print("Generating code...")
        code = await client.generate_code(
            tests, 
            planning_doc, 
            model="anthropic/claude-3.5-sonnet"
        )
        
        # Step 3: Review with Perplexity
        print("Reviewing code...")
        review = await client.review_code(
            tests, 
            code, 
            model="perplexity/pplx-70b-online"
        )
        
        print("✅ TDD workflow completed!")
        print(f"\nTests:\n{tests}")
        print(f"\nCode:\n{code}")
        print(f"\nReview:\n{review}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(tdd_workflow())
```

This setup gives you the flexibility to use the best model for each specific task while maintaining a single API integration point. 