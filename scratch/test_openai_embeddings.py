#!/usr/bin/env python3
"""
Test OpenAI embeddings integration with Upstash Vector.
"""
import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.vector_manager import VectorManager, EmbeddingManager


async def test_openai_embeddings():
    """Test real OpenAI embeddings with Upstash Vector."""
    print("🧪 Testing OpenAI Embeddings Integration")
    print("=" * 50)
    
    # Initialize managers
    vector_mgr = VectorManager()
    embedding_mgr = EmbeddingManager()  # Will use OpenAI by default
    
    # Check if OpenAI is configured
    if embedding_mgr._client:
        print(f"✅ OpenAI configured with model: {embedding_mgr.model}")
    else:
        print("⚠️  OpenAI not configured, using placeholder embeddings")
    
    # Test data - AI Rails TDD workflow stages
    test_documents = [
        {
            "id": "workflow-001",
            "text": "The planner agent creates a comprehensive design document with technical specifications and test requirements",
            "metadata": {"stage": "planning", "agent": "planner"}
        },
        {
            "id": "workflow-002", 
            "text": "The test designer creates behavioral specifications without revealing implementation details to prevent gaming",
            "metadata": {"stage": "testing", "agent": "tester"}
        },
        {
            "id": "workflow-003",
            "text": "The coder implements the solution based on technical specs while adhering to blind testing principles",
            "metadata": {"stage": "coding", "agent": "coder"}
        }
    ]
    
    print("\n1. Creating embeddings...")
    embeddings_created = 0
    for doc in test_documents:
        try:
            # Create embedding
            embedding = await embedding_mgr.create_embedding(doc["text"])
            print(f"   ✅ Created embedding for {doc['id']} ({len(embedding)} dimensions)")
            
            # Store in Vector
            if vector_mgr.index:
                vector_mgr.index.upsert([{
                    "id": doc["id"],
                    "vector": embedding,
                    "metadata": doc["metadata"]
                }])
                embeddings_created += 1
            
        except Exception as e:
            print(f"   ❌ Error with {doc['id']}: {e}")
    
    print(f"\n   Stored {embeddings_created} embeddings in Upstash Vector")
    
    # Test semantic search
    print("\n2. Testing semantic search...")
    queries = [
        "How does the testing process work?",
        "What does the planning agent do?",
        "Tell me about blind testing implementation"
    ]
    
    for query in queries:
        print(f"\n   Query: '{query}'")
        try:
            # Create query embedding
            query_embedding = await embedding_mgr.create_embedding(query)
            
            # Search
            if vector_mgr.index:
                results = vector_mgr.index.query(
                    vector=query_embedding,
                    top_k=2,
                    include_metadata=True
                )
                
                print(f"   Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    # Results are QueryResult objects, not dicts
                    print(f"     {i}. ID: {result.id}, Score: {result.score:.3f}")
                    if hasattr(result, 'metadata') and result.metadata:
                        print(f"        Stage: {result.metadata.get('stage')}, Agent: {result.metadata.get('agent')}")
        
        except Exception as e:
            print(f"   ❌ Search error: {e}")
    
    # Cleanup
    print("\n3. Cleaning up...")
    if vector_mgr.index:
        try:
            vector_mgr.index.delete([doc["id"] for doc in test_documents])
            print("   ✅ Cleaned up test embeddings")
        except:
            pass
    
    print("\n" + "=" * 50)
    if embedding_mgr._client:
        print("✅ OpenAI embeddings are working perfectly!")
        print("   Your semantic search is now powered by real AI embeddings.")
    else:
        print("⚠️  Using placeholder embeddings.")
        print("   Add your OpenAI API key to .env to enable real embeddings.")


if __name__ == "__main__":
    asyncio.run(test_openai_embeddings())