#!/usr/bin/env python3
"""
Complete demo of Redis state management + OpenAI-powered vector search.
"""
import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.redis_state_manager import RedisStateManager, WorkflowState, TestResults
from src.vector_manager import VectorManager, EmbeddingManager


async def demo_complete_system():
    """Demonstrate the complete Upstash integration."""
    print("🚀 AI Rails TDD - Complete Upstash Integration Demo")
    print("=" * 60)
    
    # Initialize managers
    redis_mgr = RedisStateManager()
    await redis_mgr.connect()
    vector_mgr = VectorManager()
    embedding_mgr = EmbeddingManager()
    
    # Demo workflow ID
    workflow_id = "demo-email-validator"
    
    print("\n📝 Phase 1: Planning")
    print("-" * 40)
    
    # Create workflow state
    workflow = WorkflowState(
        workflow_id=workflow_id,
        status="in_progress",
        feature_description="Email validation service with regex and DNS verification",
        current_stage="planning",
        created_at=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
        metadata={
            "planner_agent": "gpt-4",
            "estimated_hours": 4
        }
    )
    
    # Save to Redis
    await redis_mgr.save_workflow_state(workflow)
    print(f"✅ Saved workflow state to Redis: {workflow_id}")
    
    # Store planning document in Vector
    planning_doc = """
    Email Validation Service Design:
    1. Validate email format using regex patterns
    2. Check domain existence with DNS lookup
    3. Verify MX records for email delivery
    4. Return detailed validation results with confidence score
    """
    
    planning_embedding = await embedding_mgr.create_embedding(planning_doc)
    vector_mgr.index.upsert([{
        "id": f"{workflow_id}-plan",
        "vector": planning_embedding,
        "metadata": {
            "workflow_id": workflow_id,
            "stage": "planning",
            "agent": "planner",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }])
    print("✅ Stored planning document in Vector database")
    
    print("\n🧪 Phase 2: Test Design")
    print("-" * 40)
    
    # Update workflow state
    workflow.current_stage = "testing"
    workflow.last_updated = datetime.now(timezone.utc)
    await redis_mgr.save_workflow_state(workflow)
    
    # Store test specifications
    test_spec = """
    Behavioral Test Specifications:
    - GIVEN a valid email format WHEN validated THEN return success
    - GIVEN an invalid domain WHEN checked THEN return domain_not_found error
    - GIVEN no MX records WHEN verified THEN return mx_not_configured warning
    """
    
    test_embedding = await embedding_mgr.create_embedding(test_spec)
    vector_mgr.index.upsert([{
        "id": f"{workflow_id}-tests",
        "vector": test_embedding,
        "metadata": {
            "workflow_id": workflow_id,
            "stage": "testing",
            "agent": "tester",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }])
    print("✅ Stored test specifications in Vector database")
    
    print("\n💻 Phase 3: Implementation")
    print("-" * 40)
    
    # Update workflow state
    workflow.current_stage = "coding"
    workflow.last_updated = datetime.now(timezone.utc)
    await redis_mgr.save_workflow_state(workflow)
    
    # Simulate test results
    test_results = TestResults(
        test_id=f"{workflow_id}-test-001",
        workflow_id=workflow_id,
        test_suite="email_validation_tests",
        passed=8,
        failed=2,
        skipped=0,
        duration_seconds=1.23,
        failure_details=[
            {"test": "test_unicode_domains", "error": "UnicodeDecodeError"},
            {"test": "test_subdomain_mx", "error": "AssertionError"}
        ],
        coverage_percent=85.5,
        executed_at=datetime.now(timezone.utc)
    )
    
    await redis_mgr.save_test_results(test_results)
    print(f"✅ Saved test results: {test_results.passed} passed, {test_results.failed} failed")
    
    print("\n🔍 Phase 4: Semantic Search Demo")
    print("-" * 40)
    
    # Search queries
    queries = [
        "How do we validate email domains?",
        "What are the test requirements?",
        "DNS and MX record verification process"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        query_embedding = await embedding_mgr.create_embedding(query)
        
        results = vector_mgr.index.query(
            vector=query_embedding,
            top_k=2,
            include_metadata=True,
            filter=f"workflow_id = '{workflow_id}'"
        )
        
        if results:
            for result in results:
                print(f"  📄 Found: {result.id} (Score: {result.score:.3f})")
                print(f"     Stage: {result.metadata.get('stage')}")
        else:
            print("  No results found")
    
    print("\n📊 Phase 5: Workflow Summary")
    print("-" * 40)
    
    # Get current state from Redis
    current_state = await redis_mgr.get_workflow_state(workflow_id)
    if current_state:
        print(f"Workflow ID: {current_state.workflow_id}")
        print(f"Status: {current_state.status}")
        print(f"Current Stage: {current_state.current_stage}")
        print(f"Created: {current_state.created_at}")
        print(f"Last Updated: {current_state.last_updated}")
    
    # Get test results
    latest_results = await redis_mgr.get_test_results(workflow_id)
    if latest_results:
        print(f"\nLatest Test Results:")
        print(f"  Passed: {latest_results.passed}")
        print(f"  Failed: {latest_results.failed}")
        print(f"  Coverage: {latest_results.coverage_percent}%")
    
    # Health check
    health = await redis_mgr.health_check()
    print(f"\nRedis Health: {health.get('status')} ({health.get('backend')})")
    
    # Cleanup
    print("\n🧹 Cleanup")
    print("-" * 40)
    vector_mgr.index.delete([f"{workflow_id}-plan", f"{workflow_id}-tests"])
    await redis_mgr.close()
    print("✅ Demo complete!")
    
    print("\n" + "=" * 60)
    print("💡 Your Upstash integration is fully operational!")
    print("   - Redis for state management")
    print("   - OpenAI for embeddings")
    print("   - Vector for semantic search")


if __name__ == "__main__":
    asyncio.run(demo_complete_system())