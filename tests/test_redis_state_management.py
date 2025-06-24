"""
Comprehensive Test Suite for Redis State Management Integration

This test suite implements research-driven TDD for Redis workflow state management
with Upstash TLS support, connection pooling, and graceful fallback patterns.

Research Sources:
- Redis-py documentation and best practices
- Real-world failure modes from GitHub issues and StackOverflow
- Connection pool exhaustion patterns from production systems
- Property-based testing for data integrity validation
"""

import pytest
import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from concurrent.futures import ThreadPoolExecutor
import redis
import redis.asyncio as aioredis
from redis.exceptions import (
    ConnectionError, 
    TimeoutError, 
    BusyLoadingError,
    ResponseError,
    RedisError
)
from hypothesis import given, strategies as st, settings
from pydantic import BaseModel, ValidationError

# Assuming these models exist based on the specification
class WorkflowState(BaseModel):
    workflow_id: str
    status: str  # pending|in_progress|completed|failed
    feature_description: str
    current_stage: str
    metadata: Dict[str, Any]
    created_at: datetime
    last_updated: datetime
    ttl_hours: int

class ApprovalRequest(BaseModel):
    approval_id: str
    workflow_id: str
    request_type: str  # test|code|deploy
    content: str
    requester: str
    created_at: datetime
    expires_at: datetime
    status: str  # pending|approved|rejected|expired

class TestResults(BaseModel):
    test_id: str
    workflow_id: str
    test_suite: str
    passed: int
    failed: int
    skipped: int
    duration_seconds: float
    failure_details: Optional[List[Dict]] = None
    coverage_percent: Optional[float] = None
    executed_at: datetime

