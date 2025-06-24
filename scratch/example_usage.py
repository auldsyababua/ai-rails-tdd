"""
Example usage of the Redis State Manager with Upstash Redis.
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from src.redis_state_manager import (
    RedisStateManager, WorkflowState, ApprovalRequest, TestResults
)


async def main():
    """Example usage of Redis State Manager."""
    
    # Example 1: Connect to Upstash Redis with TLS
    # In production, get the URL from environment variables
    redis_url = os.environ.get(
        "REDIS_URL", 
        "rediss://default:your-password@your-instance.upstash.io:6379"
    )
    
    # Initialize manager with production settings
    manager = RedisStateManager(
        redis_url=redis_url,
        fallback_memory=True,  # Enable fallback for resilience
        pool_size=20,  # Adjust based on expected concurrency
        socket_connect_timeout=10.0,  # Longer timeout for cloud connections
        socket_timeout=10.0
    )
    
    try:
        # Connect to Redis
        await manager.connect()
        print("Connected to Redis")
        
        # Example workflow: Feature development
        workflow = WorkflowState(
            workflow_id="FEAT-2024-001",
            status="pending",
            feature_description="Add user authentication with OAuth2",
            current_stage="planning",
            metadata={
                "assignee": "dev-team-1",
                "priority": "high",
                "estimated_hours": 40
            },
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            ttl_hours=168  # Keep for 1 week
        )
        
        # Save workflow
        if await manager.save_workflow_state(workflow):
            print(f"Created workflow: {workflow.workflow_id}")
        
        # Simulate workflow progression
        await asyncio.sleep(1)
        
        # Update workflow status
        if await manager.update_workflow_state(
            workflow.workflow_id,
            {
                "status": "in_progress",
                "current_stage": "implementation",
                "metadata": {
                    **workflow.metadata,
                    "started_at": datetime.now(timezone.utc).isoformat()
                }
            }
        ):
            print("Updated workflow to in_progress")
        
        # Create approval request for code review
        approval = ApprovalRequest(
            approval_id=f"APPR-{workflow.workflow_id}-001",
            workflow_id=workflow.workflow_id,
            request_type="code",
            content="Please review the OAuth2 implementation in PR #123",
            requester="dev-john",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=48),
            status="pending"
        )
        
        if await manager.save_approval_request(approval):
            print(f"Created approval request: {approval.approval_id}")
        
        # Simulate test execution
        test_results = TestResults(
            test_id="TEST-001",
            workflow_id=workflow.workflow_id,
            test_suite="integration_tests",
            passed=45,
            failed=3,
            skipped=2,
            duration_seconds=120.5,
            failure_details=[
                {
                    "test": "test_oauth_token_refresh",
                    "error": "Token refresh failed with 401",
                    "file": "test_auth.py",
                    "line": 145
                },
                {
                    "test": "test_oauth_logout",
                    "error": "Session not properly cleared",
                    "file": "test_auth.py",
                    "line": 203
                },
                {
                    "test": "test_oauth_concurrent_login",
                    "error": "Race condition detected",
                    "file": "test_auth.py",
                    "line": 267
                }
            ],
            coverage_percent=78.5,
            executed_at=datetime.now(timezone.utc)
        )
        
        if await manager.save_test_results(test_results):
            print(f"Saved test results: {test_results.passed} passed, {test_results.failed} failed")
        
        # Check system health
        health = await manager.health_check()
        print(f"\nSystem Health:")
        print(f"  Status: {health['status']}")
        print(f"  Backend: {health.get('backend', 'unknown')}")
        if health.get('backend') == 'redis':
            print(f"  Redis Version: {health.get('redis_version', 'unknown')}")
            print(f"  Memory Usage: {health.get('used_memory_human', 'unknown')}")
        
        # Retrieve and display current state
        current_state = await manager.get_workflow_state(workflow.workflow_id)
        if current_state:
            print(f"\nCurrent Workflow State:")
            print(f"  ID: {current_state.workflow_id}")
            print(f"  Status: {current_state.status}")
            print(f"  Stage: {current_state.current_stage}")
            print(f"  Last Updated: {current_state.last_updated}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Always close the connection
        await manager.close()
        print("\nConnection closed")


if __name__ == "__main__":
    asyncio.run(main())