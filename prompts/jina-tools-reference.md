# Jina.ai Tools Reference Guide

## Complete Jina.ai Tool Suite Available to All Agents

### 1. **Jina Reader API** (`r.jina.ai`)
**Purpose**: Convert any URL to clean, LLM-ready Markdown
**Key Features**:
- Handles JavaScript-rendered content
- Processes iframes and Shadow DOM
- Automatic image captioning
- Table structure preservation
- Authentication support via cookies
- Stream mode for large pages
- Locale-specific rendering

**Usage Examples**:
```python
# Basic usage
jina_reader_process(url="https://docs.example.com/api")

# Advanced extraction
jina_reader_process(
    url=["https://docs.example.com/api", "https://docs.example.com/guide"],
    extract_depth="advanced"  # More comprehensive but costs more credits
)

# For authentication-gated content
# Headers: X-Cookie, X-Locale, X-No-Gfm, X-Stream
```

### 2. **Jina Grounding API** (`g.jina.ai`)
**Purpose**: Real-time fact-checking and hallucination reduction
**Key Features**:
- Factuality scores (0-1) for any statement
- Real-time web search verification
- Detailed reasoning with citations
- ~30 second processing time
- Cost: ~$0.006 per request

**Usage Examples**:
```python
# Fact-check technical claims
jina_grounding_enhance(
    content="Redis version 7.0 supports JSON data types natively"
)
# Returns: factuality_score, reasoning, references

# Verify multiple claims
jina_grounding_enhance(
    content="""
    1. Python 3.12 has a 30% performance improvement
    2. FastAPI is faster than Flask for async operations
    3. PostgreSQL 16 supports vector operations
    """
)
```

### 3. **Jina Search API** (`s.jina.ai`)
**Purpose**: AI-powered web search with reasoning
**Key Features**:
- Search, read, and reason until best answer found
- Integrates with Reader API automatically
- Optimized for technical queries
- Returns structured results

**Usage Pattern**:
```python
# Used internally by grounding API
# Searches for relevant documents
# Extracts content via Reader API
# Synthesizes answer with citations
```

### 4. **Jina Embeddings API**
**Purpose**: State-of-the-art text and multimodal embeddings
**Models Available**:
- **jina-embeddings-v3**: 
  - 89 languages support
  - 8192 token context
  - #2 on MTEB English leaderboard
- **jina-clip-v2**:
  - Multimodal (text + image)
  - Text-text, text-image, image-image retrieval
  - 3% improvement over v1

**Usage Examples**:
```python
# Text embedding
embeddings = jina_embed(
    texts=["code snippet 1", "documentation excerpt"],
    model="jina-embeddings-v3"
)

# Multimodal embedding
embeddings = jina_embed(
    inputs=["text description", image_data],
    model="jina-clip-v2"
)
```

### 5. **Jina Reranker API**
**Purpose**: Optimize search result relevance
**Key Features**:
- Re-orders results by query relevance
- Works with any search results
- Improves retrieval accuracy
- Seamless integration with Search API

**Usage Examples**:
```python
# Rerank search results
reranked = jina_rerank(
    query="Redis connection pooling best practices",
    documents=search_results,
    top_k=10
)
```

### 6. **Jina Classification API**
**Purpose**: Zero-shot and few-shot classification
**Key Features**:
- No training required
- Supports text and images
- Multi-lingual capability
- High accuracy

**Usage Examples**:
```python
# Text classification
result = jina_classify(
    text="This code has a SQL injection vulnerability",
    labels=["security_issue", "performance_issue", "style_issue"]
)

# Image classification
result = jina_classify(
    image=screenshot_data,
    labels=["ui_bug", "rendering_issue", "correct_display"]
)
```

### 7. **Jina Segmentation API**
**Purpose**: Intelligent text chunking and tokenization
**Key Features**:
- Smart document segmentation
- Respects semantic boundaries
- Optimized chunk sizes for LLMs
- Tokenization support

**Usage Examples**:
```python
# Segment long documentation
chunks = jina_segment(
    text=long_documentation,
    max_chunk_size=1000,
    overlap=100
)
```

### 8. **Jina Enrichment API** (via Kagi)
**Purpose**: Add specialized knowledge from non-mainstream sources
**Indexes**:
- **Teclis**: Specialized web index
- **TinyGem**: Curated news index
**Features**:
- Non-SEO manipulated results
- Academic and technical focus
- High-quality niche content

## Integration Patterns for Agents

### For Planning Agent:
1. Use **Grounding API** to verify all technical decisions
2. Use **Reader API** to extract current documentation
3. Use **Search API** for finding best practices
4. Use **Classification API** to categorize risks

### For Coding Agent:
1. Use **Reader API** to get API documentation
2. Use **Grounding API** to verify version compatibility
3. Use **Embeddings API** to find similar code patterns
4. Use **Reranker API** to prioritize examples

### For Review Agent:
1. Use **Grounding API** to fact-check security claims
2. Use **Reader API** to extract security advisories
3. Use **Classification API** to categorize issues
4. Use **Search API** for vulnerability databases

### For Testing Agent:
1. Use **Grounding API** to verify edge cases
2. Use **Reader API** to extract testing guides
3. Use **Search API** for real-world failure examples
4. Use **Segmentation API** to chunk test scenarios

## Best Practices

### 1. **Parallel Processing**
```python
# Good: Process multiple URLs at once
urls = ["url1", "url2", "url3"]
results = jina_reader_process(url=urls, extract_depth="advanced")

# Bad: Sequential processing
for url in urls:
    result = jina_reader_process(url=url)
```

### 2. **Fact-Check Critical Information**
```python
# Always verify version numbers, compatibility claims, security issues
critical_info = "Library X version 2.0 is compatible with Framework Y"
verification = jina_grounding_enhance(content=critical_info)
if verification.factuality_score < 0.8:
    # Flag for human review or additional research
```

### 3. **Extract Clean Content First**
```python
# For JavaScript-heavy documentation sites
clean_docs = jina_reader_process(
    url="https://dynamic-docs.example.com",
    extract_depth="advanced"
)
# Then process the clean markdown
```

### 4. **Combine Tools for Best Results**
```python
# 1. Search for information
# 2. Extract clean content with Reader
# 3. Verify facts with Grounding
# 4. Classify or segment as needed
```

## Rate Limits and Credits

- **10 million free tokens** with new API keys
- Rate limits: RPM (requests/minute) and TPM (tokens/minute)
- Tracked per API key (not IP when key provided)
- Costs:
  - Grounding: ~$0.006 per request
  - Reader: Based on content size
  - Embeddings: Based on token count

## Error Handling

```python
try:
    result = jina_grounding_enhance(content=claim)
    if result.factuality_score < 0.7:
        # Low confidence - need additional verification
        fallback_research()
except JinaAPIError as e:
    # Handle rate limits, network issues, etc.
    log.warning(f"Jina API error: {e}")
    use_alternative_verification()
```

## When to Use Each Tool

| Task | Primary Tool | Secondary Tool |
|------|--------------|----------------|
| Extract documentation | Reader API | - |
| Verify technical claims | Grounding API | Search API |
| Find code examples | Search API | Reader API |
| Check security issues | Grounding API | Reader API |
| Classify content | Classification API | - |
| Find similar code | Embeddings API | Reranker API |
| Chunk large docs | Segmentation API | - |
| Get niche knowledge | Enrichment API | - |

Remember: These tools transform agents from being limited by training data to having real-time, verified access to current information!