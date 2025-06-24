"""
Test script for Upstash Vector integration.
"""
import asyncio
import os
from datetime import datetime
from src.vector_manager import VectorManager, EmbeddingManager


async def test_vector_manager():
    """Test the Vector Manager with Upstash Vector."""
    print("Testing Vector Manager...\n")
    
    # Initialize managers
    vector_manager = VectorManager()
    embedding_manager = EmbeddingManager()
    
    # Test data
    test_documents = [
        {
            "id": "plan-001",
            "text": "Design a user authentication system with JWT tokens",
            "metadata": {
                "type": "plan",
                "agent": "planner",
                "session": "test-session-001",
                "project": "auth-system"
            }
        },
        {
            "id": "code-001", 
            "text": "Implement JWT token generation and validation",
            "metadata": {
                "type": "code",
                "agent": "coder",
                "session": "test-session-001",
                "project": "auth-system"
            }
        },
        {
            "id": "test-001",
            "text": "Test JWT token expiration and refresh logic",
            "metadata": {
                "type": "test",
                "agent": "tester",
                "session": "test-session-001",
                "project": "auth-system"
            }
        }
    ]
    
    # 1. Test upsert
    print("1. Testing vector upsert...")
    for doc in test_documents:
        embedding = await embedding_manager.create_embedding(doc["text"])
        success = await vector_manager.upsert(
            id=doc["id"],
            vector=embedding,
            metadata=doc["metadata"]
        )
        print(f"   ✓ Upserted {doc['id']}: {success}")
    
    # 2. Test query
    print("\n2. Testing vector query...")
    query_text = "How to implement authentication with tokens?"
    query_embedding = await embedding_manager.create_embedding(query_text)
    
    results = await vector_manager.query(
        vector=query_embedding,
        top_k=3
    )
    
    print(f"   Query: '{query_text}'")
    print(f"   Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. ID: {result['id']}, Score: {result['score']:.4f}")
        print(f"      Type: {result['metadata'].get('type')}")
        print(f"      Agent: {result['metadata'].get('agent')}")
    
    # 3. Test filtered query
    print("\n3. Testing filtered query...")
    filtered_results = await vector_manager.query(
        vector=query_embedding,
        top_k=2,
        filter="type = 'plan'"
    )
    
    print(f"   Filter: type = 'plan'")
    print(f"   Found {len(filtered_results)} results:")
    for result in filtered_results:
        print(f"   - {result['id']} (type: {result['metadata'].get('type')})")
    
    # 4. Test fetch
    print("\n4. Testing vector fetch...")
    fetched = await vector_manager.fetch(["plan-001", "code-001"])
    print(f"   Fetched {len(fetched)} vectors")
    for item in fetched:
        print(f"   - {item['id']}: {item['metadata'].get('type')}")
    
    # 5. Test metadata update
    print("\n5. Testing metadata update...")
    success = await vector_manager.update_metadata(
        id="plan-001",
        metadata={"reviewed": True, "reviewer": "human"}
    )
    print(f"   Update metadata: {success}")
    
    # Verify update
    updated = await vector_manager.fetch(["plan-001"])
    if updated:
        print(f"   Verified: reviewed = {updated[0]['metadata'].get('reviewed')}")
    
    # 6. Test delete
    print("\n6. Testing vector delete...")
    success = await vector_manager.delete(["test-001"])
    print(f"   Delete test-001: {success}")
    
    # Verify deletion
    remaining = await vector_manager.fetch(["test-001"])
    print(f"   Verified: vector {'not found' if not remaining else 'still exists'}")
    
    # Cleanup
    print("\n7. Cleaning up test data...")
    await vector_manager.delete(["plan-001", "code-001"])
    print("   ✓ Cleanup complete")
    
    print("\n✅ All vector tests completed!")


async def test_workflow_context():
    """Test vector storage for workflow context."""
    print("\n\nTesting Workflow Context Storage...\n")
    
    vector_manager = VectorManager()
    embedding_manager = EmbeddingManager()
    
    # Simulate storing agent outputs
    workflow_outputs = [
        {
            "session": "email-validator-001",
            "step": 1,
            "agent": "planner",
            "output": "Create an email validation service with regex pattern matching and DNS verification"
        },
        {
            "session": "email-validator-001", 
            "step": 2,
            "agent": "tester",
            "output": "Test email format validation, domain existence, and MX record verification"
        },
        {
            "session": "email-validator-001",
            "step": 3,
            "agent": "coder",
            "output": "Implement EmailValidator class with validate_format and verify_domain methods"
        }
    ]
    
    # Store workflow outputs
    print("Storing workflow outputs...")
    for output in workflow_outputs:
        id = f"{output['session']}-step-{output['step']}"
        embedding = await embedding_manager.create_embedding(output['output'])
        
        await vector_manager.upsert(
            id=id,
            vector=embedding,
            metadata={
                "session": output['session'],
                "step": output['step'],
                "agent": output['agent'],
                "timestamp": datetime.now().isoformat()
            }
        )
        print(f"   ✓ Stored {id}")
    
    # Search for relevant context
    print("\nSearching for relevant context...")
    context_query = "How should we handle email domain verification?"
    query_embedding = await embedding_manager.create_embedding(context_query)
    
    context_results = await vector_manager.query(
        vector=query_embedding,
        top_k=2,
        filter="session = 'email-validator-001'"
    )
    
    print(f"Query: '{context_query}'")
    print("Relevant context from workflow:")
    for result in context_results:
        meta = result['metadata']
        print(f"   - Step {meta['step']} ({meta['agent']}): Score {result['score']:.4f}")
    
    # Cleanup
    ids_to_delete = [f"email-validator-001-step-{i}" for i in range(1, 4)]
    await vector_manager.delete(ids_to_delete)
    print("\n✓ Workflow test complete")


async def main():
    """Run all tests."""
    # Check if we have credentials
    if not os.getenv("UPSTASH_VECTOR_URL") or not os.getenv("UPSTASH_VECTOR_TOKEN"):
        print("⚠️  WARNING: Upstash Vector credentials not found in environment.")
        print("   Running in memory-only mode.")
        print("   To use Upstash Vector, set UPSTASH_VECTOR_URL and UPSTASH_VECTOR_TOKEN")
        print()
    
    await test_vector_manager()
    await test_workflow_context()


if __name__ == "__main__":
    asyncio.run(main())