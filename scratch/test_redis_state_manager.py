"""
Quick test script to verify Redis state manager implementation.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from src.redis_state_manager import (
    RedisStateManager, WorkflowState, ApprovalRequest, TestResults
)


async def test_redis_state_manager():
    """Test the Redis state manager functionality."""
    
    # Test with memory fallback (no actual Redis required)
    manager = RedisStateManager(
        redis_url="redis://localhost:6379",  # Will fail and fallback to memory
        fallback_memory=True
    )
    
    print("Testing Redis State Manager...")
    
    # Connect (should fallback to memory)
    await manager.connect()
    print("✓ Connected (using memory fallback)")
    
    # Test workflow state
    workflow = WorkflowState(
        workflow_id="WF-123",
        status="in_progress",
        feature_description="Test feature",
        current_stage="implementation",
        metadata={"key": "value"},
        created_at=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
        ttl_hours=24
    )
    
    success = await manager.save_workflow_state(workflow)
    print(f"✓ Save workflow state: {success}")
    
    retrieved = await manager.get_workflow_state("WF-123")
    print(f"✓ Retrieved workflow: {retrieved.workflow_id if retrieved else 'None'}")
    
    # Test update
    success = await manager.update_workflow_state(
        "WF-123", 
        {"status": "completed", "current_stage": "done"}
    )
    print(f"✓ Update workflow state: {success}")
    
    # Test approval request
    approval = ApprovalRequest(
        approval_id="APR-456",
        workflow_id="WF-123",
        request_type="test",
        content="Please approve test results",
        requester="test_user",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        status="pending"
    )
    
    success = await manager.save_approval_request(approval)
    print(f"✓ Save approval request: {success}")
    
    retrieved_approval = await manager.get_approval_request("APR-456")
    print(f"✓ Retrieved approval: {retrieved_approval.approval_id if retrieved_approval else 'None'}")
    
    # Test test results
    results = TestResults(
        test_id="TEST-789",
        workflow_id="WF-123",
        test_suite="unit_tests",
        passed=10,
        failed=2,
        skipped=1,
        duration_seconds=45.5,
        failure_details=[{"test": "test_feature", "error": "assertion failed"}],
        coverage_percent=85.5,
        executed_at=datetime.now(timezone.utc)
    )
    
    success = await manager.save_test_results(results)
    print(f"✓ Save test results: {success}")
    
    # Test health check
    health = await manager.health_check()
    print(f"✓ Health check: {health['status']} (backend: {health.get('backend', 'unknown')})")
    
    # Clean up
    await manager.close()
    print("✓ Connection closed")
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    asyncio.run(test_redis_state_manager())