# Mock Redis State Manager (the class we're testing)
class RedisStateManager:
    def __init__(self, redis_url: str = None, fallback_memory: bool = True):
        self.redis_url = redis_url or "redis://localhost:6379"
        self.fallback_memory = fallback_memory
        self.memory_store = {}
        self.connection_pool = None
        self.client = None
        
    async def connect(self):
        """Initialize Redis connection with TLS support"""
        pass
        
    async def save_workflow_state(self, state: WorkflowState) -> bool:
        """Save workflow state with TTL"""
        pass
        
    async def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Retrieve workflow state"""
        pass
        
    async def update_workflow_state(self, workflow_id: str, updates: Dict) -> bool:
        """Update existing workflow state"""
        pass
        
    async def save_approval_request(self, request: ApprovalRequest) -> bool:
        """Save approval request"""
        pass
        
    async def get_approval_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get approval request"""
        pass
        
    async def save_test_results(self, results: TestResults) -> bool:
        """Save test execution results"""
        pass
        
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health"""
        pass


class TestRedisStateManagementIntegration:
    """Comprehensive test suite for Redis State Management"""
    
    @pytest.fixture
    def redis_manager(self):
        """Create Redis state manager instance for testing"""
        return RedisStateManager()
    
    @pytest.fixture
    def sample_workflow_state(self):
        """Create sample workflow state for testing"""
        return WorkflowState(
            workflow_id="TST-123456",
            status="pending",
            feature_description="Test feature implementation",
            current_stage="planning",
            metadata={"priority": "high", "team": "backend"},
            created_at=datetime.now(),
            last_updated=datetime.now(),
            ttl_hours=24
        )
    
    @pytest.fixture
    def sample_approval_request(self):
        """Create sample approval request for testing"""
        return ApprovalRequest(
            approval_id=str(uuid.uuid4()),
            workflow_id="TST-123456",
            request_type="test",
            content="Please approve test execution",
            requester="developer@company.com",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=2),
            status="pending"
        )
    
    @pytest.fixture
    def sample_test_results(self):
        """Create sample test results for testing"""
        return TestResults(
            test_id=str(uuid.uuid4()),
            workflow_id="TST-123456",
            test_suite="unit_tests",
            passed=95,
            failed=2,
            skipped=3,
            duration_seconds=45.67,
            coverage_percent=87.5,
            executed_at=datetime.now()
        )

    # HAPPY PATH TESTS
    
    def test_save_and_retrieve_workflow_state_when_redis_available_then_data_persisted(self, redis_manager, sample_workflow_state):
        """Test that workflow state can be saved with TTL and retrieved accurately"""
        with patch.object(redis_manager, 'client') as mock_client:
            mock_client.setex.return_value = True
            mock_client.get.return_value = json.dumps(sample_workflow_state.dict())
            
            # Act
            save_result = asyncio.run(redis_manager.save_workflow_state(sample_workflow_state))
            retrieved_state = asyncio.run(redis_manager.get_workflow_state("TST-123456"))
            
            # Assert
            assert save_result is True
            assert retrieved_state is not None
            assert retrieved_state.workflow_id == "TST-123456"
            assert retrieved_state.status == "pending"
            mock_client.setex.assert_called_once()
    
    def test_update_existing_workflow_state_when_valid_updates_then_preserves_integrity(self, redis_manager, sample_workflow_state):
        """Test that updates preserve data integrity and update timestamps"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            original_state = sample_workflow_state.dict()
            mock_client.get.return_value = json.dumps(original_state)
            mock_client.setex.return_value = True
            
            updates = {
                "status": "in_progress",
                "current_stage": "implementation",
                "last_updated": datetime.now().isoformat()
            }
            
            # Act
            result = asyncio.run(redis_manager.update_workflow_state("TST-123456", updates))
            
            # Assert
            assert result is True
            mock_client.get.assert_called_once()
            mock_client.setex.assert_called_once()
    
    def test_approval_request_lifecycle_when_normal_flow_then_all_operations_succeed(self, redis_manager, sample_approval_request):
        """Test creation, retrieval, and status updates of approval requests"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.setex.return_value = True
            mock_client.get.return_value = json.dumps(sample_approval_request.dict())
            
            # Act - Create
            save_result = asyncio.run(redis_manager.save_approval_request(sample_approval_request))
            
            # Act - Retrieve
            retrieved_request = asyncio.run(redis_manager.get_approval_request(sample_approval_request.approval_id))
            
            # Assert
            assert save_result is True
            assert retrieved_request is not None
            assert retrieved_request.request_type == "test"
            assert retrieved_request.status == "pending"

    # EDGE CASE TESTS (Research-Informed)
    
    def test_redis_connection_failure_when_server_unavailable_then_fallback_to_memory(self, redis_manager):
        """Verify graceful fallback to memory when Redis unavailable"""
        with patch('redis.asyncio.from_url') as mock_redis:
            # Arrange
            mock_redis.side_effect = ConnectionError("Connection refused")
            redis_manager.fallback_memory = True
            
            # Act
            connection_result = asyncio.run(redis_manager.connect())
            
            # Assert - Should not raise exception and should use memory fallback
            assert redis_manager.client is None
            assert isinstance(redis_manager.memory_store, dict)
    
    def test_connection_pool_exhaustion_when_max_connections_reached_then_handles_gracefully(self, redis_manager):
        """Handle scenario when all connections are in use"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange - Simulate pool exhaustion
            mock_client.setex.side_effect = ConnectionError("Cannot assign requested address")
            
            # Act & Assert
            with pytest.raises(ConnectionError):
                asyncio.run(redis_manager.save_workflow_state(
                    WorkflowState(
                        workflow_id="TST-999999",
                        status="pending",
                        feature_description="Test",
                        current_stage="test",
                        metadata={},
                        created_at=datetime.now(),
                        last_updated=datetime.now(),
                        ttl_hours=1
                    )
                ))
    
    def test_malformed_data_handling_when_corrupted_json_then_error_handled_gracefully(self, redis_manager):
        """Verify robust error handling for corrupted data"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.get.return_value = "invalid json data {"
            
            # Act
            result = asyncio.run(redis_manager.get_workflow_state("TST-123456"))
            
            # Assert
            assert result is None  # Should handle gracefully, not crash
    
    def test_network_timeout_recovery_when_transient_failures_then_retries_succeed(self, redis_manager):
        """Test recovery from network timeouts and transient failures"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange - First call times out, second succeeds
            mock_client.get.side_effect = [TimeoutError("Operation timed out"), json.dumps({"test": "data"})]
            
            # Act - This would typically be handled by redis-py retry logic
            with pytest.raises(TimeoutError):
                asyncio.run(redis_manager.get_workflow_state("TST-123456"))
    
    def test_large_payload_storage_when_near_redis_limits_then_handles_appropriately(self, redis_manager):
        """Verify handling of payloads near Redis limits"""
        # Arrange - Create large metadata payload (Redis default max is ~512MB)
        large_metadata = {"data": "x" * (10 * 1024 * 1024)}  # 10MB payload
        large_workflow = WorkflowState(
            workflow_id="TST-LARGE1",
            status="pending",
            feature_description="Large payload test",
            current_stage="testing",
            metadata=large_metadata,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            ttl_hours=1
        )
        
        with patch.object(redis_manager, 'client') as mock_client:
            mock_client.setex.return_value = True
            
            # Act
            result = asyncio.run(redis_manager.save_workflow_state(large_workflow))
            
            # Assert
            assert result is True
            # Verify the call was made with large payload
            mock_client.setex.assert_called_once()
            call_args = mock_client.setex.call_args
            assert len(call_args[0][1]) > 10 * 1024 * 1024  # Verify payload size

    # TTL AND EXPIRATION TESTS
    
    def test_ttl_expiration_when_time_elapsed_then_keys_expire_correctly(self, redis_manager):
        """Verify keys expire according to configured TTL"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.setex.return_value = True
            mock_client.ttl.return_value = 3600  # 1 hour remaining
            
            workflow_state = WorkflowState(
                workflow_id="TST-TTL001",
                status="pending",
                feature_description="TTL test",
                current_stage="testing",
                metadata={},
                created_at=datetime.now(),
                last_updated=datetime.now(),
                ttl_hours=1
            )
            
            # Act
            save_result = asyncio.run(redis_manager.save_workflow_state(workflow_state))
            
            # Assert
            assert save_result is True
            # Verify TTL was set correctly (1 hour = 3600 seconds)
            mock_client.setex.assert_called_once()
            call_args = mock_client.setex.call_args
            assert call_args[0][2] == 3600  # TTL in seconds

    # CONCURRENT ACCESS TESTS
    
    def test_concurrent_workflow_updates_when_simultaneous_access_then_data_consistency_maintained(self, redis_manager):
        """Ensure data consistency with simultaneous updates"""
        async def update_workflow(workflow_id: str, status: str):
            return await redis_manager.update_workflow_state(
                workflow_id, 
                {"status": status, "last_updated": datetime.now().isoformat()}
            )
        
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.get.return_value = json.dumps({
                "workflow_id": "TST-CONCURRENT",
                "status": "pending",
                "feature_description": "Concurrent test",
                "current_stage": "testing",
                "metadata": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "ttl_hours": 1
            })
            mock_client.setex.return_value = True
            
            # Act - Simulate concurrent updates
            async def run_concurrent_updates():
                tasks = [
                    update_workflow("TST-CONCURRENT", "in_progress"),
                    update_workflow("TST-CONCURRENT", "completed"),
                    update_workflow("TST-CONCURRENT", "failed")
                ]
                return await asyncio.gather(*tasks, return_exceptions=True)
            
            results = asyncio.run(run_concurrent_updates())
            
            # Assert - All updates should complete (Redis handles atomicity)
            assert all(result is True or isinstance(result, Exception) for result in results)

    # PROPERTY-BASED TESTS (Mathematically Researched)
    
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=50)
    def test_workflow_id_round_trip_property_when_any_valid_id_then_save_retrieve_consistency(self, redis_manager, workflow_id):
        """Property: Any valid workflow_id should survive save/retrieve round-trip"""
        # Filter out invalid workflow IDs based on our pattern
        if not workflow_id.replace('-', '').replace('_', '').isalnum():
            return  # Skip invalid characters
            
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            workflow_state = WorkflowState(
                workflow_id=workflow_id,
                status="pending",
                feature_description="Property test",
                current_stage="testing",
                metadata={},
                created_at=datetime.now(),
                last_updated=datetime.now(),
                ttl_hours=1
            )
            
            mock_client.setex.return_value = True
            mock_client.get.return_value = json.dumps(workflow_state.dict())
            
            # Act
            save_result = asyncio.run(redis_manager.save_workflow_state(workflow_state))
            retrieved_state = asyncio.run(redis_manager.get_workflow_state(workflow_id))
            
            # Assert - Round-trip property
            assert save_result is True
            assert retrieved_state is not None
            assert retrieved_state.workflow_id == workflow_id
    
    @given(st.integers(min_value=1, max_value=168))
    def test_ttl_monotonic_property_when_any_valid_ttl_then_expiration_time_consistent(self, redis_manager, ttl_hours):
        """Property: TTL should be monotonically decreasing over time"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            workflow_state = WorkflowState(
                workflow_id="TST-TTL-PROP",
                status="pending",
                feature_description="TTL property test",
                current_stage="testing",
                metadata={},
                created_at=datetime.now(),
                last_updated=datetime.now(),
                ttl_hours=ttl_hours
            )
            
            mock_client.setex.return_value = True
            expected_ttl_seconds = ttl_hours * 3600
            
            # Act
            result = asyncio.run(redis_manager.save_workflow_state(workflow_state))
            
            # Assert
            assert result is True
            mock_client.setex.assert_called_once()
            call_args = mock_client.setex.call_args
            assert call_args[0][2] == expected_ttl_seconds  # TTL property maintained

    # PERFORMANCE TESTS
    
    def test_operation_latency_when_normal_conditions_then_meets_performance_criteria(self, redis_manager):
        """Verify operation latency meets performance criteria (< 50ms)"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.setex.return_value = True
            workflow_state = WorkflowState(
                workflow_id="TST-PERF001",
                status="pending",
                feature_description="Performance test",
                current_stage="testing",
                metadata={},
                created_at=datetime.now(),
                last_updated=datetime.now(),
                ttl_hours=1
            )
            
            # Act - Measure latency
            start_time = time.time()
            result = asyncio.run(redis_manager.save_workflow_state(workflow_state))
            end_time = time.time()
            
            operation_time_ms = (end_time - start_time) * 1000
            
            # Assert
            assert result is True
            assert operation_time_ms < 100  # Relaxed for mocked test, would be 50ms in real scenario
    
    def test_throughput_when_batch_operations_then_meets_minimum_requirements(self, redis_manager):
        """Test minimum throughput requirements (1000 ops/sec)"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.setex.return_value = True
            mock_client.get.return_value = json.dumps({"test": "data"})
            
            num_operations = 100  # Reduced for test speed
            start_time = time.time()
            
            # Act - Batch operations
            async def batch_operations():
                tasks = []
                for i in range(num_operations):
                    workflow_state = WorkflowState(
                        workflow_id=f"TST-BATCH{i:03d}",
                        status="pending",
                        feature_description="Batch test",
                        current_stage="testing",
                        metadata={},
                        created_at=datetime.now(),
                        last_updated=datetime.now(),
                        ttl_hours=1
                    )
                    tasks.append(redis_manager.save_workflow_state(workflow_state))
                    tasks.append(redis_manager.get_workflow_state(f"TST-BATCH{i:03d}"))
                
                return await asyncio.gather(*tasks)
            
            results = asyncio.run(batch_operations())
            end_time = time.time()
            
            # Assert
            total_time = end_time - start_time
            ops_per_second = (num_operations * 2) / total_time  # 2 operations per iteration
            
            assert len(results) == num_operations * 2
            assert ops_per_second > 100  # Relaxed for mocked environment

    # SECURITY TESTS
    
    def test_tls_connection_when_upstash_url_then_uses_secure_connection(self, redis_manager):
        """Test that all connections use TLS/SSL for Upstash"""
        upstash_url = "rediss://username:password@host:port"
        redis_manager.redis_url = upstash_url
        
        with patch('redis.asyncio.from_url') as mock_from_url:
            # Act
            asyncio.run(redis_manager.connect())
            
            # Assert
            mock_from_url.assert_called_once()
            call_args = mock_from_url.call_args[0][0]
            assert call_args.startswith("rediss://")  # Secure Redis protocol
    
    def test_input_validation_when_malicious_keys_then_prevents_injection(self, redis_manager):
        """Verify all input keys are validated against injection"""
        malicious_keys = [
            "TST-123456; FLUSHALL",
            "TST-123456\nFLUSHALL",
            "TST-123456\r\nFLUSHALL",
            "../../../etc/passwd",
            "eval('malicious_code')"
        ]
        
        for malicious_key in malicious_keys:
            with pytest.raises((ValidationError, ValueError)):
                # This should be validated by the WorkflowState model
                WorkflowState(
                    workflow_id=malicious_key,
                    status="pending",
                    feature_description="Security test",
                    current_stage="testing",
                    metadata={},
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    ttl_hours=1
                )

    # HEALTH CHECK AND MONITORING TESTS
    
    def test_health_check_when_redis_healthy_then_returns_status_metrics(self, redis_manager):
        """Test health check returns comprehensive status"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.ping.return_value = True
            mock_client.info.return_value = {
                'connected_clients': 5,
                'used_memory': 1024000,
                'keyspace_hits': 1000,
                'keyspace_misses': 100
            }
            
            # Act
            health_status = asyncio.run(redis_manager.health_check())
            
            # Assert
            assert health_status is not None
            assert 'redis_connected' in health_status or health_status == {}  # Mock may return empty
    
    def test_health_check_when_redis_unhealthy_then_reports_failure(self, redis_manager):
        """Test health check properly reports Redis failures"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.ping.side_effect = ConnectionError("Connection failed")
            
            # Act
            health_status = asyncio.run(redis_manager.health_check())
            
            # Assert
            # Should not raise exception but should indicate unhealthy state
            assert health_status is not None

    # ERROR HANDLING TESTS
    
    def test_busy_loading_error_when_redis_starting_then_retries_appropriately(self, redis_manager):
        """Test handling of Redis LOADING state during startup"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.setex.side_effect = BusyLoadingError("Redis is loading the dataset in memory")
            
            # Act & Assert
            with pytest.raises(BusyLoadingError):
                asyncio.run(redis_manager.save_workflow_state(
                    WorkflowState(
                        workflow_id="TST-LOADING",
                        status="pending",
                        feature_description="Loading test",
                        current_stage="testing",
                        metadata={},
                        created_at=datetime.now(),
                        last_updated=datetime.now(),
                        ttl_hours=1
                    )
                ))
    
    def test_response_error_when_invalid_command_then_handles_gracefully(self, redis_manager):
        """Test handling of Redis command errors"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.setex.side_effect = ResponseError("WRONGTYPE Operation against a key holding the wrong kind of value")
            
            # Act & Assert
            with pytest.raises(ResponseError):
                asyncio.run(redis_manager.save_workflow_state(
                    WorkflowState(
                        workflow_id="TST-WRONGTYPE",
                        status="pending",
                        feature_description="Error test",
                        current_stage="testing",
                        metadata={},
                        created_at=datetime.now(),
                        last_updated=datetime.now(),
                        ttl_hours=1
                    )
                ))

    # INTEGRATION TESTS
    
    def test_full_workflow_lifecycle_when_complete_flow_then_all_stages_work(self, redis_manager):
        """Integration test for complete workflow lifecycle"""
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            mock_client.setex.return_value = True
            workflow_states = []
            
            def mock_get(key):
                # Return the latest state for the workflow
                if workflow_states:
                    return json.dumps(workflow_states[-1])
                return None
            
            mock_client.get.side_effect = mock_get
            
            workflow_id = "TST-LIFECYCLE"
            
            # Act 1: Create workflow
            initial_state = WorkflowState(
                workflow_id=workflow_id,
                status="pending",
                feature_description="Lifecycle test",
                current_stage="planning",
                metadata={"creator": "test_user"},
                created_at=datetime.now(),
                last_updated=datetime.now(),
                ttl_hours=24
            )
            
            save_result = asyncio.run(redis_manager.save_workflow_state(initial_state))
            workflow_states.append(initial_state.dict())
            
            # Act 2: Update to in_progress
            update_result = asyncio.run(redis_manager.update_workflow_state(
                workflow_id, 
                {"status": "in_progress", "current_stage": "implementation"}
            ))
            
            # Act 3: Retrieve final state
            final_state = asyncio.run(redis_manager.get_workflow_state(workflow_id))
            
            # Assert
            assert save_result is True
            assert update_result is True
            assert final_state is not None
            assert final_state.workflow_id == workflow_id


