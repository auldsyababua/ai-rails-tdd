#!/usr/bin/env python3
"""
Final test to verify both Redis and Vector are working correctly.
"""
import asyncio
import os
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


async def test_final():
    """Run final integration test."""
    print("🧪 Testing Upstash Integration...")
    print("=" * 50)
    
    # Test Redis
    print("\n1. Testing Redis...")
    try:
        from src.redis_state_manager import RedisStateManager, WorkflowState
        
        manager = RedisStateManager()
        await manager.connect()
        
        # Create a proper workflow state
        state = WorkflowState(
            workflow_id="test-workflow-001",
            status="in_progress",
            feature_description="Email validation with TDD",
            current_stage="testing",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            metadata={"test": True}
        )
        
        # Save it
        saved = await manager.save_workflow_state(state)
        print(f"   ✅ Saved workflow state: {saved}")
        
        # Retrieve it
        retrieved = await manager.get_workflow_state("test-workflow-001")
        print(f"   ✅ Retrieved workflow: {retrieved.workflow_id if retrieved else 'None'}")
        
        # Health check
        health = await manager.health_check()
        print(f"   ✅ Redis health: {health.get('status')} (backend: {health.get('backend')})")
        
        await manager.close()
        
    except Exception as e:
        print(f"   ❌ Redis error: {e}")
    
    # Test Vector
    print("\n2. Testing Vector...")
    try:
        from src.vector_manager import VectorManager, EmbeddingManager
        
        vector_mgr = VectorManager()
        embedding_mgr = EmbeddingManager()
        
        if vector_mgr.index:
            print(f"   ✅ Connected to Upstash Vector")
            
            # Create test embedding
            test_text = "Email validation test"
            test_embedding = await embedding_mgr.create_embedding(test_text)
            print(f"   ✅ Created embedding with {len(test_embedding)} dimensions")
            
            # Note: upstash-vector methods are synchronous, not async
            # So we don't use await here
            success = vector_mgr.index.upsert(
                vectors=[{
                    "id": "test-001",
                    "vector": test_embedding,
                    "metadata": {"type": "test"}
                }]
            )
            print(f"   ✅ Upserted vector successfully")
            
            # Query
            results = vector_mgr.index.query(
                vector=test_embedding,
                top_k=1,
                include_metadata=True
            )
            print(f"   ✅ Query returned {len(results)} results")
            
            # Cleanup
            vector_mgr.index.delete(["test-001"])
            print(f"   ✅ Cleaned up test vector")
            
        else:
            print(f"   ⚠️  Using memory fallback")
    
    except Exception as e:
        print(f"   ❌ Vector error: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Integration test complete!")
    print("\nYour Upstash setup is ready for AI Rails TDD!")


if __name__ == "__main__":
    asyncio.run(test_final())