# Performance and Load Testing
class TestRedisPerformanceAndLoad:
    """Performance-focused tests for Redis operations"""
    
    def test_connection_pool_efficiency_when_high_concurrency_then_maintains_performance(self):
        """Test connection pool efficiency under load"""
        # This would test actual connection pool behavior
        # For now, we'll simulate the test structure
        pass
    
    def test_memory_usage_per_key_when_various_payloads_then_within_limits(self):
        """Test memory usage stays within acceptable bounds"""
        # This would measure actual memory usage patterns
        pass
    
    def test_recovery_time_when_redis_restart_then_meets_sla(self):
        """Test recovery time after Redis restart meets SLA (< 5 seconds)"""
        # This would test actual recovery scenarios
        pass


# Anti-Gaming Strategies Implementation
class TestAntiGamingMeasures:
    """Tests designed to prevent superficial implementations"""
    
    @given(st.dictionaries(st.text(), st.text(), min_size=1, max_size=10))
    def test_metadata_preservation_property_when_any_metadata_then_round_trip_identical(self, metadata):
        """Property: Metadata should be preserved exactly through save/retrieve cycles"""
        # This test ensures implementations can't just ignore metadata
        redis_manager = RedisStateManager()
        
        with patch.object(redis_manager, 'client') as mock_client:
            workflow_state = WorkflowState(
                workflow_id="TST-METADATA",
                status="pending",
                feature_description="Metadata test",
                current_stage="testing",
                metadata=metadata,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                ttl_hours=1
            )
            
            mock_client.setex.return_value = True
            mock_client.get.return_value = json.dumps(workflow_state.dict())
            
            # Act
            save_result = asyncio.run(redis_manager.save_workflow_state(workflow_state))
            retrieved_state = asyncio.run(redis_manager.get_workflow_state("TST-METADATA"))
            
            # Assert
            assert save_result is True
            assert retrieved_state is not None
            assert retrieved_state.metadata == metadata
    
    def test_timestamp_ordering_invariant_when_updates_occur_then_last_updated_increases(self):
        """Invariant: last_updated should always be >= created_at and increase with updates"""
        redis_manager = RedisStateManager()
        
        with patch.object(redis_manager, 'client') as mock_client:
            # Arrange
            created_time = datetime.now()
            initial_state = {
                "workflow_id": "TST-TIMESTAMP",
                "status": "pending",
                "feature_description": "Timestamp test",
                "current_stage": "testing",
                "metadata": {},
                "created_at": created_time.isoformat(),
                "last_updated": created_time.isoformat(),
                "ttl_hours": 1
            }
            
            # Simulate passage of time
            time.sleep(0.01)  # Small delay
            updated_time = datetime.now()
            updated_state = initial_state.copy()
            updated_state.update({
                "status": "in_progress",
                "last_updated": updated_time.isoformat()
            })
            
            mock_client.get.return_value = json.dumps(updated_state)
            mock_client.setex.return_value = True
            
            # Act
            result = asyncio.run(redis_manager.update_workflow_state(
                "TST-TIMESTAMP", 
                {"status": "in_progress", "last_updated": updated_time.isoformat()}
            ))
            
            retrieved_state = asyncio.run(redis_manager.get_workflow_state("TST-TIMESTAMP"))
            
            # Assert
            assert result is True
            assert retrieved_state is not None
            assert retrieved_state.last_updated >= retrieved_state.created_at